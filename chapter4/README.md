# 第4章 【ハンズオン】リサーチエージェントを作ろう

この章のハンズオンが実施しやすいように、書籍に掲載されているコマンドをコピペしやすい形で掲載しています。

## 4.2.2 Pythonプロジェクトの作成

```bash
mkdir -p chapter4
cd chapter4
uv init --python 3.14
```

```bash
uv add strands-agents==1.36.0 "strands-agents-tools[rss]"==0.5.0 rich==14.3.3
uv add --dev "boto3[crt]"==1.42.92
```

## 4.4.1 プログラムの実行

```bash
uv run main.py
```
