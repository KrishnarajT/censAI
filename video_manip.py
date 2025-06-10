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
        return
    # log everything
    logging.info(f"Detection exists: {detection_exists}, should split: {should_not_split}")
    logging.info(f"Current scenes dataframe: {current_scenes_df.head()}")
    logging.info(f"Length of current scenes dataframe: {len(current_scenes_df)}")
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
        
        # current_scenes_df = pd.read_csv(config.temp_folder_path / f"{video_id}/scenes.csv", skiprows=1) if not detection_exists else current_scenes_df
        
        # # by this time we should have the video scenes csv and its images. 
        
        # # read the folder and get all jpg files into a list. 
        # images = list((config.temp_folder_path / f"{video_id}").glob("*.jpg"))
        # scene_images_db = pd.DataFrame(
        #     columns=["scene_number", "image_number", "timestamp", "image_path"],
        #     dtype="string"
        # )
        
        # for image in images:
        #     # extract timestamp from image filename
        #     scene_number, image_number, timestamp = image.stem.split('-')
        #     # append to the DataFrame
        #     scene_images_db.loc[len(scene_images_db)] = [
        #         scene_number, 
        #         image_number, 
        #         timestamp, 
        #         str(image)
        #     ]
        
        # # merge the config.all_scenes_df with scene_images_db on scene_number
        # config.all_scenes_df = pd.merge(
        #     config.all_scenes_df,
        #     scene_images_db,
        #     how="full",
        #     left_on="timestamp",
        #     right_on="timestamp"
        # )
        
        # # concat the scenes_images_db with config.all_scenes_df
        # config.all_scenes_df = pd.concat([config.all_scenes_df, scene_images_db], ignore_index=True)
        # # re index the DataFrame, ascending order of timestamp_ms
        # config.all_scenes_df.sort_values(by="timestamp", inplace=True, ignore_index=True)
        # # reset index
        # config.all_scenes_df.reset_index(drop=True, inplace=True)

    except subprocess.CalledProcessError as e:
        logging.error(
            f"Error splitting scenes for {video_path.name}: {e}"
        )
