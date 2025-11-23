FROM python:3.12-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files
COPY pyproject.toml ./
RUN touch README.md

# Install dependencies only (not the project itself yet)
RUN --mount=type=cache,target=/root/.cache/uv \
  uv pip install --system --no-deps transformers torch hypercorn Quart python-dotenv quart-schema quart-cors quart-rate-limiter

# Copy application code
COPY api ./api
COPY hypercorn.toml ./

# Install the project
RUN uv pip install --system --no-deps -e .

EXPOSE 5100

CMD ["uv", "run", "start"]
