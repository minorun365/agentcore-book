from strands import Agent
from strands_tools import http_request

agent = Agent(
    # モデル
    model="us.anthropic.claude-sonnet-4-6",
    # プロンプト
    system_prompt="あなたは優秀なアシスタントです。ツールを使って回答してください。",
    # ツール
    tools=[http_request],
)
