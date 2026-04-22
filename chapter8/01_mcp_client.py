from strands import Agent
from strands.tools.mcp import MCPClient
from mcp_proxy_for_aws.client import aws_iam_streamablehttp_client

# ゲートウェイにMCP接続するクライアントを作成
mcp_client = MCPClient(lambda: aws_iam_streamablehttp_client(
    endpoint="https://<ゲートウェイID>.gateway.bedrock-agentcore.us-east-1.amazonaws.com/mcp",
    aws_service="bedrock-agentcore"
))

# エージェントにツールとして渡して実行
agent = Agent(tools=[mcp_client])
agent("注文情報を検索してください")
