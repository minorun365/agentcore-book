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
   return agent(prompt)

# APIサーバーを起動
if __name__ == "__main__":
   app.run()