# 第1章 生成AIの基本とAmazon Bedrock入門

サンプルコードを実際に動かしてみたい方のために、書籍に掲載されているコマンドをコピペしやすい形で掲載しています。

## 1.5 【ハンズオン】Bedrockを使ってみよう

### 1.5.3 Converse APIで呼び出す

```bash
aws sts get-caller-identity
```

```bash
mkdir -p chapter1
cd chapter1
```

```bash
uv init --python 3.14
uv add "boto3[crt]==1.42.96"
```

```bash
uv run 01_converse.py
```

### 1.5.4 ConverseStream APIで呼び出す

```bash
uv run 02_converse_stream.py
```

### 1.5.5 ツール呼び出しを含むリクエスト

```bash
uv run 03_tool_use.py
```
