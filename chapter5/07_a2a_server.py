from strands import Agent
from strands.multiagent.a2a import StrandsA2AExecutor
from strands_tools.calculator import calculator
from bedrock_agentcore.runtime import serve_a2a

# A2Aサーバーに載せたいエージェントを作成
agent = Agent(
    description="計算エージェント",
    tools=[calculator]
)

# A2Aサーバーを起動
serve_a2a(StrandsA2AExecutor(agent))
