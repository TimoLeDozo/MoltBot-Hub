# MoltBot (OpenClaw) - Documentation Projet

**Version**: OpenClaw v2026.2.9
**Derniere mise a jour**: 10 fevrier 2026
**Interface**: Telegram @TimoLeDozo_MoltBot

---

## 1. Architecture Visee

### Concept: "Les Yeux et Les Mains"

MoltBot est une interface IA multi-modale qui combine plusieurs modeles pour optimiser les couts et les capacites.

```
                           MOLTBOT
               "L'assistant IA economique"

    LES MAINS (Execution)           LES YEUX (Vision)
    ┌──────────────────────┐       ┌──────────────────┐
    │  Ollama qwen2.5:7b   │       │  Gemini 2.5      │
    │  (LOCAL, GRATUIT)     │       │  Flash           │
    │                       │       │  (gratuit/quota) │
    │  - Generation texte   │       │                  │
    │  - Code               │       │  - Analyse       │
    │  - Raisonnement       │       │    images        │
    │  - Recherche web      │       │  - OCR           │
    │  - Creation fichiers  │       │  - Screenshots   │
    └──────────────────────┘       └──────────────────┘

    NAVIGATEUR CHROMIUM (Playwright)
    ┌────────────────────────────────────────────────┐
    │  - Extraction de donnees web                   │
    │  - Capture screenshots                         │
    │  - Automatisation interfaces LLM gratuites     │
    └────────────────────────────────────────────────┘

    SKILLS & CRON
    ┌────────────────────────────────────────────────┐
    │  - ClawHub marketplace (install via clawhub)   │
    │  - Skills custom (workspace/skills/)           │
    │  - Taches planifiees (cron jobs)               │
    └────────────────────────────────────────────────┘

                  INTERFACE TELEGRAM
                 @TimoLeDozo_MoltBot
```

### Strategie Economique

| Ressource | Cout | Usage | Limite |
|-----------|------|-------|--------|
| **Ollama (Local)** | Gratuit | Texte, code, raisonnement | Illimite |
| **Gemini 2.5 Flash** | Gratuit | Vision, OCR, images | Quota Google |
| **Brave Search API** | Gratuit | Recherche web | 2000 req/mois |
| **Chromium/Playwright** | Gratuit | Web scraping, automatisation | Illimite |

---

## 2. Etat Actuel (10 Fevrier 2026)

### Ce qui FONCTIONNE

- [x] **Infrastructure Docker**
  - Conteneur `moltbot_hub` operationnel (OpenClaw v2026.2.9)
  - Conteneur `openclaw_proxy` (Squid) operationnel
  - Reseau bridge isole: 172.25.0.0/24

- [x] **Modeles IA enregistres**
  - Ollama qwen2.5:7b = modele principal (gratuit, local)
  - Gemini 2.5 Flash = fallback vision (API Google)
  - **Erreur "No API provider" RESOLUE** (champ `api` obligatoire dans chaque provider)

- [x] **Connectivite Ollama**
  - Accessible depuis le conteneur via `host.docker.internal:11434`
  - 3 modeles disponibles sur l'hote: qwen2.5:7b, phi3:mini, tinyllama
  - Requetes directes OK (generation de texte testee)

- [x] **Telegram**
  - Bot connecte et en ligne (@TimoLeDozo_MoltBot)
  - `dmPolicy: "open"` + `allowFrom: ["*"]`
  - Messages recus et traites

- [x] **Gateway WebSocket**
  - Ecoute sur `ws://0.0.0.0:18789`
  - Token authentification 256-bit
  - Dashboard accessible en local

- [x] **Securite Reseau (Proxy Squid)**
  - Whitelist de domaines stricte (telegram, google, github, brave, npm, etc.)
  - Tout domaine non liste = bloque (403)
  - Logs d'acces pour audit

- [x] **Limites Ressources**
  - CPU: 2.0 max, RAM: 4GB max
  - `no-new-privileges`, capabilities dropped
  - Logging structure (json-file, rotation)

- [x] **Chromium Playwright**
  - Installe et configure (headless, `--no-sandbox`)
  - Browser service ready (2 profiles)

- [x] **Hooks internes**
  - `session-memory` (memoire de session)
  - `boot-md` (chargement au demarrage)
  - `command-logger` (log des commandes)

- [x] **Memory system**
  - Plugin `memory-core` actif (vector ready, FTS ready)
  - Pas encore de donnees indexees (0 fichiers, 0 chunks)

- [x] **Cron jobs**
  - Infrastructure fonctionnelle
  - Job "Morning Briefing" configure (8h, actualites tech IA)

