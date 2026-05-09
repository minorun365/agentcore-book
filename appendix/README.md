# 付録 ハンズオン環境のセットアップ

本書のハンズオンを実施する際の事前準備として、書籍に掲載されているコマンドをコピペしやすい形で掲載しています。

付録1（AWSアカウントの準備）と付録3（Bedrockのサービスクォータ）はマネジメントコンソール上の操作のみで、CLIコマンドは含まれません。本READMEには付録2「開発環境の構築」の中で登場するコマンドをまとめています。

## 付録2 【ハンズオン】開発環境の構築

### 付録2.3 コードスペースの初期設定

#### uvのインストール

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

```bash
uv --version
```

#### AWS CLIのインストール

```bash
# ダウンロード
curl -o "awscliv2.zip" https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip

# 解凍
unzip awscliv2.zip

# インストール
sudo ./aws/install
```

```bash
aws --version

# 不要なファイルを削除
rm -rf aws awscliv2.zip
```

#### AWS認証の設定

```bash
aws login --remote
```

```bash
aws sts get-caller-identity
```

### 付録2.4 作成済みコードスペースへのアクセス

#### AWS認証の再設定

```bash
aws logout
aws login --remote
```
