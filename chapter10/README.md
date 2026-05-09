# 第10章 クラウドならではの「組み込みツール」

サンプルコードを実際に動かしてみたい方のために、書籍に掲載されているコマンドをコピペしやすい形で掲載しています。

本章のサンプル（`01_browser.py`、`02_code_interpreter.py`）は単体実行できます。

> **注意**: ブラウザツール（`01_browser.py`）は Python 3.13 で動かしてください。
>
> ```bash
> uv init --python 3.13
> ```

## セットアップ

```bash
uv sync
```

各サンプルは以下の形式で実行できます。

```bash
uv run 01_browser.py
```

## 10.2 【サンプルコードのみ】AgentCoreブラウザ

### 10.2.3 Strands Agentsからの利用例

```bash
uv add "strands-agents-tools[agent_core_browser]==0.5.1"
```

## 10.3 【サンプルコードのみ】AgentCoreコードインタープリター

### 10.3.3 Strands Agentsからの利用

```bash
uv add "strands-agents-tools[agent_core_code_interpreter]==0.5.1"
```
