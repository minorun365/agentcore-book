from strands import Agent, tool
from strands_evals import Experiment, Case
from strands_evals.telemetry import StrandsEvalsTelemetry
from bedrock_agentcore.evaluation import create_strands_evaluator

@tool
def calculator(expression: str) -> str:
    """数式を計算する"""
    return str(eval(expression))

agent = Agent(tools=[calculator])

# トレースをメモリに出力するよう設定
telemetry = StrandsEvalsTelemetry().setup_in_memory_exporter()

# エージェントを実行し、記録されたトレースデータを取得する
def task_fn(case):
    response = agent(case.input)
    spans = list(telemetry.in_memory_exporter.get_finished_spans())
    return {"output": str(response), "trajectory": spans}

# テストケースを定義
cases = [Case(input="5 + 3 はいくつですか？", expected_output="8")]

# 組み込みエバリュエーター（Helpfulness）を指定
evaluator = create_strands_evaluator("Builtin.Helpfulness")

# 評価を実行
experiment = Experiment(cases=cases, evaluators=[evaluator])
reports = experiment.run_evaluations(task_fn)

print(f"スコア: {reports[0].overall_score:.2f}")
