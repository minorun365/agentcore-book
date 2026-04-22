from strands import Agent
from strands_evals import Case, Experiment
from strands_evals.evaluators import OutputEvaluator

def get_response(case: Case) -> str:
    agent = Agent(callback_handler=None)
    return str(agent(case.input))

test_cases = [
    Case[str, str](
        name="knowledge-test",
        input="フランスの首都はどこですか？",
        expected_output="パリ",
    ),
]

evaluator = OutputEvaluator(
    rubric="正確性と完全性を評価してください。",
)

experiment = Experiment[str, str](
    cases=test_cases, evaluators=[evaluator]
)
reports = experiment.run_evaluations(get_response)
print(reports[0].to_dict())
