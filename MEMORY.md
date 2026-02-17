# MEMORY

## 2026-02-17 Browser Tool Stability

- Keep `config/clawdbot.json` -> `browser.noSandbox: true` for Docker deployments.
- Without Chromium `--no-sandbox`, browser startup can fail silently in containerized runs and tool calls may timeout or fall back to non-browser paths.
