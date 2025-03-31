import pathlib
from enums.CensorshipStrength import CensorshipStrength
import pandas as pd


class Config:
    _instance = None  # Singleton instance

    # Constants
    LOGGING_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"
    LOGGING_DATE_FORMAT = "%H:%M:%S"
    VIDEO_EXTENSIONS = [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv"]
    SUBTITLE_EXTENSIONS = [".srt", ".ass", ".vtt", ".sub", ".idx"]

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "_initialized"):  # Prevent re-initialization in Singleton
            self._media_folder_path = pathlib.Path()
            self._censorship_strength = None
            self._video_and_subtitle_files = {}
            self._initialized = True
            self._temp_path = None
            self._scenes_df = pd.DataFrame(
                columns=["timestamp", "scene_number", "scene_snapshot_number", "scene_snapshot_path", "subtitle",
                         "cleaned_subtitle", "snapshot_desc", "profanity_present", "nudity_present", "should_censor"],
            ).astype({
                "timestamp": "float64",
                "scene_number": "int32",
                "scene_snapshot_number": "int32",
                "scene_snapshot_path": "string",
                "subtitle": "string",
                "cleaned_subtitle": "string",
                "snapshot_desc": "string",
                "profanity_present": "bool",
                "nudity_present": "bool",
                "should_censor": "bool"
            })

    @property
    def media_folder_path(self):
        return self._media_folder_path

    @media_folder_path.setter
    def media_folder_path(self, path):
        if not isinstance(path, str):
            raise ValueError("Path must be a string.")
        path = pathlib.Path(path)
        if not path.exists() or not path.is_dir():
            raise ValueError("The path does not exist or is not a directory.")
        self._media_folder_path = path
        self._temp_path = path / "temp"
    @property
    def censorship_strength(self):
        return self._censorship_strength

    @censorship_strength.setter
    def censorship_strength(self, strength):
        if strength is not None and not isinstance(strength, CensorshipStrength):
            raise ValueError("Censorship strength must be a CensorshipStrength.py Enum value.")
        self._censorship_strength = strength

    @property
    def video_and_subtitle_files(self):
        return self._video_and_subtitle_files

    @video_and_subtitle_files.setter
    def video_and_subtitle_files(self, files):
        if not isinstance(files, dict):
            raise ValueError("Video and subtitle files must be a dictionary.")
        self._video_and_subtitle_files = files

    @property
    def scenes_df(self):
        return self._scenes_df

    @scenes_df.setter
    def scenes_df(self, df):
        if not isinstance(df, pd.DataFrame):
            raise ValueError("Scenes DataFrame must be a pandas DataFrame.")
        self._scenes_df = df

    @property
    def temp_path(self):
        return self._temp_path

    @temp_path.setter
    def temp_path(self, path):
        if not isinstance(path, pathlib.Path):
            raise ValueError("Path must be a pathlib.Path object.")
        self._temp_path = path