- [x] **Skills (ClawHub)**
  - CLI `clawhub` installe dans l'image Docker
  - Skills installes: `xlsx`, `duckduckgo-search`
  - Skill custom: `web-search` (workspace/skills/)

### Problemes connus (non bloquants)

- **Ollama discovery echoue** : "TypeError: fetch failed" au demarrage
  - Cause: OpenClaw tente la decouverte via 127.0.0.1 (inaccessible dans le conteneur)
  - Impact: **Cosmetique uniquement** - le modele est quand meme enregistre via la config manuelle
  - Les requetes directes via `host.docker.internal:11434` fonctionnent

- **State dir migration warning** : "target already exists (/root/.openclaw)"
  - Cause: anciens fichiers dans `/root/.clawdbot/` coexistent avec `/root/.openclaw/`
  - Impact: Cosmetique, pas d'effet fonctionnel

- **Security audit warnings** :
  - "Small models require sandboxing" - sandbox desactive (Docker-in-Docker impossible)
  - "Telegram DMs are open" - voulu (bot personnel)
  - "DMs share main session" - pas de `dmScope: "per-channel-peer"` configure

### Ce qui reste a faire

- [ ] **Tester la reponse effective du bot** : envoyer un message Telegram et verifier la reponse
- [ ] **Web Scraping** : tester navigation Chromium via commande Telegram
- [ ] **Automatisation LLM Web** : explorer ChatGPT/Claude web via Playwright
- [ ] **Enrichir la memoire** : alimenter le memory-core avec du contexte

---

## 3. Architecture de Securite

### Philosophie

MoltBot ne doit JAMAIS pouvoir:
- Acceder aux fichiers systeme de Windows
- Exfiltrer des donnees sensibles vers Internet
- Consommer toutes les ressources du PC
- Acceder a des sites non autorises

### Schema de protection

```
                     HOTE WINDOWS 11
  ┌──────────────────────────────────────────────────────┐
  │                                                      │
  │  DOCKER DESKTOP                                      │
  │  ┌──────────────────────────────────────────────┐    │
  │  │        RESEAU BRIDGE (172.25.0.0/24)         │    │
  │  │                                               │    │
  │  │  ┌──────────────┐    ┌────────────────────┐  │    │
  │  │  │  SQUID PROXY │    │     MOLTBOT        │  │    │
  │  │  │              │◄──►│                    │  │    │
  │  │  │  WHITELIST:  │    │  - 2 CPU max       │  │    │
  │  │  │  telegram    │    │  - 4GB RAM max     │  │    │
  │  │  │  google      │    │  - no-new-privs    │  │    │
  │  │  │  github      │    │  - caps dropped    │  │    │
  │  │  │  brave       │    │  - volumes montes  │  │    │
  │  │  │  npm         │    │    uniquement      │  │    │
  │  │  │  wikipedia   │    └────────────────────┘  │    │
  │  │  │  etc.        │                             │    │
  │  │  └──────────────┘                             │    │
  │  │        │                                      │    │
  │  │        ▼                                      │    │
  │  │  TOUT DOMAINE NON LISTE = BLOQUE (403)        │    │
  │  └──────────────────────────────────────────────┘    │
  │                                                      │
  │  OLLAMA (localhost:11434)                             │
  │  - Accessible via Docker bridge (host.docker.internal)│
  │  - NON expose sur Internet                           │
  │  - Modeles: qwen2.5:7b, phi3:mini, tinyllama        │
  └──────────────────────────────────────────────────────┘
```

### Couches de Protection

