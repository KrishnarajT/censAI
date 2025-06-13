import pathlib
from enums.CensorshipStrength import CensorshipStrength
import pandas as pd

from enums.SceneCols import SceneCols


class Config:
    _instance = None  # Singleton instance

    # Constants
    LOGGING_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"
    LOGGING_DATE_FORMAT = "%H:%M:%S"
    VIDEO_EXTENSIONS = [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv"]
    SUBTITLE_EXTENSIONS = [".srt", ".ass", ".vtt", ".sub", ".idx"]
    NUMBER_OF_IMAGES_PER_SCENE = 7
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "_initialized"):  # Prevent re-initialization in Singleton
            self._initialized = True
            # these need care while being set
            self._media_folder_path = pathlib.Path()
            self._temp_folder_path = None
            self._censorship_strength = None
            self.muted_audio_root_path = None  # Path to the muted audio file
            self.video_and_subtitle_files = {}
            self.subtitles_processed_video_ids = []  # Track the last processed video ID

            self.video_to_id = {}
            self.id_to_video = {}

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
        self._temp_folder_path = path / "temp"
        self.muted_audio_root_path = self._temp_folder_path / "muted_audio"
        
        # create directory temp if it does not exist
        if not self._temp_folder_path.exists():
            self._temp_folder_path.mkdir(parents=True, exist_ok=True)
    
    @property
    def temp_path(self):
        return self._temp_folder_path

    @temp_path.setter
    def temp_path(self, path):
        if not isinstance(path, pathlib.Path):
            raise ValueError("Path must be a pathlib.Path object.")
        self._temp_folder_path = path

    @property
    def censorship_strength(self):
        return self._censorship_strength

    @censorship_strength.setter
    def censorship_strength(self, strength):
        if strength is not None and not isinstance(strength, CensorshipStrength):
            raise ValueError("Censorship strength must be a CensorshipStrength.py Enum value.")
        self._censorship_strength = strength

    def cleanup_temp_folder(self, video_id):
        temp_folder = self._temp_folder_path / str(video_id)
        if temp_folder.exists() and temp_folder.is_dir():
            for item in temp_folder.iterdir():
                if item.is_file():
                    item.unlink()
            temp_folder.rmdir()