# Build stage
FROM python:3.13-slim AS builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.8.23 /uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

# Install git and build tools
RUN apt-get update && apt-get install -y git build-essential && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies to a virtual environment
RUN uv sync --frozen --no-dev

# Copy application code
COPY main.py traccar_client.py ./

# Final stage
FROM gcr.io/distroless/python3-debian12@sha256:d6e8de85caaf94601d4391ee94fb299c059789eafc8a54d5f232c8ccc6e9603b

# Set working directory
WORKDIR /app

# Copy the virtual environment from builder
COPY --from=builder /app/.venv/lib/python3.13/site-packages /app/site-packages

# Copy application code
COPY --from=builder /app/main.py /app/traccar_client.py ./

# Set Python path to include our site-packages
ENV PYTHONPATH=/app/site-packages

# Run the application
CMD ["/app/main.py"]
