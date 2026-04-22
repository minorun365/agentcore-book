from strands import Agent

### 実行したいタスク
task = "「2026年の日本のスタートアップ業界の成長トレンド」について最新の情報を調査してください。"

### Researchエージェント
research = Agent(
    system_prompt="あなたは研究の専門家です。重要な情報を探してください。",
)
research_results = research(task)

### Analysisエージェント
analysis = Agent(
    system_prompt="あなたは研究データを分析して、重要な洞察を抽出します。",
)
# Researchエージェントの実行結果をプロンプトに含めて実行
analysis_results = analysis(f"次の調査結果を分析してください。\n\n{research_results}")

### Reportエージェント
report = Agent(
    system_prompt="あなたは分析に基づいて洗練されたレポートを作成します。",
)
# Analysisエージェントの実行結果をプロンプトに含めて実行
report_result = report(
    f"次の分析をもとにレポートを作成してください。\n\n{analysis_results}"
)
