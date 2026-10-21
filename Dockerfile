# syntax=docker/dockerfile:1
ARG PYTHON_VERSION=3.13
FROM ghcr.io/astral-sh/uv:python${PYTHON_VERSION}-bookworm-slim AS build
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev
COPY agent ./agent
RUN uv run --no-sync python -m livekit.agents download-files

FROM ghcr.io/astral-sh/uv:python${PYTHON_VERSION}-bookworm-slim
ENV PYTHONUNBUFFERED=1
ARG UID=10001
RUN adduser --disabled-password --gecos "" --home /app --shell /sbin/nologin --uid ${UID} appuser
COPY --from=build --chown=appuser:appuser /app /app
WORKDIR /app
USER appuser
CMD ["uv", "run", "--no-sync", "python", "-m", "agent.agent", "start"]
