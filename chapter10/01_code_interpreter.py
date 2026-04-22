from strands import Agent
from strands_tools.code_interpreter import AgentCoreCodeInterpreter

# コードインタープリターツールを初期化
code_interpreter = AgentCoreCodeInterpreter()

# エージェントを作成
agent = Agent(tools=[code_interpreter.code_interpreter])

# CSVデータからグラフを作成
csv_data = """月,売上(万円)
4月,120
5月,150
6月,180"""

response = agent(f"以下のCSVデータを棒グラフにしてください。\n\n{csv_data}")