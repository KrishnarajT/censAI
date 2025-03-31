import pathlib
from settings import Config
from rapidfuzz import process, fuzz
import re
import logging

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


def find_videos(path):
    """
    returns a list of videos from the given folder path
    """
    return [video for video in pathlib.Path(path).rglob("*") if video.suffix.lower() in config.VIDEO_EXTENSIONS]


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

    subtitles = [sub.name for sub in subtitles]
    videos = [video.name for video in videos]
    media_files = {}
    for video in videos:
        best_match, score, _ = process.extractOne(video, subtitles, scorer=custom_scorer)
        media_files[video] = best_match
        subtitles.remove(best_match)

    if len(media_files.keys()) != len(videos):
        logging.warning("Some videos do not have matching subtitles.")
    else:
        logging.info("All videos have matching subtitles.")

    return media_files
