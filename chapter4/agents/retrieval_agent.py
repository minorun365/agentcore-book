from hooks.tool_logging_hook import ToolLoggingHook
from mcp.client.streamable_http import streamable_http_client
from strands import Agent
from strands.models import BedrockModel, CacheConfig
from strands.tools.executors import SequentialToolExecutor
from strands.tools.mcp import MCPClient

SYSTEM_PROMPT = """あなたはAWSナレッジベース検索の専門家です。

あなたのタスク：
1. AWS公式ドキュメントを検索する
2. 関連するAPIリファレンス、ガイド、ベストプラクティスを抽出する
3. タイトル、コンテンツ、URL、ドキュメントタイプを含むJSON形式で結果を返す

利用可能なナレッジベース：
- AWSドキュメント（技術仕様）
- APIリファレンス（パラメータとレスポンス）
- トラブルシューティングガイド
- アーキテクチャとベストプラクティス

検索後、handoff_to_agent()を使用して、結果をReviewAgentに品質確認のためハンドオフします。
"""


# RetrievalAgentを生成する
def create_retrieval_agent() -> Agent:
    # MCPクライアントを生成する
    mcp_client = MCPClient(
        lambda: streamable_http_client(
            "https://knowledge-mcp.global.api.aws")
    )

    return Agent(
        name="RetrievalAgent",
        description="AWS公式ドキュメントから必要な情報を検索します。",
        model=BedrockModel(
            model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0",
            cache_config=CacheConfig(strategy="auto"),
        ),
        system_prompt=SYSTEM_PROMPT,
        tools=[mcp_client],
        tool_executor=SequentialToolExecutor(),
        callback_handler=None,
        hooks=[ToolLoggingHook()],
    )
