# 書籍「Amazon Bedrock AgentCore実践入門」サンプルコード

標記書籍のハンズオン用コードや、アップデートのお知らせなどを本リポジトリで公開します。

https://www.amazon.co.jp/dp/4815641234

<img width="960" height="540" alt="画像" src="https://github.com/user-attachments/assets/04e8cf88-5aa0-4129-8632-88db69d20ee5" />


## 📣 新着のお知らせ（詳細は後述）

<!-- 発売後、仕様変更やライブラリアップデートに伴う更新情報をここに追記していきます。 -->


## 💻 サンプルコードの使い方

各チャプター名のディレクトリ配下に、書籍内のサンプルコードを格納しています。コードの打ち間違いによるエラーを防ぐためにも、コピペ用にぜひ活用ください。

| 章 | 内容 | ディレクトリ |
|----|------|----|
| 第1章 | 生成AIの基本とAmazon Bedrock入門 | [`chapter1/`](./chapter1) |
| 第2章 | AIエージェント入門（概念解説のみ） | - |
| 第3章 | Strands Agents入門 | [`chapter3/`](./chapter3) |
| 第4章 | 【ハンズオン】リサーチエージェントを作ろう | [`chapter4/`](./chapter4) |
| 第5章 | AgentCoreの概要とメイン機能「ランタイム」 | [`chapter5/`](./chapter5) |
| 第6章 | 記憶を管理する「メモリー」 | [`chapter6/`](./chapter6) |
| 第7章 | 外部認証を制御する「アイデンティティ」 | [`chapter7/`](./chapter7) |
| 第8章 | ツールを束ねる「ゲートウェイ」 | [`chapter8/`](./chapter8) |
| 第9章 | ツール利用を制御する「ポリシー」 | [`chapter9/`](./chapter9) |
| 第10章 | クラウドならではの「組み込みツール」 | [`chapter10/`](./chapter10) |
| 第11章 | 運用状況を可視化する「オブザーバビリティ」 | [`chapter11/`](./chapter11) |
| 第12章 | 品質を自動評価する「評価」 | [`chapter12/`](./chapter12) |
| 第13章 | 【ハンズオン】フルスタックエージェントを構築しよう | [`chapter13/`](./chapter13) |
| 第14章 | RAGで社内データをエージェントに活かす | [`chapter14/`](./chapter14) |
| 第15章 | 【ハンズオン】アンビエントエージェントをCDKで作ろう | [`chapter15/`](./chapter15) |
| 第16章 | AIエージェントを業務にうまく導入する（概念解説のみ） | - |

### 動作環境

- Python 3.14
- パッケージ管理: [uv](https://github.com/astral-sh/uv)
- AWSリージョン: バージニア北部（`us-east-1`）
- 主要モデル: Claude Sonnet 4.6 / Haiku 4.5 / Opus 4.6（USクロスリージョン推論プロファイル）

### 認証と環境変数

- **AWS認証**: 本書のサンプルはすべて **AWS SSO 認証セッション**を前提としています。実行前に `aws sts get-caller-identity` で認証済みセッションがあることを確認してください（アクセスキー・シークレットキーをコードに直接書く構成は使いません）
- **追加のAPIキー・環境変数が必要な章**:
  - **第3章**: `06_tools.py` で Tavily 検索ツールをデモします。実行する場合は [Tavily](https://tavily.com/) の API キーを取得し、シェル環境変数 `TAVILY_API_KEY` を設定してください
  - **第11章**（Langfuse構成）: Langfuse の `LANGFUSE_PUBLIC_KEY` / `LANGFUSE_SECRET_KEY` / `LANGFUSE_HOST` を **AgentCore ランタイムの環境変数**として設定します
  - **第13章**: `CREDENTIAL_PROVIDER_NAME` / `CALLBACK_URL` / `AWS_DEFAULT_REGION` / `MEMORY_BOOKCHECKERMEMORY_ID` を **AgentCore ランタイムの環境変数**、`NEXT_PUBLIC_AGENT_ARN` を **Amplify Hosting の環境変数**として設定します
  - **第15章**: ローカルの `.env` に `BEDROCK_MODEL_ID` および Confluence 接続情報（`CONFLUENCE_URL` / `CONFLUENCE_EMAIL` / `CONFLUENCE_API_TOKEN` / `CONFLUENCE_SPACE_KEY`）を設定します。テンプレートは [`chapter15/.env.example`](./chapter15/.env.example) を参照

各章の具体的な手順は、章ディレクトリ配下の `README.md` をご覧ください。


## 🆘 エラー等でハンズオンが進められないときは

[Issues](https://github.com/minorun365/agentcore-book/issues) より、テンプレートを使って問い合わせを投稿ください。著者陣がベストエフォートで解決のお手伝いをさせていただきます。


## 📗 お知らせ詳細

<!-- 発売後に仕様変更やライブラリアップデートに伴う更新情報をここに記載していきます。 -->


## 🥰 読者のみなさまのブログ紹介

<!-- 発売後、読者のみなさまから寄せられた感想・書評をここに紹介させていただきます。 -->


## ✍️ 著者

- **御田 稔**（Minoru Onda / KAG みのるん） [@minorun365](https://github.com/minorun365) — 第5章〜第13章、第16章、付録
- **森田 和明**（Kazuaki Morita / KTC） [@moritalous](https://github.com/moritalous) — 第1章、第3章、第4章、第14章
- **熊田 寛**（Kan Kumada / Relic） [@kumada15](https://github.com/kumada15) — 第2章、第15章


## 📄 ライセンス

[MIT License](./LICENSE)
