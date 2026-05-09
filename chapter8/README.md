# 第8章 ツールを束ねる「ゲートウェイ」

本章はAgentCoreゲートウェイの解説章のため、書籍本文中にコマンド操作はありません。サンプルコードを実際に動かしてみたい方のために、以下は手元で動かす場合の補助手順を記載しています。

`01_mcp_client.py` と `02_http_target.py` はコード内の `<ゲートウェイID>` `<ターゲット名>` などをご自身の環境の値に置き換えてから実行してください。`03_interceptor.py` はAgentCoreゲートウェイのインターセプターとしてLambdaにデプロイするコードで、ローカル実行は行いません。

## 事前準備

依存関係をインストール

```bash
uv sync
```

## 8.4 【サンプルコードのみ】AgentCoreゲートウェイの呼び出し

### 8.4.1 MCPターゲットの呼び出し例

MCP接続の実装例（`01_mcp_client.py`）の実行

```bash
uv run 01_mcp_client.py
```

### 8.4.2 HTTPターゲットの呼び出し例

HTTPターゲット経由でAgentCoreランタイムを呼び出す例（`02_http_target.py`）の実行

```bash
uv run 02_http_target.py
```
