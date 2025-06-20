import ollama
from config.settings import Config

import logging

from data.dataframe_manager import ScenesDataFrameManager

config = Config()
df_manager = ScenesDataFrameManager()

def clean_text(text):
    prompt = f"""Return only the sanitized text. Remove all profanity while preserving the original meaning. If a single word is profane, replace it with a more appropriate alternative. For text with sexual implications, rewrite it in a kid-friendly manner. Do not provide explanations or advice. Only output the modified text. Give only 1 sentence

    Here are some examples of how to sanitize text:  

    Input: "Fuck!"  
    Output: "Shit!" 

    Input: "This is fucking stupid!"  
    Output: "This is freaking stupid!" 

    Input: "Fuck you!"  
    Output: "Screw you!"  

    Input: "This is so fucked!"  
    Output: "This is a total mess!"  

    Input: "Men think with their dicks?"  
    Output: "Men often prioritize materialistic things?"  

    Input: "She was sniffing my ass!"  
    Output: "She was very close to me last night!"  

    Input: "I wanna fuck you so badly"  
    Output: "I want us to be close." 
    
    Input: "I can still see her breasts moving"
    Output: "I can still see her moving"

    Input: "Have you never boned a woman's ass before jon snow?"  
    Output: "Have you never been close to a woman before, Jon Snow?" 


    Now, sanitize the following text while preserving its meaning: 

    : '{text}'"""
    response = ollama.chat(
        model="mistral", messages=[{"role": "user", "content": prompt}]
    )
    return response["message"]["content"]


def determine_if_should_censor_scene(image_descriptions: list, subtitles: list, nudity_present: bool):
    prompt = f"""You are given raw descriptions of frames from a scene in a TV show, along with some subtitles.

        These were generated using other AI models to help describe the visual and dialogue content.

        Your task is to evaluate whether this scene is likely to contain:
        - nudity or sexually suggestive content,
        - sexually intimate settings or themes,
        - visual or dialogue content that could be considered inappropriate or unnecessary for viewers avoiding such material.

        Do NOT explain your reasoning. Do NOT output anything except a single word: `true` or `false`.

        Respond `true` if **any line in the input** suggests this could possibly be a scene involving the above.

        ---

        [START OF INPUT]

        Frame Descriptions:
        {', '.join(image_descriptions)}

        Subtitles:
        {', '.join(subtitles)}

        Meta:
        Another model (NudeNet) this scene to {'' if nudity_present else 'NOT'} contain nudity, though it can be inaccurate.

        [END OF INPUT]

        Final Answer:
    : '{text}'"""
    response = ollama.chat(
        model="mistral", messages=[{"role": "user", "content": prompt}]
    )
    return response["message"]["content"]

def determine_if_should_censor_video(video_id: int):
    """
    Determines if the video should be censored based on its scenes.
    :param video_id: ID of the video to process.
    :return: True if the video should be censored, False otherwise.
    """
    rows = df_manager.all_scenes_df[
        df_manager.all_scenes_df['video_id'] == video_id &
        df_manager.all_scenes_df['nudity_present'] == True &
        df_manager.all_scenes_df['should_censor'].isnull()
    ]

    if rows.empty:
        logging.info(f"No scenes to process for video {video_id}.")
        return False
    
    try:
        for idx, row in rows.iterrows():
            image_descriptions = row['snapshot_desc'].split(', ')
            subtitles = row['scene_subtitles'].split(', ')
            media_name = config.media_name
            nudity_present = row['nudity_present']
            
            should_censor = determine_if_should_censor_scene(
                image_descriptions, subtitles, media_name, nudity_present
            )
            
            df_manager.all_scenes_df.at[idx, 'should_censor'] = should_censor
            
    except KeyboardInterrupt:
        print("\nInterrupted! Saving checkpoint...")
        config.save_checkpoint()
    logging.info(f"Completed processing for video {video_id}.")