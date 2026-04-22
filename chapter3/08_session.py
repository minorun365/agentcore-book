from strands import Agent
from strands.session import FileSessionManager

session_id = "test-session"  # セッションID
storage_dir = "./session_dir"  # 保存先ディレクトリ

session_manager = FileSessionManager(session_id=session_id, storage_dir=storage_dir)

agent = Agent(
    session_manager=session_manager,
)
