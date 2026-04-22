# 第6章 記憶を管理する「メモリー」

サンプルコードを実際に動かしてみたい方のために、書籍に掲載されているコマンドをコピペしやすい形で掲載しています。

本章の各サンプルコードは、書籍本文の手順でAgentCoreメモリーのメモリーストアを作成したうえで、コード内の `MEMORY_ID` / `STRATEGY_ID` をご自身の環境の値に置き換えてから実行してください。

## セットアップ

```bash
uv sync
```

## 6.2.2 会話イベントの保存と取得

```bash
uv run 01_stm.py
```

## 6.3.2 長期記憶の取得

```bash
uv run 02_ltm.py
```

## 6.4.1 SDKによる実装例

```bash
uv run 03_sdk.py
```

## 6.5.1 エージェントへのメモリー統合

```bash
uv add "bedrock-agentcore[strands-agents]"
```

```bash
uv run 04_strands.py
```
