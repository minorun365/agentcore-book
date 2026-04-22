from strands import Agent
from strands.hooks import BeforeToolCallEvent
from strands_tools import http_request

agent = Agent(
    tools=[http_request],
)


# Tool実行前に呼び出されるCallback関数
def before_tool_call_callback(event: BeforeToolCallEvent):
    if event.tool_use["name"] == "http_request":
        # パラメーターをチェックし、ツール実行をキャンセルする
        url: str = event.tool_use["input"]["url"]
        if not url.startswith("https://docs.aws.amazon.com/"):
            event.cancel_tool = "AWSドキュメント以外へのアクセスは禁止です。"


# フックをagentに追加
agent.hooks.add_callback(BeforeToolCallEvent, before_tool_call_callback)
agent("https://aws.amazon.com/jp/new/から最新情報を取得して")
