import logging
import time
from tqdm import tqdm
import sub_manip as sm
from settings import Config
config = Config()

def censor(video_path, subtitle_path):
    """
    Censor the video based on the subtitle file.
    :param video_path: Path to the video file.
    :param subtitle_path: Path to the subtitle file.
    :return: None
    """

    # steps = [
    #     "Analysing Subtitle file",
    #     "Splitting Each scene to get frames",
    #     "Generating description for each frame",
    #     "Censoring subtitles",
    #     "Muting audio",
    #     "Removing Scenes",
    #     "Generating final video"
    # ]

    logging.info("Starting the censorship process for : %s", video_path)

    # Initialize progress bar
    with tqdm(total=10, desc="Processing", unit="step") as pbar:

        # step 1 - processing subs
        tqdm.write(f"[INFO] Processing Subtitle File")  # Print step description
        pbar.update(1)
        sm.process_subtitles(video_path, subtitle_path)
        # write df to csv
        config.scenes_df.to_csv(config.media_folder_path / "scenes.csv", index=False)

    logging.info("Censorship process completed for : %s", video_path)