import asyncio

from strands import Agent


async def streaming():
    agent = Agent(
        # コールバックハンドラーを使ったストリーミングは無効化
        callback_handler=None,
    )
    agent_stream = agent.stream_async("こんにちは")
    async for event in agent_stream:
        if "message" in event:
            message = event["message"]  # メッセージ
        if "result" in event:
            result = event["result"]  # 最終回答
        if "data" in event:
            data = event["data"]  # トークン単位のテキスト
            print(data, end="")  # トークン単位でコンソール出力


asyncio.run(streaming())
