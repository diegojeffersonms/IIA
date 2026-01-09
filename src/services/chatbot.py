import os
import base64
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama


ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")


class GraphState(dict):
    pass


class ChatBotService:
    def __init__(self):
        self.model_texto = ChatOllama(
            model="llama3",
            base_url=ollama_url,
            streaming=True
        )
        self.model_vision = ChatOllama(
            model="llava",
            base_url=ollama_url,
            streaming=True
        )

    def vision_node(self, state: GraphState):
        message = HumanMessage(
            content=[{
                "type": "text", "text": state['messages'][-1]['content'],
                "type": "image_url", "image_url": "data:image/png;base64," + base64.b64encode(state['image_bytes']).decode('utf-8'),
            }]
        )
        resp = self.model_vision.invoke([
            SystemMessage(content="""You are an Interior Design Assistant. 
    Your job is to describe everything that you can see at the image, your output will be used to provide targeted interior design suggestions."""),
            message
        ])

        return {
            "messages": state['messages'],
            "image_description": [resp],
        }

    def text_node(self, state: GraphState):
        messages = state["messages"]
        resp = self.model_texto.invoke([
            SystemMessage(content="""You are an Interior Design Assistant. 
    Your job is to give clear, practical and professional interior design advice. 
    When possible, structure the answer with bullet points or numbered steps. 
    If the user goal is to increase sale value, prioritize changes with high impact and reasonable cost.
    You must translate all answers to Portugal Portuguese."""),
            *messages
        ])

        return {"messages": [resp]}

    def improve_space_node(self, state: GraphState):
        messages = state["messages"]
        image_description = state["image_description"][-1].content

        resp = self.model_texto.invoke([
            SystemMessage(content="""You are an Interior Design Assistant.
    Your job is to improve the clarity and professionalism of interior design advice. 
    When possible, structure the answer with bullet points or numbered steps. 
    If the user goal is to increase sale value, prioritize changes with high impact and reasonable cost.
    You must translate all assistant answers to Portugal Portuguese."""),
            *messages,
            HumanMessage(content=f"The image description is: {image_description}."),
        ])

        return {"messages": [resp]}

    def router(self, state):
        if state.get('image_bytes'):
            return "vision"
        return "text"

    def build_graph(self):
        workflow = StateGraph(dict)
        workflow.add_node("vision_llm", self.vision_node)
        workflow.add_node("text_llm", self.text_node)
        workflow.add_node("improve_space_node", self.improve_space_node)
        workflow.set_conditional_entry_point(self.router, {"vision": "vision_llm", "text": "text_llm"})
        workflow.add_edge("vision_llm", "improve_space_node")
        workflow.add_edge("text_llm", END)
        workflow.add_edge("improve_space_node", END)
        self.graph_app = workflow.compile()

