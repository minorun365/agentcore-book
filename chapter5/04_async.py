import time
import threading
from strands import Agent, tool
from bedrock_agentcore import BedrockAgentCoreApp

# AgentCore SDKでAPIクライアントを作成
app = BedrockAgentCoreApp()

# スライド資料を作成するツール（中身はダミー）
@tool
def slide_generator():
    # 非同期タスクを開始
    task_id = app.add_async_task("スライド作成")

    # バックグラウンドスレッドでタスクを実行
    def create_pptx():
        time.sleep(10)  # ダミー処理
        # 非同期タスクを完了
        app.complete_async_task(task_id)

    threading.Thread(
        target=create_pptx, daemon=True
    ).start()
    return "スライド作成を開始しました"

# Strandsでエージェントを作成
agent = Agent(tools=[slide_generator])

# APIサーバーのエントリーポイントを作成
@app.entrypoint
def invoke(payload):
    prompt = payload.get("prompt")
    return agent(prompt)

# APIサーバーを起動
if __name__ == "__main__":
    app.run()