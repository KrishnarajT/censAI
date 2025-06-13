from config.settings import Config
from nudenet import NudeDetector
import logging
from tqdm import tqdm
import time

config = Config()

# Initialize once at module level
detector = NudeDetector(model_path="models/640m.onnx", inference_resolution=640)

def detect_nudity(image_path):
    results = detector.detect(image_path)
    
    # Filter out face detections
    results = [r for r in results if 'face' not in r['class'].lower()
            #    and 'armpit' not in r['class'].lower()
               and 'feet' not in r['class'].lower()
            #    and 'covered' not in r['class'].lower()
               ]
    # print("Filtered detection results:", results)
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
      
    try:
        for idx, scene_image in tqdm(
            zip(rows.index, rows.itertuples(index=False)),
            total=len(rows),
            desc=f"Checking nudity in {video_id}",
            unit=" scene frames"
        ):
            nudity_present = detect_nudity(scene_image.scene_snapshot_path)
            config.all_scenes_df.at[idx, 'nudity_present'] = nudity_present
            # time.sleep(0.05)  # Light 50ms breather
    except KeyboardInterrupt:
        logging.warning("KeyboardInterrupt caught — saving checkpoint before exiting...")
        config.save_checkpoint()
        raise  # Re-raise to allow upstream handling or proper exit

    else:
        # If the loop completes without interruption
        logging.info(f"Finished nudity detection for video {video_id}. Saving checkpoint...")
        config.save_checkpoint()

# Load model directly
from transformers import AutoProcessor, AutoModelForCausalLM
from PIL import Image
import torch
logging.info("Loading Florence-2-large model...")
model_id = "microsoft/Florence-2-large"
processor = AutoProcessor.from_pretrained(model_id, trust_remote_code=True)
# model = AutoModelForCausalLM.from_pretrained("microsoft/Florence-2-large", trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(model_id, trust_remote_code=True).to("cuda")  # Move model to CUDA

def generate_detailed_caption(image_path, task_prompt="<MORE_DETAILED_CAPTION>"):
    # Load and preprocess the image
    image = Image.open(image_path).convert("RGB")

    # Tokenize & Encode
    inputs = processor(text=task_prompt, images=image, return_tensors="pt")
    
    # 🔥 Move **ALL** tensors to CUDA
    inputs = {key: value.to("cuda") for key, value in inputs.items()}

    # Generate Caption with Beam Search
    with torch.no_grad():
        generated_ids = model.generate(
            input_ids=inputs["input_ids"],
            pixel_values=inputs["pixel_values"],
            max_new_tokens=1024,  # Allow longer captions
            early_stopping=False,
            do_sample=False,  # No randomness
            num_beams=3,  # Beam search for better results
        )

    # Decode Output
    generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]

    # Post-process (Ensure Processing Happens on CUDA)
    parsed_answer = processor.post_process_generation(
        generated_text,
        task=task_prompt,
        image_size=image.size
    )

    return parsed_answer

def generate_descriptions_for_nude_scenes(video_id):
    """
    Generate detailed descriptions for each scene that has nudity.
    :param video_id: ID of the video to process.
    :return: None
    """

    rows = config.all_scenes_df[
        (config.all_scenes_df['video_id'] == video_id) &
        (config.all_scenes_df['nudity_present'] == True) &
        (config.all_scenes_df['snapshot_desc'].isnull())
    ]
    
    # remove duplicate scene_numbers from this
    # rows = rows.drop_duplicates(subset=['scene_number'])

    if rows.empty:
        logging.info(f"No nude scenes to process for video {video_id}.")
        return

    try:
        for idx, scene_image in tqdm(zip(rows.index, rows.itertuples(index=False)),
                                    total=len(rows), 
                                    desc=f"Generating descriptions for {video_id}", 
                                    unit=" scene frames"):
            description = generate_detailed_caption(scene_image.scene_snapshot_path)
            config.all_scenes_df.at[idx, 'snapshot_desc'] = description['<MORE_DETAILED_CAPTION>']
    except KeyboardInterrupt:
        print("\nInterrupted! Saving checkpoint...")
        config.save_checkpoint()
        print("Checkpoint saved. Exiting gracefully.")
