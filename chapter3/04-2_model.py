from strands import Agent
from strands.models import BedrockModel

# Bedrockのモデルを使用する場合はモデルIDだけを指定
agent = Agent(model="us.anthropic.claude-sonnet-4-6")
agent("こんにちは")


# モデルID以外の引数を指定する場合はBedrockModelを生成しモデル引数に指定
agent = Agent(
    model=BedrockModel(
        model_id="us.anthropic.claude-sonnet-4-6",
        region_name="us-east-1",
        temperature=1.0,
    )
)
agent("こんにちは")
