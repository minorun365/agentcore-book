# 第5章 AgentCoreの概要とメイン機能「ランタイム」

この章のハンズオンが実施しやすいように、書籍に掲載されているコマンドをコピペしやすい形で掲載しています。

## 5.2.2 AgentCore CLIでプロジェクトを作成する

```bash
npm install -g @aws/agentcore
```

```bash
agentcore create
```

```bash
cd handson
```

## 5.2.4 AgentCoreランタイムへのデプロイ

```bash
agentcore deploy
```

## 5.2.5 デプロイしたエージェントの呼び出し

```bash
uv init --python 3.14
uv add "boto3[crt]"==1.42.92
```

```bash
touch invoke.py
```

```bash
uv run invoke.py
```
