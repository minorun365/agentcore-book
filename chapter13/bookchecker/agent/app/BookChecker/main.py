import os, asyncio
from strands import Agent
from strands_tools.browser import AgentCoreBrowser
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from bedrock_agentcore.memory.integrations.strands.session_manager import AgentCoreMemorySessionManager
from bedrock_agentcore.memory.integrations.strands.config import AgentCoreMemoryConfig, RetrievalConfig
from calendar_tool import make_calendar_tool

# 環境変数からメモリーのIDを取得（デプロイ時に自動設定）
MEMORY_ID = os.getenv("MEMORY_BOOKCHECKERMEMORY_ID")

# システムプロンプトを定義
SYSTEM_PROMPT = """あなたは技術書の新刊情報を調べて、ユーザーのGoogleカレンダーに発売日を登録するアシスタントです。

## 手順
1. Browser Toolを使って、新刊カレンダー（ https://www.sbcr.jp/calender/ ）にアクセス
2. 「PC/IT書籍」カテゴリでフィルタして、技術書の新刊一覧を取得
3. ユーザーの好みや指示に合った書籍をピックアップ
4. ユーザーに確認のうえ、発売日をGoogleカレンダーに登録

## ルール
- メモリーにユーザーの好みがあれば、それを参考にレコメンド
- カレンダーの予定名に書籍のタイトル、説明欄に著者や概要を記載
- 終日予定として登録する（end_dateはstart_dateの翌日を指定）

## 出力形式
- Markdownの表は使わず、箇条書きで情報を整理してください
- 絵文字は最小限にして、簡潔で読みやすい文章を心がけてください
"""


# AgentCore SDKでAPIサーバーを作成
app = BedrockAgentCoreApp()

# AgentCoreランタイムのエントリーポイント
@app.entrypoint
async def invoke(payload, context):
    # リクエストからプロンプトとセッションIDを取得
    prompt = payload.get("prompt", "")
    session_id = payload.get("session_id")

    # AIエージェントの応答と認可URLをまとめるキューを作成
    event_queue = asyncio.Queue()

    # ブラウザツールとカレンダーツールを作成
    browser = AgentCoreBrowser()
    calendar_tool = make_calendar_tool(event_queue)

    # メモリーの設定を定義
    memory_config = AgentCoreMemoryConfig(
        memory_id=MEMORY_ID,
        session_id=session_id,
        actor_id="user",
        retrieval_config={
            "/users/{actorId}/preferences": RetrievalConfig(),
        },
    )

    # メモリーのセッションマネージャーを作成
    session_manager = AgentCoreMemorySessionManager(
        agentcore_memory_config=memory_config,
    )

    # Strands AgentsでAIエージェントを作成
    agent = Agent(
        model="us.anthropic.claude-sonnet-4-6",
        tools=[browser.browser, calendar_tool],
        system_prompt=SYSTEM_PROMPT,
        session_manager=session_manager,
    )

    # AIエージェントをストリーミングモードで呼び出す関数
    async def agent_stream():
        in_tool_use = False
        try:
            # AIエージェントのストリーミング応答を処理
            async for event in agent.stream_async(prompt):
                if "data" in event and isinstance(event["data"], str):
                    # テキスト到着時、ツール実行中なら完了イベントを先に送信
                    if in_tool_use:
                        await event_queue.put({"type": "tool_result"})
                        in_tool_use = False
                    await event_queue.put(
                      {"type": "text", "data": event["data"]}
                    )
                elif "current_tool_use" in event:
                    # 前のツールが実行中なら完了イベントを送信
                    if in_tool_use:
                        await event_queue.put({"type": "tool_result"})
                    tool_info = event["current_tool_use"]
                    await event_queue.put({
                        "type": "tool_use",
                        "tool_name": tool_info.get("name", "")
                    })
                    in_tool_use = True
        except Exception as e:
            # エラー発生時はエラーイベントを送信
            await event_queue.put({"type": "error", "data": str(e)})
        finally:
            if in_tool_use:
                await event_queue.put({"type": "tool_result"})
            # ストリーム終了を通知
            await event_queue.put(None)

    # AIエージェントを非同期で実行（ポーリング中もSSE配信を止めない）
    task = asyncio.create_task(agent_stream())

    # キューからイベントを取り出してフロントエンドへSSEで配信
    while True:
        item = await event_queue.get()
        if item is None:
            break
        yield item

    # AIエージェントが動作完了するまで待機
    await task

# APIサーバーを起動
if __name__ == "__main__":
    app.run()
