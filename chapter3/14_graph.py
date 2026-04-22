from strands import Agent
from strands.multiagent import GraphBuilder
from strands.multiagent.base import Status
from strands.multiagent.graph import GraphState

# ノードとなるエージェントを作成
researcher = Agent(system_prompt="あなたの役割はリサーチです。", callback_handler=None)
analyst = Agent(system_prompt="あなたの役割は分析です。", callback_handler=None)
fact_checker = Agent(
    system_prompt="あなたの役割はファクトチェックです。", callback_handler=None
)
decision_maker = Agent(
    system_prompt="分析結果とファクトチェックからOKかNGを返答してください。",
    callback_handler=None,
)
report_writer = Agent(
    system_prompt="あなたの役割はレポート作成です。", callback_handler=None
)

# グラフビルダーを作成
builder = GraphBuilder()

# 実行タイムアウトを600秒に指定
builder.set_execution_timeout(600)


# 指定したノードがすべて完了したかを判定
def all_dependencies_complete(required_nodes: list[str]):
    def check_all_complete(state: GraphState) -> bool:
        return all(
            node_id in state.results
            and state.results[node_id].status == Status.COMPLETED
            for node_id in required_nodes
        )

    return check_all_complete


# decisionノードの結果がOKかを判定
def is_ok(state: GraphState) -> bool:
    return "OK" in str(state.results["decision"].result)


# decisionノードの結果がNGかを判定
def is_ng(state: GraphState) -> bool:
    return "NG" in str(state.results["decision"].result)


# ノードを追加
builder.add_node(researcher, "research")
builder.add_node(analyst, "analysis")
builder.add_node(fact_checker, "fact_check")
builder.add_node(decision_maker, "decision")
builder.add_node(report_writer, "report")

# エッジを追加
builder.add_edge("research", "analysis")
builder.add_edge("research", "fact_check")
builder.add_edge("analysis", "decision",
    condition=all_dependencies_complete(["analysis", "fact_check"])
)
builder.add_edge("fact_check", "decision",
    condition=all_dependencies_complete(["analysis", "fact_check"])
)
builder.add_edge("decision", "report", condition=is_ok)
builder.add_edge("decision", "research", condition=is_ng)

# エントリーポイントを指定
builder.set_entry_point("research")

# グラフエージェントを作成
graph = builder.build()


# グラフエージェントを呼び出し
result = graph(
    "「2026年の日本のスタートアップ業界の成長トレンド」について最新の情報を調査して。"
)

report_result = result.results["report"].result  # 結果を取得
print(report_result)
