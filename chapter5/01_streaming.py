from strands import Agent
from bedrock_agentcore import BedrockAgentCoreApp

# AIエージェントとAPIサーバーを作成
agent = Agent()
app = BedrockAgentCoreApp()

# APIサーバーのエントリーポイントを設定
@app.entrypoint
async def invoke(payload, context):
   # プロンプトを取り出してAIエージェントを呼び出し
   prompt = payload.get("prompt")
   stream = agent.stream_async(prompt)

   # ストリーミングレスポンスを逐次返却
   async for event in stream:
       yield event

# APIサーバーを起動
if __name__ == "__main__":
   app.run()