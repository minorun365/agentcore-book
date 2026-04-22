import boto3
import json

# AWS SDKでAgentCore用のAPIクライアントを作成
client = boto3.client('bedrock-agentcore')

# AgentCoreランタイムを呼び出す
response = client.invoke_agent_runtime(
   agentRuntimeArn="arn:aws:bedrock-agentcore:us-east-1:xxxxxxxxxxxx:runtime/handson_MyAgent-XXXXXXXXXX", # あなたのランタイムARNを記載
   runtimeSessionId="this-is-runtime-session-id-000001",
   payload=json.dumps({"prompt": "AgentCoreについて教えて"})
)

# ストリーミングレスポンスを1行ずつ処理
for line in response["response"].iter_lines():
   line = line.decode("utf-8")

   # データを含んでいたらテキストを抽出表示
   if line.startswith("data: "):
       try:
           data = json.loads(line[6:])
           text = data["event"]["contentBlockDelta"]["delta"]["text"]
           print(text, end="", flush=True)
       except:
           pass