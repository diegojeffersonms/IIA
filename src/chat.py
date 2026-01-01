from ollama import chat
import json
import os
from datetime import datetime

# ==============================
# CONFIG
# ==============================

# Modelos
TEXT_MODEL = "llama3.2:latest"             # rápido para conversa só texto (podes trocar por 'phi3' etc.)
IMAGE_MODEL = "interiorDesignAssistant2:latest"  # multimodal (modelo baseado em qwen3-vl criado via ollama create)

# Ficheiro de histórico
HISTORY_FILE = "chat_history.json"

# Few-shot (exemplos curtos para guiar o estilo)
FEW_SHOT = [
    {
        "role": "user",
        "content": "Tenho uma sala pequena e com pouca luz natural. O que posso fazer para parecer maior e mais luminosa?"
    },
    {
        "role": "assistant",
        "content": (
            "Sugestões práticas:\n"
            "1) Paredes em tons claros (branco quente, bege claro) para refletir luz.\n"
            "2) Espelhos (de preferência frente a uma janela) para ampliar visualmente.\n"
            "3) Iluminação por camadas: teto + candeeiros de apoio + fita LED indireta.\n"
            "4) Mobiliário leve/compacto e com pernas aparentes.\n"
            "5) Cortinas leves e claras (evitar tecidos pesados)."
        )
    },
    {
        "role": "user",
        "content": "Tenho uma sala pequena. O que recomendas?"
    },
    {
        "role": "assistant",
        "content": (
            "- Analisar iluminação\n"
            "- Sugerir cores claras\n"
            "- Propor mobiliário funcional"
        )
    },
    {
        "role": "user",
        "content": "Quero tornar a cozinha mais atrativa para venda. Dá recomendações rápidas."
    },
    {
        "role": "assistant",
        "content": (
            "Para aumentar o valor percebido na venda:\n"
            "- Paleta neutra e luminosa (branco, cinza claro, madeira clara).\n"
            "- Trocar puxadores e torneira por modelos modernos (acabamento inox/preto mate).\n"
            "- Iluminação LED (quente) sob armários + pendentes simples sobre a ilha.\n"
            "- Destralhar bancadas e criar 'home staging' (fruta, plantas, poucos objetos).\n"
            "- Se possível, atualizar eletrodomésticos para um conjunto coerente (inox)."
        )
    },
]

# STREAMING ???


def safe_image_path(path: str):
    if not path:
        return None
    path = path.strip().strip('"').strip("'")
    return path if os.path.exists(path) else None

def choose_model(has_image: bool) -> str:
    return IMAGE_MODEL if has_image else TEXT_MODEL

def save_history(last_model_used: str, messages: list) -> None:
    payload = {
        "timestamp": datetime.now().isoformat(),
        "models": {"text": TEXT_MODEL, "image": IMAGE_MODEL},
        "last_model_used": last_model_used,
        "messages": messages,
    }
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

def main():
    print("\n ######## Interior Designer Assistant ########\n")
    print("Hello! I am your Interior Designer Assistant.")
    print("Type 'exit' to quit.\n")

    messages = []
    
    last_model = TEXT_MODEL

    while True:
        user_input = input("You: ")

        if user_input.lower() in ['sair', 'exit', 'quit']:
            print("Interior Designer Assistant: Goodbye! Have a great day!")
            break
        
        img_in = input("\nIf you have an image to share, please provide the file path (or press Enter to skip): \n").strip()
        img_path = safe_image_path(img_in)

        user_message = {
            "role": "user",
            "content": user_input,
            "time": datetime.now().isoformat()
        }

        if img_path:
            user_message["images"] = [img_path]
        else:
            if img_in:
                print("\n Error: Image not found. Continuing with text only.")

        messages.append(user_message)

        current_model = choose_model(has_image=bool(img_path))
        last_model = current_model

        response = chat(
            model=current_model,
            messages=messages
        )

        reply = response["message"]["content"]
        print(f"\nIA:\n{reply}\n")
        messages.append({
            "role": "assistant",
            "content": reply,
            "time": datetime.now().isoformat(),
            "model_used": current_model
        })

    save_history(last_model_used=last_model, messages=messages)
    print("\nChat history saved to chat_history.json")



if __name__ == "__main__":
    main()