import pathlib
from enums.CensorshipStrength import CensorshipStrength

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
