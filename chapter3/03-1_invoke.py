from strands import Agent

agent = Agent(
    # Noneを指定
    callback_handler=None,
)
result = agent("こんにちは")

# resultを出力
print(result.message["content"][-1]["text"])
