from mcp.server.fastmcp import FastMCP

mcp = FastMCP("MathServer")


@mcp.tool()
def add(a: int, b: int) -> int:
    """add two numbers"""
    return a + b


def multiple(a: int, b: int) -> int:
    """multiply two numbers"""
    return a * b


if __name__ == "__main__":
    # transport = 'stdio' argument tells the server to use the standard input and output (stdin/stdout) for communication.
    mcp.run(transport="stdio")  # or "http" for HTTP transport
