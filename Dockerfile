FROM node:24-slim

# Install system dependencies for Playwright Chromium
RUN apt-get update && apt-get install -y \
    ca-certificates \
    git \
    procps \
    python3 \
    python3-pip \
    # Essential Chromium dependencies
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    libatspi2.0-0 \
    # Fonts for rendering
    fonts-liberation \
    fonts-noto-color-emoji \
    && rm -rf /var/lib/apt/lists/*

COPY workspace/skills/google-doc-sync/requirements.txt /tmp/google-doc-sync-requirements.txt
RUN pip3 install --break-system-packages --no-cache-dir -r /tmp/google-doc-sync-requirements.txt

# Install OpenClaw (latest version)
RUN npm install -g openclaw@2026.2.15 clawhub

# Install Playwright Chromium
# Disable Playwright sandbox (use --no-sandbox via env var)
ENV PLAYWRIGHT_BROWSERS_PATH=/root/.cache/ms-playwright
RUN npx playwright@1.58.0 install chromium --with-deps
RUN cat <<'EOF' > /usr/local/bin/openclaw-chromium-wrapper \
 && chmod +x /usr/local/bin/openclaw-chromium-wrapper
#!/bin/sh
set -eu
CHROME_BIN="${OPENCLAW_CHROMIUM_BIN:-/root/.cache/ms-playwright/chromium-1208/chrome-linux64/chrome}"
exec "$CHROME_BIN" --use-system-cert-verifier "$@"
EOF

WORKDIR /app

# Start the bot (openclaw is compatible with clawdbot command)
CMD ["openclaw", "gateway", "--port", "18789", "--bind", "lan"]
