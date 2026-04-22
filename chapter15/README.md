# 第15章 【ハンズオン】アンビエントエージェントをCDKで作ろう

この章のハンズオンが実施しやすいように、書籍に掲載されているコマンドをコピペしやすい形で掲載しています。

## 15.2.1 ディレクトリ構成

```bash
# Pythonプロジェクトを作成して移動
uv init chapter15 --python 3.14
cd chapter15

# データディレクトリを作成
mkdir data
```

```bash
uv add strands-agents==1.36.0 bedrock-agentcore==1.6.3 boto3==1.42.92
```

## 15.2.3 環境変数と設定ファイル

```bash
touch .env
```

```bash
touch data/users.json
```

```bash
touch data/classification_rules.json
```

## 15.3.1 AIエージェントの初期設定

```bash
mkdir src
touch src/__init__.py src/agent.py
```

## 15.3.4 Lambda関数の作成

```bash
mkdir -p src/lambda/agent_invoker
mkdir -p src/lambda/approval_callback
```

```bash
touch src/lambda/agent_invoker/agent_invoker.py
```

```bash
touch src/lambda/approval_callback/approval_callback.py
```

## 15.5.1 プロジェクト設定とDockerfile

```bash
mkdir -p cdk/bin cdk/lib docker
touch cdk/tsconfig.json cdk/cdk.json cdk/bin/app.ts cdk/lib/expense-agent-stack.ts docker/Dockerfile
```

```bash
cd cdk

# Node.jsプロジェクトを初期化
npm init -y

# CDK本体とAgentCoreコンストラクトをインストール
npm install aws-cdk-lib@2.250.0 constructs@10.6.0 @aws-cdk/aws-bedrock-agentcore-alpha@2.250.0-alpha.0 @cdklabs/deploy-time-build@0.1.2 dotenv@17.4.2

# TypeScriptとCDK CLIを開発用にインストール
npm install -D typescript@6.0.3 ts-node @types/node aws-cdk@2.1118.2
```

## 15.6.1 CDKデプロイ

```bash
cd /workspaces/agentcore-handson/chapter15/cdk
npx cdk bootstrap
```

```bash
npx cdk deploy
```

## 15.6.2 動作確認

```bash
cd /workspaces/agentcore-handson/chapter15
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
```

パターン1: 社内ルールあり、10万円未満（課長承認）

```bash
aws s3 cp data/receipt_rule_under100k.png \
  s3://expense-agent-${ACCOUNT_ID}/receipts/001/test_$(date +%s).png
```

他のパターンのテスト

```bash
# パターン2: 社内ルールなし（LLM推論で分類）、10万未満（課長承認）
aws s3 cp data/receipt_search_under100k.png \
  s3://expense-agent-${ACCOUNT_ID}/receipts/001/test_$(date +%s).png

# パターン3: 社内ルールあり、10万以上（部長承認）
aws s3 cp data/receipt_rule_over100k.png \
  s3://expense-agent-${ACCOUNT_ID}/receipts/001/test_$(date +%s).png

# パターン4: 社内ルールなし（LLM推論で分類）、10万以上（部長承認）
aws s3 cp data/receipt_search_over100k.png \
  s3://expense-agent-${ACCOUNT_ID}/receipts/001/test_$(date +%s).png
```

## 15.6.3 トラブルシューティング

SNSサブスクリプションの状態確認

```bash
aws sns list-subscriptions-by-topic \
  --topic-arn <トピックARN>
```

SNSサブスクリプションの再登録

```bash
aws sns subscribe \
  --topic-arn <トピックARN> \
  --protocol email \
  --notification-endpoint <メールアドレス>
```

CLIでサブスクリプションを承認

```bash
aws sns confirm-subscription \
  --topic-arn <トピックARN> \
  --token <トークン> \
  --authenticate-on-unsubscribe true
```

## 15.6.4 クリーンアップ

```bash
cd /workspaces/agentcore-handson/chapter15/cdk
npx cdk destroy
```