| Couche | Protection | Statut |
|--------|------------|--------|
| 1. Reseau | Proxy Squid + whitelist domaines | OK |
| 2. Isolation | Docker bridge reseau dedie | OK |
| 3. Ressources | Limites CPU (2) et RAM (4GB) | OK |
| 4. Privileges | no-new-privileges, capabilities dropped | OK |
| 5. Fichiers | Volumes montes uniquement (pas d'acces hote) | OK |
| 6. Auth | Token Gateway 256-bit | OK |
| 7. Sandbox | Desactive (Docker-in-Docker impossible) | N/A |

---

## 4. Configuration

### Structure du Projet

```
Moltbot-Hub/
├── config/
│   ├── clawdbot.json          # Config principale OpenClaw
│   └── cron/
│       └── jobs.json          # Taches planifiees
├── workspace/
│   ├── output/                # Fichiers generes par le bot
│   └── skills/                # Skills (custom + ClawHub)
│       ├── web-search/        # Skill custom recherche web
│       ├── xlsx/              # ClawHub: manipulation Excel
│       └── duckduckgo-search/ # ClawHub: recherche DDG
├── squid.conf                 # Whitelist proxy Squid
├── docker-compose.yml         # Config Docker principale
├── docker-compose.override.yml # Config Squid + reseau
├── Dockerfile                 # Image Node 24 + OpenClaw + Playwright
├── .env                       # Tokens (TELEGRAM_TOKEN, GOOGLE_API_KEY)
└── CLAUDE.md                  # Cette documentation
```

### Mapping des chemins (hote -> conteneur)

| Hote | Conteneur | Usage |
|------|-----------|-------|
| `./config/clawdbot.json` | `/root/.openclaw/openclaw.json` | Config principale |
| `./config/cron/` | `/root/.openclaw/cron/` | Cron jobs |
| `./workspace/skills/` | `/app/skills/` | Skills ClawHub |
| `./workspace/` | `/app/workspace/` | Fichiers de travail |

### Config OpenClaw (points cles)

Chaque provider DOIT avoir un champ `api`. Valeurs possibles:
- `openai-completions` (Ollama, OpenAI)
- `google-generative-ai` (Google/Gemini)
- `anthropic-messages`, `azure-openai-responses`, etc.

Si un provider n'a pas de champ `api`, TOUS les modeles deviennent "missing".

### Format Cron Job (v2026.2.9)

```json
{
  "id": "job-id",
  "name": "Job Name",
  "enabled": true,
  "schedule": { "kind": "cron", "expr": "0 8 * * *" },
  "sessionTarget": "isolated",
  "payload": { "kind": "agentTurn", "message": "description de la tache" },
  "delivery": { "mode": "announce", "channel": "last" },
  "state": {}
}
```

---

## 5. Commandes Utiles

### Gestion Docker

```bash
docker compose up -d                    # Demarrer
docker logs moltbot_hub -f --tail 50    # Logs temps reel
docker restart moltbot_hub              # Redemarrer
docker exec moltbot_hub openclaw status # Status complet
docker exec moltbot_hub openclaw doctor # Diagnostic
docker exec moltbot_hub openclaw models list  # Modeles
```

### Gestion Ollama (Hote Windows)

```bash
start "" "C:\Users\timca\AppData\Local\Programs\Ollama\ollama.exe" serve
tasklist | findstr ollama
ollama list
```

### Tests de Connectivite

```bash
# Test Ollama depuis conteneur
docker exec moltbot_hub node -e "fetch('http://host.docker.internal:11434/api/tags').then(r=>r.json()).then(d=>console.log(JSON.stringify(d,null,2)))"

# Test generation
docker exec moltbot_hub node -e "fetch('http://host.docker.internal:11434/api/generate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({model:'qwen2.5:7b',prompt:'Bonjour',stream:false})}).then(r=>r.json()).then(d=>console.log(d.response))"
```

### Proxy Squid

```bash
docker logs openclaw_proxy | tail -20           # Logs
docker logs openclaw_proxy | grep "DENIED"      # Domaines bloques
# Ajouter un domaine: editer squid.conf puis docker restart openclaw_proxy
```

---

## 6. Historique des Problemes

| Date | Probleme | Cause | Solution |
|------|----------|-------|----------|
| 31/01 | Ollama non accessible | Service non demarre + env var manquante | Demarrer Ollama + OLLAMA_API_KEY |
| 01/02 | Gateway inaccessible | Config incorrecte | bind=lan, mode=local, token fort |
| 01-02/02 | Bot ne repond pas (Pairing) | dmPolicy="pairing" | dmPolicy="open" + allowFrom=["*"] |
| 02/02 | Crash spawn docker | Sandbox mode="all" | Supprimer section sandbox |
| 02-09/02 | "No API provider registered" | Champ `api` manquant dans providers | Ajouter `"api": "openai-completions"` etc. |
| 09/02 | doctor --fix echoue | Bind mount = EBUSY rename | Corriger les fichiers manuellement |

---

## 7. Directives d'Autonomie (pour Claude)

### Permissions

- [x] Executer commandes docker, docker-compose
- [x] Modifier fichiers config/*.json et docker-compose.yml
- [x] Utiliser flags non-interactifs (-y, --fix)
- [x] Diagnostiquer et corriger erreurs automatiquement

### Interdictions

- [ ] NE PAS supprimer volumes Docker (`docker-compose down -v`)
- [ ] NE PAS modifier fichiers systeme Windows hors projet
- [ ] NE PAS executer commandes destructives sans confirmation
- [ ] NE PAS supprimer les couches de securite (proxy, limits, caps)

### En cas d'echec apres 3 tentatives

Consigner l'erreur dans `LOG_ERREUR.txt` et arreter.
