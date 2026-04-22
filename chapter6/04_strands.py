from strands import Agent
from bedrock_agentcore.memory.integrations.strands.config import AgentCoreMemoryConfig, RetrievalConfig
from bedrock_agentcore.memory.integrations.strands.session_manager import AgentCoreMemorySessionManager

# メモリーの設定
MEMORY_ID = "<ここにメモリーIDを入れる>"
STRATEGY_ID = "<ここに戦略IDを入れる>"
ACTOR_ID = "User1"
SESSION_ID = "Session1"

# 長期記憶の名前空間
NAMESPACE = f"/strategies/{STRATEGY_ID}/actors/{ACTOR_ID}/"

# メモリーの設定を作成（長期記憶の自動取得を有効化）
memory_config = AgentCoreMemoryConfig(
    memory_id=MEMORY_ID,
    session_id=SESSION_ID,
    actor_id=ACTOR_ID,
    retrieval_config={NAMESPACE: RetrievalConfig()}
)

# セッションマネージャーを作成
session_manager = AgentCoreMemorySessionManager(
    agentcore_memory_config=memory_config
)

# エージェントを作成（メモリーを統合）
agent = Agent(
    model="us.anthropic.claude-sonnet-4-6",
    session_manager=session_manager
)

# 会話を実行（短期記憶に自動保存される）
agent("私はトルコ料理が好きです。")
