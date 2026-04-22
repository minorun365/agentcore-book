from strands import Agent

agent = Agent(
    system_prompt="あなたはリサーチエージェントです。ツールを活用して情報を収集し回答します。回答はMarkdown形式で出力します。",
)

result = agent("Bedrockについて情報収集をしてください。")

with open("image.jpg", mode="rb") as f:
    image_bytes = f.read()

result = agent(
    [
        {
            "image": {"format": "jpeg", "source": {"bytes": image_bytes}},
        },
        {"text": "画像に写っている動物を特定してください"},
    ]
)
