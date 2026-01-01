from ollama import chat
import json
import os

messages = []

print("\n ######## Interior Designer Assistant ########\n")
print("Hello! I am your Interior Designer Assistant.")
print("Type 'exit' to quit.\n")

while True:
    user_input = input("You: ")

    if user_input.lower() in ['sair', 'exit', 'quit']:
        print("Interior Designer Assistant: Goodbye! Have a great day!")
        break

    image_path = input(
        "\nIf you have an image to share, please provide the file path (or press Enter to skip): \n"
    ).strip()

    user_message = {
        "role": "user",
        "content": user_input
    }

    if image_path:
        if os.path.exists(image_path):
            user_message["images"] = [image_path]
        else:
            print("\n Error: Image not found. Continuing with text only.")

    messages.append(user_message)

    response = chat(
        model="assistenteIntDesigner",
        messages=messages
    )

    reply = response["message"]["content"]
    print(f"\nInterior Designer Assistant:\n{reply}\n")

    messages.append({
        "role": "assistant",
        "content": reply
    })

# Guardar histórico
with open("chat_history.json", "w", encoding="utf-8") as f:
    json.dump(messages, f, ensure_ascii=False, indent=4)

print("\nChat history saved to chat_history.json")
