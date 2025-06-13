import pathlib
from config.settings import Config
from rapidfuzz import process, fuzz
import re
import logging
import subprocess
import pandas as pd
import pysrt
from enums.SceneCols import SceneCols
import profanity as pf
import sys
import subprocess
from tqdm import tqdm
from data.dataframe_manager import ScenesDataFrameManager

config = Config()
df_manager = ScenesDataFrameManager()
from safetext import SafeText


def save_snapshot(video_path, output_image, timestamp):
    """
    Extracts a frame from the video at a given timestamp and saves it as an image.
    :param video_path: Path to the video file
    :param output_image: Path to save the snapshot
    :param timestamp: Time (in HH:MM:SS format) to extract the frame
    """
    command = [
        "ffmpeg", "-ss", timestamp, "-i", video_path,
        "-frames:v", "1", "-q:v", "2", output_image, "-y"
    ]
    subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"Snapshot saved at {output_image}")


def custom_scorer(choice, query, **kwargs):
    """Prioritizes exact episode number matches while still considering overall similarity."""
    base_score = fuzz.ratio(choice, query)

    # Extract episode number (SxxExx) from the query and choice
    query_episode = re.search(r'S\d{2}E\d{2}', query)
    choice_episode = re.search(r'S\d{2}E\d{2}', choice)

    # If episode numbers match exactly, return a guaranteed high score
    if query_episode and choice_episode and query_episode.group() == choice_episode.group():
        return 100  # Ensure it gets the highest ranking

    return base_score  # Otherwise, return normal fuzzy match score

def find_subtitles(path):
    """
    Returns a sorted list of subtitle paths from the given folder path.
    Sorting ensures consistent order across runs.
    """
    return sorted(
        (sub for sub in pathlib.Path(path).rglob("*") if sub.suffix.lower() in config.SUBTITLE_EXTENSIONS),
        key=lambda p: str(p).lower()  # ensures case-insensitive sort
    )

def match_video_and_subtitles(videos, subtitles):
    """
    matches the video and subtitle files based on their names match percentage
    Expects: videos : list of video file pathlib paths
            subs : list of subtitle file pathlib paths
    """
    if not videos or not subtitles:
        logging.warning("No videos or subtitles found.")
        return {}

    subtitle_names = [sub.name for sub in subtitles]
    media_files = {}
    for video in videos:
        best_match, score, _ = process.extractOne(video.name, subtitle_names, scorer=custom_scorer)
        subtitle = next((s for s in subtitles if s.name == best_match), None)
        media_files[config.video_to_id[video]] = subtitle
        subtitle_names.remove(best_match)

    if len(media_files.keys()) != len(videos):
        logging.warning("Some videos do not have matching subtitles.")
    else:
        logging.info("All videos have matching subtitles.")
    return media_files


def align_subtitles(video_id, subtitle_path):
    """
    Aligns the subtitles with the video using ffsubsync.

    Args:
        video_path, subtitle_path (pathlib.Path): Paths to the video and subtitle files.
    Returns:
        None
    """
    video_path = config.id_to_video[video_id]
    # skip if already done
    if subtitle_path is None:
        logging.warning(f"No matching subtitle for video: {video_path.name}")
        return
    # Define output subtitle path (appends "_synced" before .srt)
    subtitle_synced_path = subtitle_path.with_stem(subtitle_path.stem + ".synced")

    # Check if the synced subtitle already exists
    if subtitle_synced_path.exists():
        logging.info(f"Synced subtitle already exists: {subtitle_synced_path.name}")
        config.video_and_subtitle_files[video_id] = subtitle_synced_path
        return
    
    command = [
        "ffsubsync", str(video_path),
        "-i", str(subtitle_path),
        "--vad", "webrtc",
        "-o", str(subtitle_synced_path)
    ]

    try:
        subprocess.run(command, check=True)
        # update dictionary with the new synced subtitle path
        config.video_and_subtitle_files[video_id] = subtitle_synced_path
    except subprocess.CalledProcessError as e:
        logging.error(
            f"Error aligning subtitles for {video_path.name}: {e}"
        )


def clean_subtitles(video_id, subtitle_path):
    """
    Processes the subtitles to extract relevant information.
    """
    # skip if already done
    if video_id in config.subtitles_processed_video_ids:
        logging.info("Skipping video %s subtitle processing as they have already been processed.", video_id)
        return
    
    st = SafeText(language="en")
    subs = pysrt.open(subtitle_path)

    try:
        for sub in tqdm(subs, desc="Cleaning subtitles", unit="sub"):
            profane = st.check_profanity(sub.text)

        df_manager.all_scenes_df.loc[len(df_manager.all_scenes_df)] = {
            str(SceneCols.TIMESTAMP): sub.start.ordinal,
            str(SceneCols.SUBTITLE_START_TIME): sub.start.ordinal,
            str(SceneCols.SUBTITLE_END_TIME): sub.end.ordinal,
            str(SceneCols.VIDEO_ID): video_id,
            str(SceneCols.SCENE_NUMBER): None,
            str(SceneCols.SCENE_SNAPSHOT_NUMBER): None,
            str(SceneCols.SCENE_SNAPSHOT_PATH): None,
            str(SceneCols.SUBTITLE): sub.text,
            str(SceneCols.CLEANED_SUBTITLE): pf.clean_text(sub.text) if profane else None,
            str(SceneCols.SNAPSHOT_DESC): None,
            str(SceneCols.PROFANITY_PRESENT): True if profane else False,
            str(SceneCols.NUDITY_PRESENT): None,
            str(SceneCols.SHOULD_CENSOR): None
        }


    except KeyboardInterrupt:
        print("\nKeyboard interrupt detected. Saving checkpoint before exiting...")
        config.save_checkpoint()
        raise  # re-raises the exception if you want the program to still exit with error

    # Optional: Save one last time at end if loop completes
    config.save_checkpoint()
