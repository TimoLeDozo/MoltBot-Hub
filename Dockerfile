FROM node:24-slim

# Installation des dépendances système pour Playwright Chromium
RUN apt-get update && apt-get install -y \
    git \
    procps \
    # Dépendances Chromium essentielles
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
    # Fonts pour rendu correct
    fonts-liberation \
    fonts-noto-color-emoji \
    && rm -rf /var/lib/apt/lists/*

# Installation d'OpenClaw (dernière version - anciennement Clawdbot/Moltbot)
RUN npm install -g openclaw@latest clawhub

# Installation de Playwright Chromium
# Désactiver le sandbox Playwright (utiliser le flag --no-sandbox via env var)
ENV PLAYWRIGHT_BROWSERS_PATH=/root/.cache/ms-playwright
RUN npx playwright@1.58.0 install chromium --with-deps

WORKDIR /app

# Lancement du bot (openclaw est compatible avec la commande clawdbot)
CMD ["openclaw", "gateway", "--port", "18789", "--bind", "lan"]
