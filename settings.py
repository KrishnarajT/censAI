import pathlib

class Config:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._media_folder_path = pathlib.Path()
            cls._instance._censorship_strength = None
            cls._instance.video_and_srt_files = {}
        return cls._instance
    
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
        self._censorship_strength = strength
        
    @property
    def video_and_srt_files(self):
        return self._video_and_srt_files
    
    @video_and_srt_files.setter
    def video_and_srt_files(self, files):
        self._video_and_srt_files  = files

    @property
    def LOGGING_FORMAT(self):
        return "%(asctime)s [%(levelname)s] %(message)s"
    
    @property
    def LOGGING_DATE_FORMAT(self):
        return "%H:%M:%S"