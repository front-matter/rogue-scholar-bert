FROM python:3.13-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Install dependencies
RUN uv pip install --system --no-cache \
  transformers torch flask gunicorn

# Copy application code
COPY inference.py /app/inference.py

# Expose port for HTTP API
EXPOSE 6000

# Command to run the app
CMD ["gunicorn", "--bind", "0.0.0.0:6000", "--workers", "4", "--timeout", "120", "inference:app"]