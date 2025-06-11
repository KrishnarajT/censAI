import logging
import time
from tqdm import tqdm
import sub_manip as sm
import video_manip as vm
from config.settings import Config
import nudity as nd
import time
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
        "Detect Nudity in the Video",
        # "Generating description for each frame",
        # "Use description and nudenet results to determine if censoring is needed",
        # "Muting audio",
        # "Removing Scenes",
        # "Generating final video"
    ]
    
    video_path = config.id_to_video[video_id]
    logging.info("Starting the censorship process for : %s", video_path)


    total_start = time.perf_counter()  # Total timer

    # Initialize progress bar
    with tqdm(total=len(steps), desc="Processing", unit="step") as pbar:

        # Step 1 - Aligning Subtitles
        step_start = time.perf_counter()
        tqdm.write(steps[0])
        sm.align_subtitles(video_id, subtitle_path)
        tqdm.write(f"→ Done in {time.perf_counter() - step_start:.2f} sec")
        pbar.update(1)

        # Step 2 - Processing Subtitles
        step_start = time.perf_counter()
        tqdm.write(steps[1])
        sm.process_subtitles(video_id, subtitle_path)
        tqdm.write(f"→ Done in {time.perf_counter() - step_start:.2f} sec")
        pbar.update(1)

        # Step 3 - Splitting Scenes
        step_start = time.perf_counter()
        tqdm.write(steps[2])
        vm.split_into_scenes(video_id)
        tqdm.write(f"→ Done in {time.perf_counter() - step_start:.2f} sec")
        pbar.update(1)

        # Step 4 - Nudity Detection
        step_start = time.perf_counter()
        tqdm.write("Detecting potential Nudity in video. This may take a while... (around 7 mins per 1 hour of video)")
        nd.detect_nudity_in_video(video_id)
        tqdm.write(f"→ Done in {time.perf_counter() - step_start:.2f} sec")
        pbar.update(1)

        # Save data
        config.all_scenes_df.to_csv(config.temp_folder_path / "scenes.csv", index=False)
        config.all_scenes_df.to_pickle(config.temp_folder_path / "scenes.pkl")

    total_duration = time.perf_counter() - total_start
    tqdm.write(f"\n✅ All steps completed in {total_duration:.2f} seconds.")
        
    logging.info("Censorship process completed for : %s", video_path)
    logging.info("\n\n")