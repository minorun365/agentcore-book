import boto3
from datetime import datetime

# APIクライアントの作成
agentcore = boto3.client("bedrock-agentcore")

# メモリーの設定
MEMORY_ID = "<ここにメモリーIDを入れる>"
ACTOR_ID = "User1"
SESSION_ID = "Session1"

# 会話イベントの保存
agentcore.create_event(
    memoryId=MEMORY_ID,
    actorId=ACTOR_ID,
    sessionId=SESSION_ID,
    eventTimestamp=datetime.now(),
    payload=[
        {
            "conversational": {
                "content": {"text": "私はパクチーが苦手です。"},
                "role": "USER"
            }
        },
        {
            "conversational": {
                "content": {"text": "承知しました、別の食材を利用します。"},
                "role": "ASSISTANT"
            }
        }
    ]
)

# イベントの取得と表示
response = agentcore.list_events(
    memoryId=MEMORY_ID,
    actorId=ACTOR_ID,
    sessionId=SESSION_ID
)
print(response["events"])
