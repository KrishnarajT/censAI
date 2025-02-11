import ollama

with open("./test/ep1.srt", "r", encoding="utf-8") as file:
    file_content = file.read()

response = ollama.chat(
    model="llama3.2",  # Replace with your model
    messages=[{"role": "user", "content": file_content + "\n\ncan you return the same script but without any gore "}]
)

print(response['message']['content'])
