import os
from dotenv import load_dotenv
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import START, END
from langgraph.graph.state import StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool
from langchain_core.messages import BaseMessage

load_dotenv()


os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGSMITH_API_KEY")
os.environ["LANGSMITH_TRACING"] = (
    "true"  # https://docs.smith.langchain.com/observability
)
os.environ["LANGSMITH_PROJECT"] = (
    "demoCrashCourse"  # https://docs.smith.langchain.com -> setup Project
)

# Initialize the model
llm = init_chat_model("groq:llama3-8b-8192")


class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


def make_tool_graph():
    # Graph with tools
    @tool
    def add(a: float, b: float):
        """Add two numbers"""
        return a + b

    @tool
    def explain(topic: str) -> str:
        """Explain a given topic in simple terms."""
        # You can use the LLM itself or a static response
        return f"{topic} is a broad concept in AI. (Add more details here.)"

    tools = [add, explain]
    llm_with_tool = llm.bind_tools(tools)

    # Node Definition
    def call_llm_model(state: State):
        return {"messages": [llm_with_tool.invoke(state["messages"])]}

    # Graph
    builder = StateGraph(State)
    builder.add_node("tool_calling_llm", call_llm_model)
    tool_node = ToolNode(tools)
    builder.add_node("tools", tool_node)

    # Add Edges
    builder.add_edge(START, "tool_calling_llm")
    builder.add_conditional_edges("tool_calling_llm", tools_condition)
    builder.add_edge("tools", "tool_calling_llm")

    # compile the graph
    graph = builder.compile()
    return graph


tool_agent = make_tool_graph()
