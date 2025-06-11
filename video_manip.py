import pathlib
from config.settings import Config
import sys
import subprocess
config = Config()
import logging
import pandas as pd
import math

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
    detection_exists = (config.temp_folder_path / f"{video_id}/scenes.csv").exists()
    if detection_exists:
        # read csv file and create df ignore first line, read columns from second line onwards
        current_scenes_df = pd.read_csv(config.temp_folder_path / f"{video_id}/scenes.csv", skiprows=1)
        # check if generated_images match the number of scenes
        should_not_split = math.isclose(len(current_scenes_df) * config.NUMBER_OF_IMAGES_PER_SCENE, len(list((config.temp_folder_path / f"{video_id}").glob("*.jpg"))), rel_tol=0.01)
        
    if should_not_split:
        logging.info(f"Scenes already split for video {video_id}, skipping...")
        # update our scenes_db just in case script has resumed after tampering. we are removing duplicates based on timestamp and video_id so its fine. 
        add_image_paths_and_scene_subs(video_id)
        return
    # log everything
    logging.info(f"Detection exists: {detection_exists}, should split: {should_not_split}")
    logging.info(f"Number of images in folder: {len(list((config.temp_folder_path / f'{video_id}').glob('*.jpg')))}")
    video_path = config.id_to_video[video_id]
    logging.info(f"Splitting video {video_path.name} into scenes...")
    
    command = [
        sys.executable, "-m", "scenedetect", 
        "--verbosity", "error",
        "--input", str(video_path),
        "list-scenes",
        "-f", f"{config.temp_folder_path}/{video_id}/scenes",
        "save-images",
        "--num-images", f"{config.NUMBER_OF_IMAGES_PER_SCENE}",
        "--filename", "$SCENE_NUMBER-$IMAGE_NUMBER-$TIMESTAMP_MS",
        "--output", f"{config.temp_folder_path}/{video_id}",
    ]

    load_scenes = [
        "load-scenes", "-i",
        f"{config.temp_folder_path}/{video_id}/scenes.csv"
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
    images = list((config.temp_folder_path / f"{video_id}").glob("*.jpg"))
    if not images:
        logging.warning(f"No images found in {config.temp_folder_path / video_id}. Skipping scene update.")
        return
    scene_images_db = pd.DataFrame(
            columns=["scene_number", "video_id", "scene_snapshot_number", "timestamp", "scene_snapshot_path"],
        ).astype({
                "timestamp": "float64",
                "scene_number": "int32",
                "video_id": "int32",
                "scene_snapshot_number": "int32",
                "scene_snapshot_path": "string"
            })
        
    for image in images:
        # extract timestamp from image filename
        scene_number, image_number, timestamp = map(int, image.stem.split('-'))

        # append to the DataFrame
        scene_images_db.loc[len(scene_images_db)] = [
            scene_number,
            video_id,
            image_number,
            timestamp,
            str(image)
        ]
        
    # concat the scenes_images_db with config.all_scenes_df
    config.all_scenes_df = pd.concat([config.all_scenes_df, scene_images_db], ignore_index=True)
    # re index the DataFrame, ascending order of timestamp_ms
    config.all_scenes_df.sort_values(by=["video_id", "timestamp"], inplace=True, ignore_index=True)
    # reset index
    config.all_scenes_df.reset_index(drop=True, inplace=True)
    # remove duplicates based on timestamp in case script was rerun
    config.all_scenes_df.drop_duplicates(subset=["timestamp", "video_id"], inplace=True)
    # update scene_number for subtitles, so wherever it is null, we fill it from the scene_number on the row above
    config.all_scenes_df['scene_number'] = config.all_scenes_df['scene_number'].fillna(method='ffill')
    # update scene_subtitles, wherever scene subtitles are not null, copy them onto the rows where scene number matches
    # get a dictionary of scene_number to scene_subtitle
    scene_subtitles = config.all_scenes_df[config.all_scenes_df['scene_subtitle'].notnull()][['scene_number', 'scene_subtitle']].set_index('scene_number').to_dict()['scene_subtitle']
    # update the scene_subtitle column with the values from the dictionary
    config.all_scenes_df['scene_subtitle'] = config.all_scenes_df['scene_number'].replace(scene_subtitles)
    # now simply fill all null scene_subtitles with the scene_subtitle from the row above
    config.all_scenes_df['scene_subtitle'] = config.all_scenes_df['scene_subtitle'].fillna(method='ffill')
    
    # log everything
    logging.info(f"Number of images in folder: {len(images)}")
    logging.info(f"Scene images database: {scene_images_db.head()}")
    logging.info(f"All scenes database: {config.all_scenes_df.head()}")
    
    # save all df as pickle files in the temp folder
    config.all_scenes_df.to_pickle(config.temp_folder_path / f"{video_id}/all_scenes_df.pkl")
    scene_images_db.to_pickle(config.temp_folder_path / f"{video_id}/scene_images_db.pkl")
