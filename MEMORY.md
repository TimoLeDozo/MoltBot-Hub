# MEMORY

## 2026-02-17 Browser Tool Stability

- Keep `config/clawdbot.json` -> `browser.noSandbox: true` for Docker deployments.
- Without Chromium `--no-sandbox`, browser startup can fail silently in containerized runs and tool calls may timeout or fall back to non-browser paths.
- Keep `browser.executablePath` on `/usr/local/bin/openclaw-chromium-wrapper` so Chromium runs with `--use-system-cert-verifier` in Docker.
- With strict Squid whitelist, allow PKI infrastructure domains (for chain/OCSP fetches): `.ssl.com`, `.digicert.com`, `.letsencrypt.org`, `.identrust.com`, `.globalsign.com`.
