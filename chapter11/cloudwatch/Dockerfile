FROM ghcr.io/astral-sh/uv:python3.14-trixie-slim

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

RUN useradd -m -u 1000 bedrock_agentcore

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY --chown=bedrock_agentcore:bedrock_agentcore . .
RUN uv sync --frozen --no-dev

USER bedrock_agentcore

# OTelのPython SDK経由でアプリを起動（自動計装を有効化）
CMD ["opentelemetry-instrument", "python", "main.py"]
