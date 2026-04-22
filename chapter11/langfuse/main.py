import base64
import os

from strands import Agent
from strands.telemetry import StrandsTelemetry
from bedrock_agentcore import BedrockAgentCoreApp

# Langfuseの認証設定（環境変数から取得）
LANGFUSE_PUBLIC_KEY = os.environ["LANGFUSE_PUBLIC_KEY"]
LANGFUSE_SECRET_KEY = os.environ["LANGFUSE_SECRET_KEY"]
LANGFUSE_HOST = os.environ["LANGFUSE_HOST"]

# OTLPエクスポーターの認証ヘッダーを生成
auth = base64.b64encode(
    f"{LANGFUSE_PUBLIC_KEY}:{LANGFUSE_SECRET_KEY}".encode()
).decode()

# Langfuseにトレースを送信するよう設定
StrandsTelemetry().setup_otlp_exporter(
    endpoint=f"{LANGFUSE_HOST}/api/public/otel/v1/traces",
    headers={
        "Authorization": f"Basic {auth}",
        "x-langfuse-ingestion-version": "4",  # v4対応
    },
)

# AIエージェントとAPIサーバーを作成
agent = Agent()
app = BedrockAgentCoreApp()

# APIサーバーのエントリーポイントを設定
@app.entrypoint
async def invoke(payload, context):
    prompt = payload.get("prompt")
    return agent(prompt)

# APIサーバーを起動
if __name__ == "__main__":
    app.run()
