from strands import Agent

# model引数が未指定の場合は、BedrockModelモデルのデフォルトモデル（執筆時点ではClaude Sonnet 4）が使用される
agent = Agent()
agent("こんにちは")