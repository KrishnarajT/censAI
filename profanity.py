import ollama

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