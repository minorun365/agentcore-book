# 第12章 自動で品質をチェックする「評価」

サンプルコードを実際に動かしてみたい方のために、書籍に掲載されているコマンドをコピペしやすい形で掲載しています。

サンプルコード（`02_on_demand.py`）は、AWS認証情報を設定したうえで単体実行できます。Strands Agents EvalsとAgentCoreの組み込み評価器（Builtin.Helpfulness）を利用します。

## 事前準備

依存関係をインストール

```bash
uv sync
```

## 12.3.2 オンデマンド評価の実行

Strands Agents EvalsとAgentCoreを連携させる依存関係を追加

```sh
uv add 'bedrock-agentcore[strands-agents-evals]==1.6.3'
```

オンデマンド評価のサンプルコード（`02_on_demand.py`）の実行

```bash
uv run 02_on_demand.py
```
