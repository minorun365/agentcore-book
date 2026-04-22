from strands import Agent
from strands.agent.conversation_manager import SlidingWindowConversationManager

agent = Agent(
    conversation_manager=SlidingWindowConversationManager(
        window_size=10,  # 保持するメッセージの数。デフォルトは40
    ),
)
