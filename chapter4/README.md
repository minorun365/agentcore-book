# 第4章 【ハンズオン】リサーチエージェントを作ろう

この章のハンズオンが実施しやすいように、書籍に掲載されているコマンドをコピペしやすい形で掲載しています。

## 4.2 【ハンズオン】プロジェクトのセットアップ

### 4.2.2 Pythonプロジェクトの作成

【2026/8/11更新】uv 0.12以降でも書籍と同じディレクトリ構成になるよう、プロジェクト作成コマンドに `--no-package` オプションを追加しました。

```bash
mkdir -p chapter4
cd chapter4
uv init --no-package --python 3.14
```

```bash
uv add strands-agents==1.38.0 "strands-agents-tools[rss]==0.5.1" rich==14.3.3
uv add --dev "boto3[crt]==1.42.96"
```

## 4.4 【ハンズオン】リサーチエージェントの実行

### 4.4.1 プログラムの実行

```bash
uv run main.py
```
