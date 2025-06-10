from config.settings import Config
import logging
import util
import sub_manip as sm
import video_manip as vm
import censor as cn
from enums.LoggingColors import LoggingColors
if __name__ == "__main__":
    config = Config()
    logging.basicConfig(
        format=config.LOGGING_FORMAT,
        datefmt=config.LOGGING_DATE_FORMAT,
        level=logging.INFO,
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("ollama").setLevel(logging.WARNING)
    logging.getLogger("safetext").setLevel(logging.ERROR)
    util.print_welcome_message()
    media_folder_path = input("\nEnter the path to the media folder (will be searched recursively): ").strip()
    config.media_folder_path = media_folder_path

    util.get_censorship_strength()
    logging.info(f"{LoggingColors.BLUE_INFO}Selected censorship strength: {config.censorship_strength}{LoggingColors.RESET}")
    print()

    logging.info(f"{LoggingColors.BLUE_INFO}Looking for video and subtitle files{LoggingColors.RESET}")
    videos = vm.find_videos(config.media_folder_path)
    vm.create_video_to_id_mappings(videos)  # Create stable ID mappings for videos
    subtitles = sm.find_subtitles(config.media_folder_path)
    config.video_and_subtitle_files = sm.match_video_and_subtitles(videos, subtitles)
    logging.info(
        f"{LoggingColors.BLUE_INFO}Found {len(videos)} videos and {len(subtitles)} subtitles, matched {len(config.video_and_subtitle_files)} of them. {LoggingColors.RESET}")
    print()

    logging.info(f"{LoggingColors.BLUE_INFO}Proceeding to align subtitles with audio for precision.{LoggingColors.RESET}")
    logging.info(f"{LoggingColors.YELLOW_WARNING}Completed aligning subtitles with audio.{LoggingColors.RESET}")
    print()

    util.print_censorship_message()
    
    # resume censorship process
    config.init_or_resume_scenes_df()
    
    for video_id, subtitle_path in config.video_and_subtitle_files.items():
        logging.info(f"{LoggingColors.BLUE_INFO}Processing video ID {video_id} with subtitle: {subtitle_path.name}{LoggingColors.RESET}")
        cn.censor(video_id, subtitle_path)
    print("All done! Enjoy your media.")
