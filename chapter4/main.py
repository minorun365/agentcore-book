import asyncio, gc

from agents.orchestrator_agent import create_orchestrator_agent
from rich import print
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt


# ユーザーとの対話ループを実行し、質問をOrchestratorAgentに処理させる
async def main():
    orchestrator = create_orchestrator_agent()

    while True:
        user_input = Prompt.ask("何でも聞いて下さい")

        # ユーザーの入力に"exit"が含まれる場合は処理を終了する
        if "exit" in user_input:
            break

        # オーケストレーターエージェント呼び出し
        result = orchestrator(user_input)
        final_message = result.message["content"][-1]["text"]

        print(
            Panel(
                Markdown(final_message, justify="left"),
                title="Orchestrator response",
            )
        )


if __name__ == "__main__":
    asyncio.run(main())
    gc.collect()  # StrandsのPython 3.14バグ対策
