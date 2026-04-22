from strands import Agent
from strands_tools import http_request

# 子エージェント（リサーチ担当）を定義
research_agent = Agent(
    name="Research Assistant",
    system_prompt="リサーチを行う専門エージェントです。",
    tools=[http_request],
)

# 親エージェントに子エージェントを直接渡す
orchestrator = Agent(tools=[research_agent])
