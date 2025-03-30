from settings import Config
import logging
import util


def menu_system():
    print("Enter censorship strength (1 or 2):")
    print("1. Moderate - Only Explicit on screen exposed nudity is removed.  ")
    print(
        "2. Strict - Almost all on screen nudity is removed. If any story is present in said scenes, an AI generated summary is provided on a black screen later. Profane dialogues are muted and their subttiles replaced by AI generated sentences with similar meaning. "
    )

    choice = input("Enter your choice: ").strip()


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

    menu_system()
