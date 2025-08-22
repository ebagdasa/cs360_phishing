# Dockerfile for Puzzle MCP Server
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install additional dependencies for HTTP/WebSocket servers
RUN pip install --no-cache-dir fastapi uvicorn websockets

# Copy application files
COPY . .

# Create a non-root user
RUN useradd -m -u 1000 puzzleuser && chown -R puzzleuser:puzzleuser /app
USER puzzleuser

# Expose ports
EXPOSE 8000 8765

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command (can be overridden)
CMD ["python", "puzzle_http_server.py", "--host", "0.0.0.0", "--port", "8000"]
