from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq

from dotenv import load_dotenv
import os
import asyncio

load_dotenv()


async def main():
    client = MultiServerMCPClient(
        {
            "MathServer": {
                "command": "python",
                "args": ["mathServer.py"],
                "transport": "stdio",
            },
            "WeatherServer": {
                "url": "http://127.0.0.1:8000/mcp",
                "transport": "streamable_http",
            },
        }
    )

    groq_api_key = os.getenv("GROQ_API_KEY")
    if groq_api_key is not None:
        os.environ["GROQ_API_KEY"] = groq_api_key
    else:
        raise EnvironmentError("GROQ_API_KEY environment variable is not set.")

    tools = await client.get_tools()
    model = ChatGroq(model="llama-3.1-8b-instant")
    agent = create_react_agent(model, tools)

    math_response = agent.invoke(
        {"messages": [{"role": "user", "content": "what is (3 + 5) * 12 ?"}]}
    )
    print("Math Response: ", math_response["messages"][-1].content)

    math_response = agent.invoke(
        {"messages": [{"role": "user", "content": "what is Weather in California?"}]}
    )
    print("Weather Response: ", math_response["messages"][-1].content)


asyncio.run(main())
