FROM ghcr.io/astral-sh/uv:python3.14-trixie-slim
WORKDIR /app

ENV UV_SYSTEM_PYTHON=1 \
    PYTHONUNBUFFERED=1

# 依存パッケージをインストール
COPY pyproject.toml ./
RUN uv pip install .

# 非rootユーザーを作成
RUN useradd -m -u 1000 bedrock_agentcore

EXPOSE 8080

# プロジェクト全体をコピー
COPY --chown=bedrock_agentcore:bedrock_agentcore . .

USER bedrock_agentcore

CMD ["python", "-m", "src.agent"]
