from strands import Agent, tool
from strands.tools.executors import SequentialToolExecutor


@tool
def get_weather(location: str):
    """locationの天気を取得

    Args:
        location: 都市名
    """
    return f"{location}の天気は晴れで、気温は25℃です。"


agent = Agent(
    tools=[get_weather],
    tool_executor=SequentialToolExecutor(),  # 順次実行方式
)
