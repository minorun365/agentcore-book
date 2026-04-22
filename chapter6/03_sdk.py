import time
from bedrock_agentcore.memory.session import MemorySessionManager
from bedrock_agentcore.memory.constants import ConversationalMessage, MessageRole

# メモリーの設定
MEMORY_ID = "<ここにメモリーIDを入れる>"
STRATEGY_ID = "<ここに戦略IDを入れる>"
ACTOR_ID = "User1"
SESSION_ID = "Session1"

# 長期記憶の名前空間
NAMESPACE = f"/strategies/{STRATEGY_ID}/actors/{ACTOR_ID}/"

# セッションマネージャーの作成
session_manager = MemorySessionManager(memory_id=MEMORY_ID)

# メモリーセッションの作成
session = session_manager.create_memory_session(
    actor_id=ACTOR_ID,
    session_id=SESSION_ID
)

# 会話ターンの追加（短期記憶に保存される）
session.add_turns(
    messages=[
        ConversationalMessage(
            "私は生エビのアレルギーもあります。",
            MessageRole.USER
        )
    ],
)
session.add_turns(
    messages=[
        ConversationalMessage(
            "承知しました、別の食材を利用します。",
            MessageRole.ASSISTANT
        )
    ],
)

# 短期記憶の取得と表示
turns = session.get_last_k_turns(k=5)
print("【短期記憶の取得結果】")
for turn in turns:
    print(turn[0])

# 長期メモリーへの反映を待機（非同期処理のため約1分待つ）
time.sleep(70)

# セマンティック検索で長期記憶を取得
search_results = session.search_long_term_memories(
    query="このユーザーの特徴は？",
    namespace_prefix=NAMESPACE
)
print("【長期記憶の取得結果】")
for result in search_results:
    print(result)
