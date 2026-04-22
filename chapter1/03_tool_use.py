import math

import boto3

# Bedrock Runtimeを呼び出すクライアントを生成
client = boto3.client("bedrock-runtime")


# 円の面積を計算するツール
def circle_area_tool(radius: float) -> str:
    area = math.pi * radius**2
    return f"{area:.10f}"


# ツール名とツール関数を辞書型で保持
tool_list = {"circle_area_tool": circle_area_tool}

# ツール定義
tool_spec = {
    "toolSpec": {
        "name": "circle_area_tool",
        "description": "円の面積を計算するツール",
        "inputSchema": {
            "json": {
                "type": "object",
                "properties": {
                    "radius": {
                        "type": "number",
                        "description": "円の半径（cm）",
                    }
                },
                "required": ["radius"],
            }
        },
    }
}

# メッセージを作成
messages = [
    {
        "role": "user",
        "content": [
            # 送信プロンプト
            {"text": "半径3センチと半径7センチの円の面積を教えて"},
        ],
    },
]

# Converse API呼び出し
response = client.converse(
    modelId="us.anthropic.claude-sonnet-4-6",
    messages=messages,
    toolConfig={"tools": [tool_spec]},  # ツール定義を指定
)

while True:
    tool_request = []
    for content in response["output"]["message"]["content"]:
        if "text" in content:
            print(f"text: {content['text']}")
        if "toolUse" in content:
            tool_request.append(content)

    # ツール呼び出し要求がなければwhileを抜ける
    if len(tool_request) == 0:
        break

    # Bedrockのレスポンスをメッセージに追加
    messages.append(response["output"]["message"])

    # ツール実行結果を格納する変数
    tool_result = []

    for tool_use in tool_request:
        tool_use_id = tool_use["toolUse"]["toolUseId"]
        tool_name = tool_use["toolUse"]["name"]
        tool_input = tool_use["toolUse"]["input"]

        print(
            f"tool_id: {tool_use_id},  tool_name: {tool_name},"
            f" tool_input: {tool_input}"
        )

        # ツールリストから呼び出すツールを取得
        tool = tool_list[tool_name]

        # ツールを実行
        result = tool(**tool_input)

        print(f"tool_result: {result}")

        # ツール実行結果を保持
        tool_result.append(
            {
                "toolResult": {
                    "toolUseId": tool_use_id,
                    "content": [{"text": result}],
                }
            }
        )

    # ツール実行結果をメッセージに追加
    messages.append({"role": "user", "content": tool_result})

    # ツール実行結果を含めたメッセージを再度Bedrockに送信
    response = client.converse(
        modelId="us.anthropic.claude-sonnet-4-6",
        messages=messages,
        toolConfig={"tools": [tool_spec]},
    )
