import pandas as pd

from enums.SceneCols import SceneCols
from enums.SceneImageCols import SceneImageCols
from config.settings import Config

class ScenesDataFrameManager:
    _instance = None  # Singleton instance
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, "_initialized"):  # Prevent re-initialization in Singleton
            self.all_scenes_df = pd.DataFrame()        
            self.scene_images_df = pd.DataFrame()
            self.config = Config()
            self._initialized = True
            self.load_checkpoint()

    def init_scene_images_df(self):
        """
        Initializes the scene images DataFrame with the appropriate columns.
        """
        # clean up if already initialized
        if not self.scene_images_df.empty:
            self.scene_images_df = pd.DataFrame()
        self.scene_images_df = pd.DataFrame(
            columns=[col.name_str for col in SceneImageCols],
        ).astype({col.name_str: col.dtype for col in SceneImageCols})
        
        # print("Initialized scene images DataFrame.")

    def save_checkpoint(self):
        self.all_scenes_df.to_csv(self.config._temp_folder_path / "scenes.csv", index=False)
        self.all_scenes_df.to_pickle(self.config._temp_folder_path / "scenes.pkl")
        
    def load_checkpoint(self):
        if self.config._temp_folder_path.exists() and (self.config._temp_folder_path / "scenes.pkl").exists():
            # Load existing DataFrame from pickle
            self.all_scenes_df = pd.read_pickle(self.config._temp_folder_path / "scenes.pkl")
            print("Loaded scenes DataFrame from existing file.")
        else:
            # Initialize a new DataFrame
            self.all_scenes_df = pd.DataFrame(
                columns=[col.name_str for col in SceneCols],
            ).astype({col.name_str: col.dtype for col in SceneCols})
            print("Initialized new scenes DataFrame.")
        
    def print_stats(self, video_id: int):
        """
        Prints statistics about the scenes for a given video ID.
        :param video_id: ID of the video to print stats for.
        """
        if self.all_scenes_df.empty:
            print("No scenes to display.")
            return
        
        # print how many scenes we censored (from should_censor)
        # print how many subtitles we changed (from profanity_present)
        # print total how much time we cut
        censored_scenes = self.all_scenes_df[self.all_scenes_df['should_censor'] == True & (self.all_scenes_df['video_id'] == video_id)]
        changed_subtitles = self.all_scenes_df[self.all_scenes_df['profanity_present'] == True & (self.all_scenes_df['video_id'] == video_id)]
        
        # to find how much time cut, we have to find the timestamp of the first frame (row) from censored_scenes, and the timestamp of the last frame from that scene, and so on for all censored scenes
        total_time_cut = 0
        censored_scenes_list = censored_scenes['scene_number'].unique().tolist()
        for scene_number in censored_scenes_list:
            scene_df = censored_scenes[censored_scenes['scene_number'] == scene_number]
            if not scene_df.empty:
                start_time = scene_df['timestamp'].min()
                end_time = scene_df['timestamp'].max()
                total_time_cut += (end_time - start_time) / 1000

        print(f"Total Time Cut: {total_time_cut} seconds")
        
        print(f"Total Scenes in Video: {len(self.all_scenes_df[self.all_scenes_df['video_id'] == video_id])}")
        print(f"Total Scenes with Subtitles: {len(self.all_scenes_df[self.all_scenes_df['scene_subtitles'].notnull() & (self.all_scenes_df['video_id'] == video_id)])}")
        print(f"Total Censored Scenes: {len(censored_scenes)}")
        print(f"Total Changed Subtitles: {len(changed_subtitles)}")