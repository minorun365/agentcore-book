from strands import Agent
from strands.models import BedrockModel
from strands_tools import calculator, current_time

model = BedrockModel(
    model_id="us.anthropic.claude-sonnet-4-6",
    region_name="us-east-1",
)

# AIエージェントを作成
agent = Agent(
    model=model,
    system_prompt="あなたは計算エージェントです。時刻の確認には current_time を、計算には calculator を必ず使ってください。時刻の確認の際は現地のタイムゾーンを意識すること。",
    tools=[calculator, current_time],
)

# AIエージェントを呼び出し
agent("現在の日時を基準に、今年が終わるまでの残り秒数を求めてください。")
