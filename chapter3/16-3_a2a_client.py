import asyncio

from strands import Agent
from strands_tools.a2a_client import A2AClientToolProvider

# A2Aツール群を初期化
provider = A2AClientToolProvider(known_agent_urls=["http://localhost:9000"])

# リモートエージェントを利用できる親エージェントを作成
agent = Agent(tools=provider.tools)


async def main():
    result = await agent.invoke_async(
        "利用可能なエージェントを選び、12 x 34を計算して。"
    )
    print(result.message["content"][-1]["text"])


asyncio.run(main())
