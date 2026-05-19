from mcp import stdio_client, StdioServerParameters
from strands import Agent
from strands.tools.mcp import MCPClient

mcp_client = MCPClient(
    lambda: stdio_client(
        StdioServerParameters(
            command="uvx",
            args=["--with", "boto3[crt]==1.42.96", "awslabs.bedrock-kb-retrieval-mcp-server@latest"],
            env={
                "AWS_REGION": "us-east-1",
                "FASTMCP_LOG_LEVEL": "ERROR",
            },
        )
    )
)

agent = Agent(
    tools=[mcp_client],
    system_prompt="社内規定を参照して正確に回答してください。"
)
agent("出張時の宿泊費の上限を教えて")
