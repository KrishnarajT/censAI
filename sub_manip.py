import pathlib
from settings import Config
from rapidfuzz import process, fuzz
import re
import logging
import subprocess

config = Config()


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
    returns a list of subtitles from the given folder path
    """
    return [sub for sub in pathlib.Path(path).rglob("*") if sub.suffix.lower() in config.SUBTITLE_EXTENSIONS]


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
        media_files[video] = subtitle
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
            continue

        # Construct ffsubsync command
        command = [
            "ffsubsync", str(video_path),
            "-i", str(subtitle_path),
            "--vad", "webrtc",  # Uses WebRTC Voice Activity Detection for better sync
            "-o", str(subtitle_synced_path)
        ]

        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            logging.error(
                f"Error aligning subtitles for {video_path.name}: {e}"
            )
