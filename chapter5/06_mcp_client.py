from strands import Agent
from strands.tools.mcp import MCPClient
from mcp_proxy_for_aws.client import aws_iam_streamablehttp_client

AGENT_ARN = "<MCPサーバーのランタイムARN>"

# ARNをエンコードしてURLを作成
encoded_arn = AGENT_ARN.replace(":", "%3A").replace("/", "%2F")
mcp_url = (f"https://bedrock-agentcore.us-east-1.amazonaws.com/runtimes/{encoded_arn}/invocations")

# MCPクライアントを作成
mcp_client = MCPClient(
    lambda: aws_iam_streamablehttp_client(
        endpoint=mcp_url,
        aws_service="bedrock-agentcore",
        terminate_on_close=False
    )
)

# StrandsでAIエージェントを作成して、呼び出し
agent = Agent(
   tools=mcp_client.list_tools_sync()
)
response = agent("3と5を足して")
