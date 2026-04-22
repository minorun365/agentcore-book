# 第3章 Strands Agents入門

サンプルコードを実際に動かしてみたい方のために、書籍に掲載されているコマンドをコピペしやすい形で掲載しています。

各スニペット（`01_simple.py` 〜 `18_evals.py`）は単体で実行できますが、`16-1_a2a_server.py` と `16-3_a2a_client.py` のように別ターミナルでペア起動が必要なものもあります。

## 事前準備

依存関係をインストール

```bash
uv sync
```

各スニペットは、ファイル名を書き換えて以下の形式で実行できます。

```bash
uv run 01_simple.py
```

## 3.2.1 AIエージェントの構築

```bash
uv add strands-agents
```

## 3.3.1 モデル

```bash
uv add strands-agents[openai]  # OpenAIの場合
uv add strands-agents[anthropic]  # Anthropicの場合
```

## 3.3.3 ツール

```bash
uv add strands-agents-tools
```

```bash
uv add strands-agents-tools[rss]
```

## 3.4.2 Pythonプロジェクトの作成

```bash
mkdir -p chapter3/handson
cd chapter3/handson
```

```bash
uv init --python 3.14
uv add strands-agents==1.36.0 strands-agents-tools==0.5.0 boto3[crt]==1.42.92
```

## 3.4.3 モデル、プロンプト、ツールを組み合わせる

```bash
uv run main.py
```

## 3.6.7 Strands AgentsでA2A連携を行う

```bash
uv add "strands-agents[a2a]" strands-agents-tools
```

```bash
curl http://localhost:9000/.well-known/agent-card.json
```

## 3.7.1 トレーシング

```bash
uv add "strands-agents[otel]"
```

## 3.7.2 Evals SDK

```bash
uv add strands-agents-evals
```
