# 第11章 運用状況を可視化する「オブザーバビリティ」

サンプルコードを実際に動かしてみたい方のために、書籍に掲載されているコマンドをコピペしやすい形で掲載しています。

本章のサンプルコードは、第5章のハンズオンで作成したプロジェクト（ `handson/app/MyAgent/` ）に差し込む差分ファイル群です。章内でハンズオンは実施しません。

- `cloudwatch/` — CloudWatchへトレースを送信する構成（ADOT自動計装を利用）
    - `pyproject.toml`：第5章のハンズオンで作成した `handson/app/MyAgent/pyproject.toml` の依存関係をこの内容に差し替えます
    - `Dockerfile`：コンテナイメージでデプロイする場合に `handson/app/MyAgent/` へ配置します
- `langfuse/` — Langfuseへトレースを送信する構成
    - `main.py`：第5章のハンズオンで作成した `handson/app/MyAgent/main.py` をこの内容で置き換えます
    - `pyproject.toml` / `Dockerfile`：上記と同様に差し替え・配置します

## 11.5.2 AgentCoreランタイムからLangfuseへのトレース送信

Strands AgentsにOpenTelemetry向けの依存関係を追加

```bash
uv add 'strands-agents[otel]'
```
