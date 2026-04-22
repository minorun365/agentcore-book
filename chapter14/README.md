# 第14章 RAGで社内データをエージェントに活かす

本章は解説中心の章のため、書籍本文にコマンド列（bashコマンド）の掲載はありません。サンプルコードを実際に動かしてみたい方のために、以下は本リポジトリのStreamlit製RAGアプリ（`main.py`）を手元で動かす場合の補助手順を記載しています。

第2章のハンズオンで作成したナレッジベースを利用します。第2章が未実施の場合は先に実施してください。

## 事前準備

ナレッジベース用アセット（`chapter2-handson-asset.zip`）を解凍

```bash
unzip chapter2-handson-asset.zip
```

依存関係をインストール

```bash
uv sync
```

## サンプルアプリの起動

Streamlitアプリを起動

```bash
uv run streamlit run main.py
```
