# Scripts OpenClaw

## monitor-bot.sh

Script de monitoring du bot OpenClaw.

### Usage

```bash
bash scripts/monitor-bot.sh
```

### Verifications

1. Etat du conteneur
2. Ressources CPU/RAM
3. Services actifs (Gateway, Browser, Telegram)
4. Erreurs recentes dans les logs
5. Sessions actives
6. Points de securite

## model-truth-router.ps1

Routeur "table de verite" pour switcher dynamiquement entre Gemini, NVIDIA et Qwen selon:
- situation (`auto`, `chat`, `browser`, `analysis`, `research`, `emergency`)
- erreurs recentes (quota/rate-limit)
- budget tokens journalier
- disponibilite locale Ollama (`qwen2.5:0.5b`, `qwen2.5:7b`)

### Usage

Dry-run (aucune modification):

```powershell
powershell -ExecutionPolicy Bypass -File scripts/model-truth-router.ps1 -Situation auto
```

Appliquer la decision dans `config/clawdbot.json`:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/model-truth-router.ps1 -Situation browser -Apply
```

Appliquer + redemarrer le conteneur:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/model-truth-router.ps1 -Situation auto -Apply -RestartContainer
```

### Sortie

Rapport JSON ecrit dans:
- `workspace/output/model-routing-report.json`