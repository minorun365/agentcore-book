from mcp.server.fastmcp import FastMCP

# MCP SDKでサーバーを作成
mcp = FastMCP(
    host="0.0.0.0", stateless_http=True
)

# 提供したいツールを作成（例：足し算ツール）
@mcp.tool()
def add_numbers(a: int, b: int):
    return a + b

# MCPサーバーを起動
if __name__ == "__main__":
    mcp.run(transport="streamable-http")
