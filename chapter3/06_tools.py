from mcp.client.streamable_http import streamable_http_client
from strands import Agent, tool
from strands.tools.mcp import MCPClient
from strands_tools.tavily import tavily_search


@tool
def get_weather(location: str):
    """locationの天気を取得

    Args:
        location: 都市名
    """
    return f"{location}の天気は晴れで、気温は25℃です。"


agent = Agent(tools=[get_weather])
agent("東京の天気を教えて")

# 事前に環境変数 TAVILY_API_KEY に APIキーを設定しておく
agent = Agent(tools=[tavily_search])
agent("Strands Agentsの公式ドキュメントを検索して、MCPの概要を要約して")

mcp_client = MCPClient(
    lambda: streamable_http_client("https://knowledge-mcp.global.api.aws")
)

agent = Agent(tools=[mcp_client])
agent(
    "AWSの最新ドキュメントを参照して、AgentCore EvaluationsとBedrock Evaluationsの違いを教えて"
)
