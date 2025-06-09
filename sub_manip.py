import pathlib
from config.settings import Config
from rapidfuzz import process, fuzz
import re
import logging
import subprocess
import pandas as pd
import pysrt
import profanity as pf
import sys
import subprocess

config = Config()
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


def align_subtitles(video_and_subtitle_files):
    """
    Aligns the subtitles with the video using ffsubsync.

    Args:
        video_and_subtitle_files : dict of video path as keys and subtitle path as values
    """

    for video_path, subtitle_path in video_and_subtitle_files.items():
        if subtitle_path is None:
            logging.warning(f"No matching subtitle for video: {video_path.name}")
            continue

        # Define output subtitle path (appends "_synced" before .srt)
        subtitle_synced_path = subtitle_path.with_stem(subtitle_path.stem + ".synced")

        # Check if the synced subtitle already exists
        if subtitle_synced_path.exists():
            logging.info(f"Synced subtitle already exists: {subtitle_synced_path.name}")
            video_and_subtitle_files[video_path] = subtitle_synced_path
            continue

        # Construct ffsubsync command
        # we use sys.executable to ensure the correct Python environment is used that has ffsubsync installed
        command = [
            sys.executable, "-m", "ffsubsync", str(video_path),
            "-i", str(subtitle_path),
            "--vad", "webrtc",
            "-o", str(subtitle_synced_path)
        ]

        try:
            subprocess.run(command, check=True)
            # update dictionary with the new synced subtitle path
            video_and_subtitle_files[video_path] = subtitle_synced_path
        except subprocess.CalledProcessError as e:
            logging.error(
                f"Error aligning subtitles for {video_path.name}: {e}"
            )


def process_subtitles(video_path, subtitle_path):
    """
    Processes the subtitles to extract relevant information.
    """
    st = SafeText(language="en")
    subs = pysrt.open(subtitle_path)

    for sub in subs:
        profane = True if st.check_profanity(sub.text) else False
        config.scenes_df.loc[len(config.scenes_df)] = [sub.start.ordinal, 
                                                       config.video_to_id[video_path],
                                                       None,
                                                       None,
                                                       None,
                                                       sub.text,
                                                       pf.clean_text(sub.text) if profane else None,
                                                       None,
                                                       profane,
                                                       False,
                                                       False]
