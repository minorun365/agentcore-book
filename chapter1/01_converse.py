import boto3

# Bedrock Runtimeを呼び出すクライアントを生成
client = boto3.client("bedrock-runtime")

# Converse API呼び出し
response = client.converse(
    modelId="us.anthropic.claude-sonnet-4-6",
    messages=[
        {
            "role": "user",
            "content": [
                {"text": "こんにちは"},  # 送信プロンプト
            ],
        },
    ],
)

# テキストのみをコンソールに出力
print(response["output"]["message"]["content"][0]["text"])
