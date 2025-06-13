import pathlib
from config.settings import Config
import sys
import subprocess
from enums import SceneCols, SceneImageCols
import logging
import pandas as pd
import math
from data.dataframe_manager import ScenesDataFrameManager

import subprocess
import logging


config = Config()
df_manager = ScenesDataFrameManager()
def find_videos(path):
    """
    Returns a sorted list of video paths from the given folder path.
    Sorting ensures consistent order across runs.
    """
    return sorted(
        (video for video in pathlib.Path(path).rglob("*") if video.suffix.lower() in config.VIDEO_EXTENSIONS),
        key=lambda p: str(p).lower()  # case-insensitive path sort
    )

def create_video_to_id_mappings(video_list):
    """
    updates config.video_to_id and config.id_to_video dictionaries
    to keep stable ID mappings consistent across runs.
    Expects: video_list : list of video file pathlib paths
    """
    # Build dictionaries for path <-> id mappings
    config.video_to_id = {}
    config.id_to_video = {}

    for idx, video_path in enumerate(video_list, start=1):
        config.video_to_id[video_path] = idx
        config.id_to_video[idx] = video_path

def split_into_scenes(video_id):
    """
    Splits the video into scenes using scene_detect library.
    """
    
    # skip if already done
    # done by reading the scenes.csv file in the temp / video_id folder if it exists. 
    # convert that csv file to a df, if no. of rows * NUMBER_OF_IMAGES_PER_SCENE is equal to the number of images in the folder, then skip
    current_scenes_df = pd.DataFrame()
    should_not_split = False
    detection_exists = (config._temp_folder_path / f"{video_id}/scenes.csv").exists()
    if detection_exists:
        # read csv file and create df ignore first line, read columns from second line onwards
        current_scenes_df = pd.read_csv(config._temp_folder_path / f"{video_id}/scenes.csv", skiprows=1)
        # check if generated_images match the number of scenes
        should_not_split = math.isclose(len(current_scenes_df) * config.NUMBER_OF_IMAGES_PER_SCENE, len(list((config._temp_folder_path / f"{video_id}").glob("*.jpg"))), rel_tol=0.01)
        
    if should_not_split:
        logging.info(f"Scenes already split for video {video_id}, skipping...")
        # update our scenes_db just in case script has resumed after tampering. we are removing duplicates based on timestamp and video_id so its fine. 
        add_image_paths_and_scene_subs(video_id)
        return
    # log everything
    logging.info(f"Detection exists: {detection_exists}, should split: {should_not_split}")
    logging.info(f"Number of images in folder: {len(list((config._temp_folder_path / f'{video_id}').glob('*.jpg')))}")
    video_path = config.id_to_video[video_id]
    logging.info(f"Splitting video {video_path.name} into scenes...")
    
    command = [
        sys.executable, "-m", "scenedetect", 
        "--verbosity", "error",
        "--input", str(video_path),
        "list-scenes",
        "-f", f"{config._temp_folder_path}/{video_id}/scenes",
        "save-images",
        "--num-images", f"{config.NUMBER_OF_IMAGES_PER_SCENE}",
        "--filename", "$SCENE_NUMBER-$IMAGE_NUMBER-$TIMESTAMP_MS",
        "--output", f"{config._temp_folder_path}/{video_id}",
    ]

    load_scenes = [
        "load-scenes", "-i",
        f"{config._temp_folder_path}/{video_id}/scenes.csv"
    ]
    
    # join if detection_exists is True
    if detection_exists:
        command.extend(load_scenes)
    
    try:
        subprocess.run(command, check=True)
        add_image_paths_and_scene_subs(video_id)
    except subprocess.CalledProcessError as e:
        logging.error(
            f"Error splitting scenes for {video_path.name}: {e}"
        )

