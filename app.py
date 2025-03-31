from settings import Config
import logging
import util


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
    vids = util.find_videos(config.media_folder_path)
    subs = util.find_subtitles(config.media_folder_path)
    config.video_and_srt_files = util.match_video_and_subtitles(vids, subs)
    logging.info(f"Found {len(config.video_and_srt_files)} videos")
    
    util.get_censorship_strength()
    logging.info(f"Selected censorship strength: {config.censorship_strength}")
    
    