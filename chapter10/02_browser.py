from strands import Agent
from strands_tools.browser import AgentCoreBrowser

# ブラウザツールを初期化
browser = AgentCoreBrowser()

# エージェントを作成
agent = Agent(tools=[browser.browser])

# エージェントにウェブ操作を指示
response = agent(
    "https://aws.amazon.com/bedrock/agentcore/ にアクセスして、"
    "AgentCoreの主な機能を3つ教えてください。"
)
