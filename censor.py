import logging
import time
from tqdm import tqdm
import sub_manip as sm
import video_manip as vm
from config.settings import Config
config = Config()

def censor(video_id, subtitle_path):
    """
    Censor the video based on the subtitle file.
    :param video_path: Path to the video file.
    :param subtitle_path: Path to the subtitle file.
    :return: None
    """

    steps = [
        "Aligning Subtitles",
        "Processing Subtitle File",
        "Splitting Video into Scenes",
        # "Analysing Subtitle file",
        # "Splitting Each scene to get frames",
        # "Run nudenet on each frame",
        # "Generating description for each frame",
        # "Use description and nudenet results to determine if censoring is needed",
        # "Muting audio",
        # "Removing Scenes",
        # "Generating final video"
    ]
    
    video_path = config.id_to_video[video_id]
    logging.info("Starting the censorship process for : %s", video_path)

    # Initialize progress bar
    with tqdm(total=len(steps), desc="Processing", unit="step") as pbar:

        # step 1 - Aligning Subtitles
        tqdm.write(steps[0])
        pbar.update(1)
        sm.align_subtitles(video_id, subtitle_path)

        # step 2 - processing subs
        tqdm.write(steps[1])
        pbar.update(1)
        sm.process_subtitles(video_id, subtitle_path)
        
        # step 3 - splitting scenes
        tqdm.write(steps[2])
        vm.split_into_scenes(video_id)
        pbar.update(1)
        
        #! write df to csv # debug
        config.all_scenes_df.to_csv(config.temp_folder_path / "scenes.csv", index=False)
        # write to pickle file
        config.all_scenes_df.to_pickle(config.temp_folder_path / "scenes.pkl")
        
        
    logging.info("Censorship process completed for : %s", video_path)