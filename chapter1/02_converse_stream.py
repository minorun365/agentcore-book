import boto3

# Bedrock Runtimeを呼び出すクライアントを生成
client = boto3.client("bedrock-runtime")

# ConverseStream API呼び出し
streaming_response = client.converse_stream(
    modelId="us.anthropic.claude-sonnet-4-6",
    messages=[
        {
            "role": "user",
            "content": [
                {"text": "日本の四季をテーマにしたポエムを作って"},  # 送信プロンプト
            ],
        },
    ],
)

# ストリーミングで返却される結果を逐次処理
for chunk in streaming_response["stream"]:
    # テキストのみをコンソールに出力
    if "contentBlockDelta" in chunk:
        text = chunk["contentBlockDelta"]["delta"]["text"]
        print(text, end="")  # 出力後の改行を抑制するために「end=""」を指定
print("")  # すべての出力が終わったら改行する
