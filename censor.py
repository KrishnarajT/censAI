import logging
import time
from tqdm import tqdm
import sub_manip as sm
from config.settings import Config
config = Config()

def censor(video_id, subtitle_path):
    """
    Censor the video based on the subtitle file.
    :param video_path: Path to the video file.
    :param subtitle_path: Path to the subtitle file.
    :return: None
    """

    # steps = [
    #     "Analysing Subtitle file",
    #     "Splitting Each scene to get frames",
    #     "Run nudenet on each frame",
    #     "Generating description for each frame",
    #     "Use description and nudenet results to determine if censoring is needed",
    #     "Muting audio",
    #     "Removing Scenes",
    #     "Generating final video"
    # ]

    # skip if already done
    if video_id in config.processed_video_ids:
        logging.info("Skipping video %s as it has already been processed.", video_id)
        return
    
    video_path = config.id_to_video[video_id]
    logging.info("Starting the censorship process for : %s", video_path)

    # Initialize progress bar
    with tqdm(total=10, desc="Processing", unit="step") as pbar:

        # step 1 - processing subs
        tqdm.write(f"[INFO] Processing Subtitle File")  # Print step description
        pbar.update(1)
        sm.process_subtitles(video_path, subtitle_path)
        #! write df to csv # debug
        config.scenes_df.to_csv(config.temp_folder_path / "scenes.csv", index=False)
        # write to pickle file
        config.scenes_df.to_pickle(config.temp_folder_path / "scenes.pkl")

        # step 2 - splitting scenes
        
        
        
    logging.info("Censorship process completed for : %s", video_path)