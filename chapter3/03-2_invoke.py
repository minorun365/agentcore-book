from strands import Agent


# ストリーミング処理を行う関数
def print_callback_handler(**kwargs):
    print(kwargs)


agent = Agent(
    # ストリーミング処理を行う関数を指定
    callback_handler=print_callback_handler
)
agent("こんにちは")
