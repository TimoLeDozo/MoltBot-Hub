# MEMORY

## 2026-02-17 Browser Tool Stability

- Keep `config/clawdbot.json` -> `browser.noSandbox: true` for Docker deployments.
- Without Chromium `--no-sandbox`, browser startup can fail silently in containerized runs and tool calls may timeout or fall back to non-browser paths.
- Keep `browser.executablePath` on `/usr/local/bin/openclaw-chromium-wrapper` so Chromium runs with `--use-system-cert-verifier` in Docker.
- With strict Squid whitelist, allow PKI infrastructure domains (for chain/OCSP fetches): `.ssl.com`, `.digicert.com`, `.letsencrypt.org`, `.identrust.com`, `.globalsign.com`.

## 2026-02-18 Health Check Findings

- Gemini free tier can effectively cap usage at ~20 requests/day; this is a critical service limit for bot availability.
- Browser-heavy turns can consume ~15k-19k tokens per snapshot pass, accelerating quota burn.
- Telegram reply "An unknown error occurred" is often a masked upstream model failure (quota/rate-limit/content filter), not a browser crash.
- Current OpenClaw runtime behavior shows no robust retry/backoff path for 429 bursts across provider fallback chains.
- `workspace/skills/web-search/skill.json` must point `command` to the wrapper `index.js` path, not `search.js`, to keep proxy/timeouts/error handling consistent.
