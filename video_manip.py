import pathlib
from config.settings import Config
import sys
import subprocess
config = Config()
import logging

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
    video_path = config.id_to_video[video_id]
    command = [
        sys.executable, "-m", "scenedetect", 
        "-i", str(video_path),
        "-o", str(config.temp_folder_path),
        "list-scenes",
        "-f", f"{video_id}_scenes",
        "save-images",
        "--num-images", "10"
        "--filename", "{video_id}_$SCENE_NUMBER_$IMAGE_NUMBER_$TIMESTAMP_MS"
    ]

    try:
        subprocess.run(command, check=True)
        # update dictionary with the new synced subtitle path
    except subprocess.CalledProcessError as e:
        logging.error(
            f"Error aligning subtitles for {video_path.name}: {e}"
        )
