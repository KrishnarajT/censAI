import logging
import time
from tqdm import tqdm
from data.dataframe_manager import ScenesDataFrameManager
import sub_manip as sm
import video_manip as vm
from config.settings import Config
import profanity as pf
import nudity as nd
import time
config = Config()
df_manager = ScenesDataFrameManager()
def censor(video_id, subtitle_path):
    """
    Censor the video based on the subtitle file.
    :param video_path: Path to the video file.
    :param subtitle_path: Path to the subtitle file.
    :return: None
    """

    steps = [
        "1. Aligning Subtitles",
        "2. Cleaning Subtitle File",
        "3. Splitting Video into Scenes",
        "4. Detecting potential Nudity in video",
        "5. Generating AI descriptions for each scene that has nudity",
        "6. Using All information to determine if scene should be censored by asking an LLM",
        "7. Muting audio",
        "8. Removing Scenes, Generating final video",
        "Final Stats and Cleanup"
    ]
    current_step = iter(range(len(steps)))
    video_path = config.id_to_video[video_id]
    logging.info("Starting the censorship process for : %s", video_path)


    total_start = time.perf_counter()  # Total timer

    # Initialize progress bar
    with tqdm(total=len(steps), desc="Processing", unit="step") as pbar:

        # Step 1 - Aligning Subtitles
        step_start = time.perf_counter()
        tqdm.write(steps[next(current_step)])
        sm.align_subtitles(video_id, subtitle_path)
        tqdm.write(f"→ Done in {time.perf_counter() - step_start:.2f} sec")
        pbar.update(1)
        config.save_checkpoint()

        # Step 2 - Processing Subtitles
        step_start = time.perf_counter()
        tqdm.write(steps[next(current_step)])
        sm.clean_subtitles(video_id, subtitle_path)
        tqdm.write(f"→ Done in {time.perf_counter() - step_start:.2f} sec")
        pbar.update(1)
        config.save_checkpoint()

        # Step 3 - Splitting Scenes
        step_start = time.perf_counter()
        tqdm.write(steps[next(current_step)])
        vm.split_into_scenes(video_id)
        tqdm.write(f"→ Done in {time.perf_counter() - step_start:.2f} sec")
        pbar.update(1)
        config.save_checkpoint()

        # Step 4 - Nudity Detection
        step_start = time.perf_counter()
        tqdm.write(steps[next(current_step)])
        nd.detect_nudity_in_video(video_id)
        tqdm.write(f"→ Done in {time.perf_counter() - step_start:.2f} sec")
        pbar.update(1)
        config.save_checkpoint()
        
        # Step 5 - Generate description for each scene that has nudity
        step_start = time.perf_counter()
        tqdm.write(steps[next(current_step)])
        nd.generate_descriptions_for_nude_scenes(video_id)
        tqdm.write(f"→ Done in {time.perf_counter() - step_start:.2f} sec")
        pbar.update(1)
        config.save_checkpoint()

        # Step 6 - Use description and nudenet results to determine if censoring is needed
        step_start = time.perf_counter()
        tqdm.write(steps[next(current_step)])
        pf.determine_if_should_censor_scene(video_id)
        tqdm.write(f"→ Done in {time.perf_counter() - step_start:.2f} sec")
        pbar.update(1)
        
        # Step 7 - Muting audio
        step_start = time.perf_counter()
        tqdm.write(steps[next(current_step)])
        vm.mute_audio(video_id)
        tqdm.write(f"→ Done in {time.perf_counter() - step_start:.2f} sec")
        pbar.update(1)
        
        # Step 8 - Remove scenes and generate final video
        step_start = time.perf_counter()
        tqdm.write(steps[next(current_step)])
        vm.remove_scenes_and_generate_final_video(video_id)
        tqdm.write(f"→ Done in {time.perf_counter() - step_start:.2f} sec")
        pbar.update(1)
        
        # Final Stats and Cleanup
        step_start = time.perf_counter()
        tqdm.write(steps[next(current_step)])
        df_manager.print_stats(video_id)
        config.cleanup_temp_folder(video_id)
        tqdm.write(f"→ Done in {time.perf_counter() - step_start:.2f} sec")
        
    total_duration = time.perf_counter() - total_start
    tqdm.write(f"\n✅ All steps completed in {total_duration:.2f} seconds.")
        
    logging.info("Censorship process completed for : %s", video_path)
    logging.info("\n\n")
