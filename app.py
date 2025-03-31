from settings import Config
import logging
import util
import sub_manip as sm
import video_manip as vm

if __name__ == "__main__":
    config = Config()
    logging.basicConfig(
        format=config.LOGGING_FORMAT,
        datefmt=config.LOGGING_DATE_FORMAT,
        level=logging.INFO,
    )

    util.print_welcome_message()
    media_folder_path = input("\nEnter the path to the media folder: ").strip()
    config.media_folder_path = media_folder_path

    logging.info("Looking for video and subtitle files")
    videos = vm.find_videos(config.media_folder_path)
    subtitles = sm.find_subtitles(config.media_folder_path)
    config.video_and_subtitle_files = sm.match_video_and_subtitles(videos, subtitles)
    logging.info(
        f"Found {len(videos)} videos and {len(subtitles)} subtitles, matched {len(config.video_and_subtitle_files)} of them. ")

    util.get_censorship_strength()
    logging.info(f"Selected censorship strength: {config.censorship_strength}")

    logging.info("Proceeding to align subtitles with audio for precision.")
    sm.align_subtitles(config.video_and_subtitle_files)
    logging.info("Completed aligning subtitles with audio.")

    logging.info("\n")


