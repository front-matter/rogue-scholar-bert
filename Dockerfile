FROM python:3.12-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files
COPY pyproject.toml ./
RUN touch README.md

# Install dependencies to system Python
RUN --mount=type=cache,target=/root/.cache/uv \
  uv pip install --system .

# Copy application code
COPY api ./api
COPY hypercorn.toml ./

EXPOSE 5100

CMD ["hypercorn", "-b", "0.0.0.0:5100", "api:app"]
