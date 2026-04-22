from strands import Agent
from strands.multiagent import Swarm

researcher = Agent(name="researcher",
    system_prompt="あなたは調査の専門家です。"
)
coder = Agent(name="coder",
    system_prompt="あなたはコーディングの専門家です。"
)
reviewer = Agent(name="reviewer",
    system_prompt="あなたはコードレビューの専門家です。"
)
architect = Agent(name="architect",
    system_prompt="あなたはシステム設計の専門家です。"
)

swarm = Swarm([coder, researcher, reviewer, architect])

result = swarm("TODOアプリ用のシンプルなREST APIを設計して実装してください")
