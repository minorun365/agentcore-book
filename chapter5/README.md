# 第5章 AgentCoreの概要とメイン機能「ランタイム」

サンプルコードを実際に動かしてみたい方のために、書籍に掲載されているコマンドをコピペしやすい形で掲載しています。本章では、ランタイムへのデプロイを体験するハンズオン手順（5.3節）と、ハーネスを呼び出すサンプルコード（5.2節）の両方を扱います。

## 5.2 【サンプルコードのみ】まずは「ハーネス」でAgentCoreを体験

### 5.2.3 作成したエージェントを呼び出す

マネジメントコンソールで作成したハーネスのARNを `00_invoke_harness.py` 内の `<ハーネスARN>` に置き換えてから実行してください。

```bash
uv run 00_invoke_harness.py
```

## 5.3 【ハンズオン】AIエージェントをランタイムにデプロイしてみよう

### 5.3.2 AgentCore CLIでプロジェクトを作成する

【2026/6/30更新】CDKのアップデートに伴うエラー回避のため、AgentCore CLIのインストールコマンドを修正しました。

```bash
# 本章用のディレクトリを作成して移動
mkdir chapter5
cd chapter5

# AgentCore CLIをインストール
npm install -g @aws/agentcore@latest
```

```bash
agentcore create
```

```bash
cd handson
```

### 5.3.4 AgentCoreランタイムへのデプロイ

```bash
agentcore deploy
```

### 5.3.5 デプロイしたエージェントの呼び出し

```bash
uv init --python 3.14
uv add "boto3[crt]==1.42.96"
```

```bash
touch invoke.py
```

```bash
uv run invoke.py
```
