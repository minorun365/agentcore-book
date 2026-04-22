import boto3

# APIクライアントの作成
agentcore = boto3.client("bedrock-agentcore")

# メモリーの設定
MEMORY_ID = "<ここにメモリーIDを入れる>"
STRATEGY_ID = "<ここに戦略IDを入れる>"
ACTOR_ID = "User1"

# 長期記憶の名前空間
NAMESPACE = f"/strategies/{STRATEGY_ID}/actors/{ACTOR_ID}/"

# セマンティック検索で長期記憶を取得
results = agentcore.retrieve_memory_records(
    memoryId=MEMORY_ID,
    namespace=NAMESPACE,
    searchCriteria={
        "searchQuery": "このユーザーの特徴は？"
    }
)

# 結果を表示
for record in results["memoryRecordSummaries"]:
    print(record)
