from strands import Agent
from strands.multiagent.a2a import A2AServer
from strands_tools.calculator import calculator

# 計算ツールを持つエージェントを作成
strands_agent = Agent(
    name="Calculator Agent",
    description="計算を行うエージェントです。",
    tools=[calculator],
)

# A2Aサーバーを作成
a2a_server = A2AServer(agent=strands_agent)

# A2Aサーバーを起動（デフォルトで9000番ポートを使用）
a2a_server.serve()
