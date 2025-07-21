from mcp.server.fastmcp import FastMCP

mcp = FastMCP("WeatherServer")


@mcp.tool()
def get_weather(location: str) -> str:
    """Get the weather for the location"""
    return f"The weather in the location is sunny."


if __name__ == "__main__":

    mcp.run(transport="streamable-http")  # or "http" for HTTP transport
