import pathlib
from settings import Config
import logging

def find_videos(path):
    '''
    returns a list of videos from the given folder path
    '''    
    return []
    
def find_subtitles(path):
    '''
    returns a list of subtitles from the given folder path
    '''
    return []

def match_video_and_subtitles(videos, subs):
    '''
    matches the video and subtitle files based on their names match percentage
    '''
    return {}

def print_welcome_message():
    print("Welcome to CensAI!")
    print(
        """

    ░▒▓██████▓▒░░▒▓████████▓▒░▒▓███████▓▒░ ░▒▓███████▓▒░░▒▓██████▓▒░░▒▓█▓▒░ 
    ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░ 
    ░▒▓█▓▒░      ░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░ 
    ░▒▓█▓▒░      ░▒▓██████▓▒░ ░▒▓█▓▒░░▒▓█▓▒░░▒▓██████▓▒░░▒▓████████▓▒░▒▓█▓▒░ 
    ░▒▓█▓▒░      ░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░ 
    ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░ 
    ░▒▓██████▓▒░░▒▓████████▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓███████▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░ 

    Censorship Model for TV shows and Movies

    """
    )

def get_censorship_strength():
    config = Config()
    print("Enter censorship stren   gth (1 or 2):")
    print("1. Moderate - Only Explicit on screen exposed nudity is removed.  ")
    print(
        "2. Strict - Almost all on screen nudity is removed. If any story is present in said scenes, an AI generated summary is provided on a black screen later. Profane dialogues are muted and their subttiles replaced by AI generated sentences with similar meaning. "
    )

    choice = input("Enter your choice: ").strip()
    if choice not in ['1', '2']:
        print("Invalid choice. Please enter 1 or 2.")
        return get_censorship_strength()
    config.censorship_strength = 'MODERATE' if choice == '1' else 'STRICT'
