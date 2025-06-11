from config.settings import Config
from nudenet import NudeDetector
import logging
config = Config()

# Initialize once at module level
detector = NudeDetector(model_path="models/640m.onnx", inference_resolution=640)

def detect_nudity(image_path):
    results = detector.detect(image_path)
    
    # Filter out face detections
    results = [r for r in results if 'face' not in r['class'].lower()
               and 'armpit' not in r['class'].lower()
               and 'feet' not in r['class'].lower()
               and 'covered' not in r['class'].lower()
               ]
    print("Filtered detection results:", results)
    return len(results) > 0

def detect_nudity_in_video(video_id):
    """
    Detect nudity in the video and store results in the global DataFrame.
    :param video_path: Path to the video file.
    :return: None
    """

    rows = config.all_scenes_df[
        (config.all_scenes_df['video_id'] == video_id) &
        (config.all_scenes_df['scene_snapshot_path'].notnull()) & 
        (config.all_scenes_df['nudity_present'].isnull())
    ]

    if rows.empty:
        logging.info(f"Nudity detection already done for video {video_id} or no scenes to process.")
        return

    for idx, scene_image in zip(rows.index, rows.itertuples(index=False)):
        print(f"Processing scene {scene_image.scene_number} for video {video_id}: {scene_image.scene_snapshot_path}")
        nudity_present = detect_nudity(scene_image.scene_snapshot_path)
        config.all_scenes_df.at[idx, 'nudity_present'] = nudity_present
