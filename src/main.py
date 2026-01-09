import os
import base64
import hyperdiv as hd
from services.chatbot import ChatBotService

class file_picker(hd.Plugin):
    _assets_root = os.path.join(os.path.dirname(__file__), "assets")
    _assets = ["file_picker.js"]

    image_metadata = hd.Prop(hd.Any, None)
    disabled = hd.Prop(hd.Bool, False)


initial_message = dict(role="assistant", content="Olá! Sou um assistente de design de interiores, estou aqui para ajudar-te a melhorar o seu espaço e aumentar o valor da sua propriedade.", id=0, gpt_model="")
chatbot_service = ChatBotService()
chatbot_service.build_graph()


def add_message(role, content, state, gpt_model):
    """
    Add a message to the state.

    Args:
        role (str): The role of the message (e.g., 'user', 'assistant').
        content (str): The content of the message.
        state (hd.state): The state object.
        gpt_model (str): The GPT model used for generating the message.
    """
    state.messages += (
        dict(role=role, content=content, id=state.message_id, gpt_model=gpt_model, img_data=state.img_data),
    )
    state.message_id += 1


def process_image_data(base64_string):
    """Convert format 'data:image/png;base64,iVBOR...' to raw bytes
    
    Args:
        base64_string (str): The base64 encoded image string.
    """

    if not base64_string:
        return None
    if ";base64," in base64_string:
        _, base64_data = base64_string.split(";base64,")
        return base64.b64decode(base64_data)
    return base64.b64decode(base64_string)


def request(state):
    """
    Send a request to the Ollama chatbot API.

    Args:
        state (hd.state): The state object.
    """

    img_bytes = process_image_data(state.img_data)

    models = set()
    for message_chunk, metadata in chatbot_service.graph_app.stream(
        {"messages": [dict(role=m["role"], content=m["content"]) for m in state.messages], "image_bytes": img_bytes},
        stream_mode="messages"
    ):
        node_name = metadata.get("langgraph_node")
        model_name = metadata.get("ls_model_name")
        models.add(model_name)

        if node_name == "vision_llm":
            continue

        if message_chunk.content:
            state.current_reply += message_chunk.content

    add_message("assistant", state.current_reply, state, ", ".join(models))
    state.current_reply = ""
    state.img_name = None
    state.img_data = None


def render_message(role, content, gpt_model = None, image_data = None):
    """
    Render a user message.

    Args:
        content (str): The content of the message.
        gpt_model (str): The GPT model used for generating the message.
    """
    if role == "user":
        with hd.hbox(
            align="center",
            padding=0.5,
            border_radius="medium",
            background_color="neutral-50",
            font_color="neutral-600",
            justify="space-between",
        ):
            with hd.vbox(gap=0.5):
                with hd.hbox(gap=0.5, align="center"):
                    hd.icon("chevron-right", shrink=0)
                    hd.text(content)

                if image_data:
                    with hd.hbox(padding_left=2):
                        hd.image(image_data, width=10)

            hd.badge("user", pill=True)
    else:
        with hd.hbox(
            align="center",
            padding=0.5,
            border_radius="medium",
            font_color="neutral-900",
            justify="space-between",
        ):
            hd.markdown(content)

            hd.badge(f"assistant {f'({gpt_model})' if gpt_model else ''}", pill=True, variant="success")

def main():
    """
    Main function to run the Ollama Chatbot.
    """
    state = hd.state(
        messages=(
            initial_message,
        ),
        current_reply="",
        gpt_model="",
        message_id=0,
        img_name=None,
        img_data=None,
    )

    task = hd.task()

    template = hd.template(title="Interior Design Chatbot", logo="/assets/uminho-eng.jpeg",sidebar=False)

    with template.body:
        if len(state.messages) > 0:
            with hd.box(direction="vertical-reverse", gap=1.5, vertical_scroll=True):
                if state.current_reply:
                    hd.markdown(state.current_reply)

                for e in reversed(state.messages):
                    with hd.scope(e["id"]):
                        if e["role"] == "system":
                            continue
                        if e["role"] == "user":
                            render_message(e["role"], e["content"], image_data=e["img_data"] if "img_data" in e else None)
                        else:
                            render_message(e["role"], e["content"], gpt_model=e["gpt_model"])

        with hd.box(align="center", gap=1.5):
            with hd.form(direction="horizontal", width="100%") as form:
                with hd.box(
                    padding_left=0.5,
                    direction="horizontal",
                    align="center",
                    border="1px solid #ccc",
                    border_radius="medium",
                    padding=(0, 0.5),
                    gap=0.5,
                    grow=1,
                ):
                    uploader = file_picker(disabled=task.running)
                    with hd.box(grow=1):
                        prompt = form.text_input(
                            placeholder="Converse com Interior Design Assistant...",
                            autofocus=True,
                            disabled=task.running,
                            name="prompt",
                        )
                    prompt_submit = form.submit_button("Enviar", disabled=task.running)
                    if uploader.image_metadata:
                        state.img_name = uploader.image_metadata['name']
                        state.img_data = uploader.image_metadata['content']

            if uploader.image_metadata:
                with hd.box(gap=1, border="1px solid #ddd", padding=1, border_radius="large"):
                    hd.text(f"Arquivo: {state.img_name}")

                    if state.img_data:
                        hd.image(state.img_data, width=15)

            if form.submitted:
                add_message("user", prompt.value, state, "user")
                prompt.reset()
                uploader.image_metadata = None
                task.rerun(request, state)

            if task.running:
                 with hd.box(font_size=4):
                    hd.spinner(
                        speed="5s",
                        track_width=0.5
                    )

            if len(state.messages) > 0 or state.img_name:
                if hd.button(
                    "Limpar Mensagens", size="small", variant="text", disabled=task.running
                ).clicked:
                    state.messages = (initial_message,)
                    state.img_name = None
                    state.img_data = None
                    uploader.image_metadata = None


index_page = hd.index_page(
    title="MIA - Interior Design Chatbot",
    description="Interior Design Chatbot powered by Hyperdiv and Ollama.",
    keywords=("hyperdiv", "python", "ollama", "chatbot", "interior design", "uminho"),
    favicon="/assets/uminho.png",
)

hd.run(main, index_page=index_page)