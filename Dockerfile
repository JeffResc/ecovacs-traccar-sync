# Build stage
FROM python:3.13-slim AS builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.11.17 /uv /usr/local/bin/uv

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
FROM gcr.io/distroless/python3-debian13@sha256:0e300647f5a9d51fb686e9167c97248e0419cd6e5186efc50b642748aab8d8be

# Set working directory
WORKDIR /app

# Copy the virtual environment from builder
COPY --from=builder /app/.venv/lib/python3.13/site-packages /app/site-packages

# Copy application code
COPY --from=builder /app/main.py /app/traccar_client.py ./

# Set Python path to include our site-packages
ENV PYTHONPATH=/app/site-packages

# Run the application
ENTRYPOINT ["/usr/bin/python3"]
CMD ["/app/main.py"]
