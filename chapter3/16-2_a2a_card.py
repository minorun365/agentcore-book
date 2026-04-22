import asyncio

from strands.agent.a2a_agent import A2AAgent


async def main():
    a2a_agent = A2AAgent(endpoint="http://localhost:9000")
    card = await a2a_agent.get_agent_card()
    print(f"Agent: {card.name}")
    print(f"Description: {card.description}")
    print(f"Skills: {card.skills}")


asyncio.run(main())
