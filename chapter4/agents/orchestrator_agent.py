from agents.plan_agent import create_plan_agent
from agents.retrieval_agent import create_retrieval_agent
from agents.review_agent import create_review_agent
from agents.whatsnew_search_agent import create_whatsnew_search_agent
from hooks.tool_logging_hook import ToolLoggingHook
from rich import print
from rich.panel import Panel
from strands import Agent, tool
from strands.models import BedrockModel, CacheConfig
from strands.multiagent import Swarm, SwarmResult
from strands_tools import current_time

now = current_time.current_time("Asia/Tokyo")

SYSTEM_PROMPT = f"""あなたは複数のソースから情報を統合するリサーチディレクターです。
現在日時は{now}です。

あなたのタスク：
1. ユーザーの質問を受け取る
2. execute_swarm_searchツールを呼び出して、複数のナレッジソースを検索する
3. 見つけた情報をもとに、Markdownを生成する
4. ソース参照とリンクを含める

見出し、箇条書き、および適切な出典を含む明確なMarkdown形式で出力します。
"""


# マルチエージェントSwarmを用いて情報収集を行うツール
@tool
async def execute_swarm_search(query: str) -> str:
    """複数のソースからマルチエージェントSwarmを使用して情報収集を行います。"""

    plan = create_plan_agent()  # PlanAgent
    whatsnew_search = create_whatsnew_search_agent()  # WhatsNewSearchAgent
    retrieval = create_retrieval_agent()  # RetrievalAgent
    review = create_review_agent()  # ReviewAgent

    swarm = Swarm(
        [plan, retrieval, whatsnew_search, review],
        entry_point=plan,
    )  # 4つのエージェントでSwarmを生成

    multiagent_result: SwarmResult = None

    async for event in swarm.stream_async(query):
        if event.get("type") == "multiagent_node_start":
            # マルチエージェント内の一つのエージェントの開始イベント
            node_id = event.get("node_id")
            print(f"[bold yellow]multiagent_node_start: {node_id}")

        elif event.get("type") == "multiagent_handoff":
            # エージェントの判断により別のエージェントへ処理の制御が移動したイベント
            message = event.get("message")
            from_node_ids = event.get("from_node_ids")
            to_node_ids = event.get("to_node_ids")
            print(
                Panel(
                    message,
                    title=f"Hand off {from_node_ids} -> {to_node_ids}",
                    title_align="left",
                )
            )

        elif event.get("type") == "multiagent_node_stop":
            # マルチエージェント内の一つのエージェントの終了イベント
            node_id = event.get("node_id")
            print(f"[bold yellow]multiagent_node_stop: {node_id}")

        elif event.get("type") == "multiagent_result":
            # マルチエージェントの最終回答を生成したイベント
            multiagent_result = event.get("result")

    # 最後に実行していたエージェントのノードIDを取得
    final_node_id = multiagent_result.node_history[-1].node_id
    # 最後に実行していたエージェントのresultを取得
    final_result = multiagent_result.results[final_node_id]

    return final_result.result.message


# OrchestratorAgentを生成する
def create_orchestrator_agent() -> Agent:
    return Agent(
        name="OrchestratorAgent",
        description="複数のソースから情報収集を行い、Markdownレポートを生成",
        system_prompt=SYSTEM_PROMPT,
        model=BedrockModel(
            model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0",
            cache_config=CacheConfig(strategy="auto"),
            additional_request_fields={
                "tool_choice": {
                    "disable_parallel_tool_use": True,
                }
            },
        ),
        tools=[execute_swarm_search],
        callback_handler=None,
        hooks=[ToolLoggingHook()],
    )
