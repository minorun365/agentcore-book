# 第13章 【ハンズオン】フルスタックエージェントを構築しよう

この章のハンズオンが実施しやすいように、書籍に掲載されているコマンドをコピペしやすい形で掲載しています。

## 13.3 【ハンズオン】AIエージェントの構築

### 13.3.1 プロジェクトの作成

```bash
# agentディレクトリをGit追跡から除外
printf '\nagent/\n' >> .gitignore

# AgentCore CLIをインストール
npm install -g @aws/agentcore@1.0.0-preview.8
```

```bash
agentcore create
```

### 13.3.2 依存パッケージの追加

```bash
cd agent/app/BookChecker
uv add requests==2.33.1 strands-agents-tools==0.5.1 playwright==1.58.0 nest-asyncio==1.6.0
```

### 13.3.3 カレンダー登録ツールの作成

```bash
touch calendar_tool.py
```

### 13.3.5 AgentCoreランタイムへのデプロイ

```bash
cd /workspaces/bookchecker/agent
agentcore deploy
```

## 13.4 【ハンズオン】Webアプリの構築

### 13.4.1 Next.jsプロジェクトの準備

```bash
cd /workspaces/bookchecker
```

### 13.4.2 テンプレートの整理

```bash
rm -rf amplify/data

npm install next@16.2.4 react@19.2.5 react-dom@19.2.5 @aws-amplify/ui-react@6.15.3 react-markdown@10.1.0 @aws-sdk/client-bedrock-agentcore@3.1037.0
```

### 13.4.3 フロントエンドのコード実装

```bash
touch app/providers.tsx
```

### 13.4.4 3LOコールバック用Route Handlerの作成

```bash
mkdir -p app/api/set-token
touch app/api/set-token/route.ts

mkdir -p app/api/oauth2/callback
touch app/api/oauth2/callback/route.ts
```

### 13.4.6 Amplifyへのデプロイとリソース確認

```bash
cd /workspaces/bookchecker
git add -A
git commit -m "最初のコミット"
git push
```

### 13.4.7 SSRコンピュートロールの設定

IAMロール作成時の「カスタム信頼ポリシー」に貼り付けるJSONです。

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "amplify.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

### 13.4.8 認証連携・環境変数・コールバックURLの設定

AgentCoreランタイムに設定する環境変数の変数名です。

- CALLBACK_URL
- CREDENTIAL_PROVIDER_NAME
- AWS_DEFAULT_REGION

ワークロードIDの許可URLリスト登録コマンドです。

```bash
aws bedrock-agentcore-control update-workload-identity --name <ランタイムID> --allowed-resource-oauth2-return-urls <コールバックURL>
```
