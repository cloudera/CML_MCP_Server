# Simple, fast Dockerfile using UV
FROM python:3.12-slim

# Build argument for Cloudera AI Workbench host URL
ARG CAI_WORKBENCH_HOST
# Persist as runtime env var so the server can read it at container start
ENV CAI_WORKBENCH_HOST=${CAI_WORKBENCH_HOST}

# Install system dependencies and UV
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && curl -LsSf https://astral.sh/uv/install.sh | sh \
    && mv /root/.local/bin/uv /usr/local/bin/uv \
    && mv /root/.local/bin/uvx /usr/local/bin/uvx

# Create non-root user (cai for Cloudera AI)
RUN groupadd -r cai && useradd -r -g cai cai

# Set working directory
WORKDIR /app

# Copy project files
COPY --chown=cai:cai pyproject.toml uv.lock ./
COPY --chown=cai:cai cai_workbench_mcp_server/ ./cai_workbench_mcp_server/

# Install dependencies with UV (much faster than pip!)
RUN uv sync --frozen

# Install Cloudera AI Workbench API (cmlapi - required for upload_folder)
# Extract domain from CAI_WORKBENCH_HOST (strip https:// and trailing /)
RUN if [ -n "${CAI_WORKBENCH_HOST}" ]; then \
        WORKBENCH_DOMAIN=$(echo "${CAI_WORKBENCH_HOST}" | sed 's|https\?://||' | sed 's|/$||'); \
        echo "Installing cmlapi from https://${WORKBENCH_DOMAIN}/api/v2/python.tar.gz"; \
        uv pip install --allow-insecure-host ${WORKBENCH_DOMAIN} https://${WORKBENCH_DOMAIN}/api/v2/python.tar.gz; \
    else \
        echo "Warning: CAI_WORKBENCH_HOST not provided, skipping cmlapi installation"; \
    fi

# Switch to non-root user
USER cai

# Activate UV environment
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Expose port for HTTP mode
EXPOSE 8080

# Default to stdio mode (like Terraform MCP server)
CMD ["python", "-m", "cai_workbench_mcp_server.stdio_server"]