def add_image_paths_and_scene_subs(video_id):
    # by this time we should have the video scenes csv and its images. 
    # read the folder and get all jpg files into a list. 
    images = list((config._temp_folder_path / f"{video_id}").glob("*.jpg"))
    if not images:
        logging.warning(f"No images found in {config._temp_folder_path / video_id}. Skipping scene update.")
        return
    df_manager.init_scene_images_df()
    for image in images:
        # extract timestamp from image filename
        scene_number, image_number, timestamp = map(int, image.stem.split('-'))

        # append to the DataFrame
        df_manager.scene_images_df.loc[len(df_manager.scene_images_df)] = [
            scene_number,
            video_id,
            image_number,
            timestamp,
            str(image)
        ]
        
    # concat the scenes_images_db with df_manager.all_scenes_df
    df_manager.all_scenes_df = pd.concat([df_manager.all_scenes_df, df_manager.scene_images_df], ignore_index=True)
    # re index the DataFrame, ascending order of timestamp_ms
    df_manager.all_scenes_df.sort_values(by=["video_id", "timestamp"], inplace=True, ignore_index=True)
    # reset index
    df_manager.all_scenes_df.reset_index(drop=True, inplace=True)
    # remove duplicates based on timestamp in case script was rerun
    df_manager.all_scenes_df.drop_duplicates(subset=["timestamp", "video_id"], inplace=True)
    # update scene_number for subtitles, so wherever it is null, we fill it from the scene_number on the row above
    df_manager.all_scenes_df['scene_number'] = df_manager.all_scenes_df['scene_number'].ffill()
    
    # log everything
    logging.info(f"Number of images in folder: {len(images)}")
    logging.info(f"Scene images database: {df_manager.scene_images_df.head()}")
    logging.info(f"All scenes database: {df_manager.all_scenes_df.head()}")
    
    # save all df as pickle files in the temp folder
    df_manager.all_scenes_df.to_pickle(config._temp_folder_path / f"{video_id}/all_scenes_df.pkl")
    df_manager.scene_images_df.to_pickle(config._temp_folder_path / f"{video_id}/scene_images_db.pkl")

def mute_audio(video_id):
    """
    Mutes specific portions of audio in a video based on profanity timestamps using ffmpeg.
    """
    video_path = config.id_to_video[video_id]
    output_path = config.muted_audio_root_path / video_path.name

    # Filter profane rows
    profane_audio_timestamps = df_manager.all_scenes_df[
        (df_manager.all_scenes_df['profanity_present'] == True) &
        (df_manager.all_scenes_df['video_id'] == video_id)
    ]

    if profane_audio_timestamps.empty:
        logging.info(f"No profane audio timestamps found for video {video_id}. Skipping audio muting.")
        return

    # Get subtitle start and end times in seconds
    intervals = list(zip(
        profane_audio_timestamps[SceneCols.SUBTITLE_START_TIME.value[0]] / 1000.0,
        profane_audio_timestamps[SceneCols.SUBTITLE_END_TIME.value[0]] / 1000.0
    ))

    # Generate FFmpeg volume filter expression
    # aeval: 'volume=enable='between(t,start,end)+between(t,...)...':volume=0'
    volume_expr = "+".join([f"between(t,{start},{end})" for start, end in intervals])
    volume_filter = f"volume=enable='{volume_expr}':volume=0"

    command = [
        "ffmpeg", "-i", str(video_path),
        "-af", volume_filter,
        "-c:v", "copy",  # Copy video stream without re-encoding
        str(output_path)
    ]

    try:
        subprocess.run(command, check=True)
        logging.info(f"Muted profane segments for {video_path.name}. Output saved to {output_path}.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error muting audio for {video_path.name}: {e}")

def remove_scenes_and_generate_final_video(video_id):
    """
    Removes scenes based on the DataFrame and generates a final video without those scenes.
    """
    video_path = config.id_to_video[video_id]
    input_path = config.muted_audio_root_path / video_path.name
    output_path = config.media_folder_path / f"censored_{video_path.name}"
    # Filter out scenes that should not be censored
    scenes_to_remove = df_manager.all_scenes_df[
        (df_manager.all_scenes_df['should_censor'] == True) &
        (df_manager.all_scenes_df['video_id'] == video_id)
    ]

    if scenes_to_remove.empty:
        logging.info(f"No scenes to remove for video {video_id}. Generating final video without changes.")
        # Just copy the original video if no scenes to remove
        subprocess.run(["cp", str(input_path), output_path], check=True)   
        return

    # Generate FFmpeg filter expression to remove specified scenes
    filter_expr = ""
    for _, row in scenes_to_remove.iterrows():
        start_time = row[SceneCols.SUBTITLE_START_TIME.value[0]] / 1000.0  # Convert ms to seconds
        end_time = row[SceneCols.SUBTITLE_END_TIME.value[0]] / 1000.0  # Convert ms to seconds
        filter_expr += f"between(t,{start_time},{end_time})+"
    
    # Remove trailing '+' and wrap in 'not' to keep only non-censored parts
    filter_expr = f"not({filter_expr[:-1]})"

    command = [
        "ffmpeg", "-i", str(input_path),
        "-vf", f"select='{filter_expr}'",
        "-c:v", "copy", "-c:a", "aac",  # Copy video, encode audio
        str(output_path)
    ]

    try:
        subprocess.run(command, check=True)
        logging.info(f"Final video generated at {output_path}.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error generating final video for {video_path.name}: {e}")