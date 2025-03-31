import pathlib
from settings import Config

config = Config()


def find_videos(path):
    """
    returns a list of videos from the given folder path
    """
    return [video for video in pathlib.Path(path).rglob("*") if video.suffix.lower() in config.VIDEO_EXTENSIONS]
