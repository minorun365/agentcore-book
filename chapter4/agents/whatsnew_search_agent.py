from hooks.tool_logging_hook import ToolLoggingHook
from strands import Agent
from strands.models import BedrockModel, CacheConfig
from strands_tools import current_time, rss

SYSTEM_PROMPT = """あなたはAWS最新ニュース検索の専門家です。

あなたのタスク：
1. AWS最新ニュースRSSフィード (https://aws.amazon.com/about-aws/whats-new/recent/feed/) から最新のニュース、更新情報、リリース情報を検索する
2. ユーザーのクエリに一致する関連エントリを抽出する
3. タイトル、コンテンツ、URL、日付、サービスを含むJSON形式で結果を返す

検索後、handoff_to_agent()を使用して、結果をReviewAgentに品質確認のためハンドオフします。
"""


# WhatsNewSearchAgentを生成する
def create_whatsnew_search_agent() -> Agent:
    return Agent(
        name="WhatsNewSearchAgent",
        description="AWS What's Newから最新ニュース、更新情報、リリース情報を検索します。",
        model=BedrockModel(
            model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0",
            cache_config=CacheConfig(strategy="auto"),
        ),
        system_prompt=SYSTEM_PROMPT,
        tools=[rss, current_time],
        callback_handler=None,
        hooks=[ToolLoggingHook()],
    )
