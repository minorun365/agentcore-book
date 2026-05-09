# 第3章 Strands Agents入門

サンプルコードを実際に動かしてみたい方のために、書籍に掲載されているコマンドをコピペしやすい形で掲載しています。本章は各機能を試すスニペット（3.2/3.3/3.6/3.7節）と、ハンズオン（3.4節）の両方を扱います。

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

## 3.2 【サンプルコードのみ】Strands Agentsの基本的な使い方

### 3.2.1 AIエージェントの構築

```bash
uv add strands-agents==1.38.0
```

## 3.3 【サンプルコードのみ】エージェントの構成要素

### 3.3.1 モデル

```bash
uv add "strands-agents[openai]==1.38.0"  # OpenAIの場合
uv add "strands-agents[anthropic]==1.38.0"  # Anthropicの場合
```

`04-3_model.py` を実行する場合は、コード内の `api_key="<api key>"` を OpenAI のAPIキーに書き換えてから実行してください。

### 3.3.2 プロンプト

`05_prompt.py` の後半は画像入力の例として `image.jpg` を読み込みます。

### 3.3.3 ツール

```bash
uv add strands-agents-tools==0.5.1
```

```bash
uv add "strands-agents-tools[rss]==0.5.1"
```

## 3.4 【ハンズオン】Strands Agentsを試してみよう

### 3.4.2 Pythonプロジェクトの作成

```bash
mkdir -p chapter3/handson
cd chapter3/handson
```

```bash
uv init --python 3.14
uv add strands-agents==1.38.0 strands-agents-tools==0.5.1 "boto3[crt]==1.42.96"
```

### 3.4.3 モデル、プロンプト、ツールを組み合わせる

```bash
uv run main.py
```

## 3.6 【サンプルコードのみ】マルチエージェント

### 3.6.7 Strands AgentsでA2A連携を行う

```bash
uv add "strands-agents[a2a]==1.38.0" strands-agents-tools==0.5.1
```

```bash
curl http://localhost:9000/.well-known/agent-card.json
```

## 3.7 【サンプルコードのみ】トレーシングと評価

### 3.7.1 トレーシング

```bash
uv add "strands-agents[otel]==1.38.0"
```

### 3.7.2 Evals SDK

```bash
uv add strands-agents-evals==0.1.15
```
