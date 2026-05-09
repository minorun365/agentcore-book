# 第7章 外部認証を制御する「アイデンティティ」

本章はAgentCoreアイデンティティの解説章のため、書籍本文中にコマンド操作はありません。サンプルコードを実際に動かしてみたい方のために、以下は手元で動かす場合の補助手順を記載しています。

`01_outbound.py` は書籍本文の手順でAtlassianのOAuthプロバイダーを事前登録してから実行してください。`02_callback_server.py` は同ディレクトリに `.agentcore.json`（`{"user_id": "..."}` の内容）を配置する必要があります。

## 事前準備

依存関係をインストール

```bash
uv sync
```

## 7.3 【サンプルコードのみ】アウトバウンド認証

アウトバウンド認証を使ったツール実装例（`01_outbound.py`）の実行

```bash
uv run 01_outbound.py
```

3LOフローのコールバックサーバー（`02_callback_server.py`）の起動

```bash
uv run 02_callback_server.py
```

OAuth認可完了後は `Ctrl+C` でサーバーを停止してください。port 9090 が使用中だった場合は `lsof -i :9090 -t | xargs kill` で解放できます。
