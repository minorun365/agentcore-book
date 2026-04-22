from hooks.tool_logging_hook import ToolLoggingHook
from strands import Agent
from strands.models import BedrockModel, CacheConfig

SYSTEM_PROMPT = """あなたは情報品質レビュアーです。

あなたのタスク：
1. 複数のソース（AWSドキュメント、最新ニュース）からの検索結果をレビューする
2. 情報の完全性をスコアリングする（0-100）
3. スコアが70以上の場合：レビューを終了し、統合されたレスポンスを提供する
4. スコアが70未満の場合：情報ギャップを特定し、handoff_to_agent()を使用してPlanAgentに追加の検索戦略のためハンドオフする

レビュー基準：
- 情報の鮮度
- 信頼性（公式 > 非公式）
- 完全性（質問のすべての側面に答える）
- ソースの多様性

追加情報が必要な場合は、handoff_to_agent()を使用して、不足している情報の詳細をPlanAgentにハンドオフします。
"""


# ReviewAgentを生成する
def create_review_agent() -> Agent:
    return Agent(
        name="ReviewAgent",
        description="情報の完全性をレビューし必要に応じて追加検索をリクエスト",
        model=BedrockModel(
            model_id="us.anthropic.claude-sonnet-4-6",
            cache_config=CacheConfig(strategy="auto"),
        ),
        system_prompt=SYSTEM_PROMPT,
        callback_handler=None,
        hooks=[ToolLoggingHook()],
    )
