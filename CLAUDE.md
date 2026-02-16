# MoltBot (OpenClaw) - Documentation Projet

**Version**: OpenClaw v2026.2.9
**Derniere mise a jour**: 16 fevrier 2026
**Interface**: Telegram @TimoLeDozo_MoltBot

---

## 1. Architecture Visee

### Concept: "Les Yeux et Les Mains"

MoltBot est une interface IA multi-modale qui combine plusieurs modeles pour optimiser les couts et les capacites.

```
                           MOLTBOT
               "L'assistant IA economique"

    CERVEAU PRINCIPAL              FALLBACKS
    â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”       â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
    â”‚  Gemini 2.5 Flash    â”‚       â”‚  Ollama           â”‚
    â”‚  (Google API)         â”‚       â”‚  qwen2.5:0.5b    â”‚
    â”‚                       â”‚       â”‚  (LOCAL, CPU)     â”‚
    â”‚  - Generation texte   â”‚       â”‚                  â”‚
    â”‚  - Code + raisonnementâ”‚       â”‚  NVIDIA           â”‚
    â”‚  - Vision, OCR        â”‚       â”‚  Kimi K2.5       â”‚
    â”‚  - Recherche web      â”‚       â”‚  (NIM API)       â”‚
    â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜       â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜

    NAVIGATEUR CHROMIUM (Playwright)
    â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
    â”‚  - Extraction de donnees web                   â”‚
    â”‚  - Capture screenshots                         â”‚
    â”‚  - Automatisation interfaces LLM gratuites     â”‚
    â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜

    SKILLS & CRON
    â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
    â”‚  - ClawHub marketplace (install via clawhub)   â”‚
    â”‚  - Skills custom (workspace/skills/)           â”‚
    â”‚  - Taches planifiees (cron jobs)               â”‚
    â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜

                  INTERFACE TELEGRAM
                 @TimoLeDozo_MoltBot
```

### Strategie Economique

| Ressource | Cout | Usage | Limite |
|-----------|------|-------|--------|
| **Gemini 2.5 Flash** | Gratuit | Modele principal (texte, vision, code) | Quota Google AI Studio |
| **Ollama qwen2.5:0.5b** | Gratuit | Fallback local CPU | Illimite (lent) |
| **NVIDIA Kimi K2.5** | Gratuit | Fallback cloud | Quota NIM |
| **Brave Search API** | Gratuit | Recherche web | 2000 req/mois |
| **Chromium/Playwright** | Gratuit | Web scraping, automatisation | Illimite |

---

## 2. Etat Actuel (16 Fevrier 2026)

### Architecture Modeles (mise a jour 16/02)

```
Priorite 1: google/gemini-2.5-flash     (API Google, gratuit/quota)
Priorite 2: ollama/qwen2.5:0.5b         (local, CPU-only fallback)
Priorite 3: nvidia/moonshotai/kimi-k2.5  (NVIDIA NIM, gratuit)
```

**Changements depuis le 11/02:**
- Modele Ollama downgrade: `qwen2.5:7b` -> `qwen2.5:0.5b` (7b inutilisable sur CPU)
- Provider NVIDIA ajoute (Kimi K2.5 via `integrate.api.nvidia.com`)
- Gemini 2.5 Flash est le modele principal effectif

### Ce qui FONCTIONNE

- [x] **Infrastructure Docker**
  - Conteneur `moltbot_hub` UP (OpenClaw v2026.2.9)
  - Conteneur `openclaw_proxy` (Squid) UP
  - Reseau bridge isole: 172.25.0.0/24

- [x] **3 providers IA enregistres**
  - Google Gemini 2.5 Flash = modele principal
  - Ollama qwen2.5:0.5b = fallback local
  - NVIDIA Kimi K2.5 = fallback cloud
  - **Erreur "No API provider" RESOLUE** (champ `api` obligatoire dans chaque provider)

- [x] **Telegram**
  - Bot connecte et en ligne (@TimoLeDozo_MoltBot)
  - `dmPolicy: "open"` + `allowFrom: ["*"]`
  - Messages recus et traites

- [x] **Gateway WebSocket**
  - Ecoute sur `ws://0.0.0.0:18789`
  - Token authentification 256-bit
  - Dashboard accessible en local

- [x] **Securite Reseau (Proxy Squid)**
  - Whitelist de domaines stricte (telegram, google, github, brave, npm, nvidia, etc.)
  - Tout domaine non liste = bloque (403)
  - `forwarded_for off` + `via off` (pas de fuite IP)

- [x] **Limites Ressources**
  - CPU: 2.0 max, RAM: 4GB max
  - `no-new-privileges`, capabilities dropped
  - Logging structure (json-file, rotation)

- [x] **Chromium Playwright**
  - Installe et configure (headless, `--no-sandbox`)
  - Browser service ready (2 profiles)

- [x] **Hooks internes**
  - `session-memory`, `boot-md`, `command-logger`

- [x] **Cron jobs (2 jobs)**
  - `morning-briefing` : 8h quotidien, actualites tech IA
  - `heartbeat-12h` : toutes les 12h, status system

- [x] **Skills**
  - Built-in: `healthcheck`, `skill-creator`
  - Custom: `web-search` (Brave API via proxy undici)

### Problemes ACTIFS (16 Fevrier 2026)

- **BLOQUANT: Gemini retourne "billing error / rate_limit"**
  - Le bot ne peut plus repondre aux messages Telegram
  - Cascade echoue: Gemini (rate_limit) -> Ollama (billing error) -> NVIDIA (timeout)
  - Cause probable: quota Google AI Studio epuise ou cle invalide
  - A verifier: dashboard Google AI Studio

- **BLOQUANT: Cron "Morning Briefing" en erreur (3 echecs consecutifs)**
  - Erreur: `FailoverError: No API key found for provider "anthropic"`
  - Les sessions cron isolees ne trouvent pas les providers configures
  - L'agent cron semble chercher "anthropic" comme provider par defaut

- **Ollama discovery echoue** : "TypeError: fetch failed" au demarrage (cosmetique)

- **Ollama fallback retourne "billing error"** au lieu de fonctionner
  - Bizarre pour un modele local - le modele `qwen2.5:0.5b` est peut-etre absent de l'hote

### Ce qui reste a faire

- [ ] **URGENT: Resoudre l'erreur billing Gemini** (bot muet actuellement)
- [ ] **Corriger le cron Morning Briefing** (erreur anthropic provider)
- [ ] **Verifier que qwen2.5:0.5b existe sur l'hote Ollama** (`ollama list`)
- [ ] **Nettoyer les cles API en clair** dans `models.json` et `test_nvidia.sh`
- [ ] **Web Scraping** : tester navigation Chromium via commande Telegram
- [ ] **Enrichir la memoire** : alimenter le memory-core avec du contexte
- [ ] **Mettre a jour OpenClaw** : v2026.2.9 -> v2026.2.15

---

## 2b. Audit du 11 Fevrier 2026

### Failles trouvees et corrigees

| # | Faille | Severite | Fichier | Correctif applique |
|---|--------|----------|---------|-------------------|
| 1 | Cle API Brave en dur dans le code source | CRITIQUE | `workspace/skills/web-search/search.js:5`, `search.sh:6` | Remplace par `process.env.BRAVE_API_KEY` / `${BRAVE_API_KEY}` |
| 2 | Injection de commande via query non echappee | CRITIQUE | `workspace/skills/web-search/index.js:14` | Utilise `JSON.stringify(query)` au lieu de `"${query}"` |
| 3 | Cle API Brave en clair dans docker-compose.yml | HAUTE | `docker-compose.yml:17` | Deplace dans `.env`, reference via `${BRAVE_API_KEY}` |
| 4 | Volume legacy `./config:/root/.clawdbot` | MOYENNE | `docker-compose.yml:6` | Supprime (causait le warning de migration) |
| 5 | `ipc: host` expose l'espace IPC de l'hote | HAUTE | `docker-compose.yml:29` | Remplace par `shm_size: '512m'` |
| 6 | Ollama baseUrl sans `/v1` | MOYENNE | `config/clawdbot.json:10` | Corrige en `http://host.docker.internal:11434/v1` |
| 7 | DuckDuckGo absent de la whitelist Squid | MOYENNE | `squid.conf` | Ajoute `.duckduckgo.com` |
| 8 | Headers proxy exposent IP interne | BASSE | `squid.conf:63-64` | `forwarded_for off` + `via off` |
| 9 | IDENTITY.md et USER.md vides (bootstrap incomplet) | MOYENNE | `config/sandboxes/` | Remplis avec profil MoltBot + utilisateur Timo |
| 10 | BOOTSTRAP.md encore present (agent tente re-bootstrap) | BASSE | `config/sandboxes/` | Supprime |
| 11 | SOUL.md profil generique ("Soy Jack") | BASSE | `config/sandboxes/` | Remplace par profil "Expert Automation 10X" |
| 12 | Sandboxes non montees dans le conteneur | HAUTE | `docker-compose.yml` | Ajoute volume `./config/sandboxes:/root/.openclaw/agents` |

### Failles connues non corrigees (acceptees)

| Faille | Raison |
|--------|--------|
| Telegram DMs ouverts a tous | Voulu (bot personnel, un seul utilisateur) |
| DMs partagent la session principale | Acceptable (un seul utilisateur) |
| Sandbox desactive | Docker-in-Docker impossible dans cette config |
| Config chmod 777 dans conteneur | Cause par bind mount Windows, pas corrigeable sans changer l'OS |
| Ollama discovery echoue au demarrage | Cosmetique, le modele est enregistre manuellement |

### Comparaison avec projets similaires

Apres recherche (Open WebUI, LibreChat, LobeChat), l'architecture MoltBot est solide :

| Aspect | MoltBot | Open WebUI | LibreChat |
|--------|---------|------------|-----------|
| Proxy sortant (whitelist) | Squid | Non | Non |
| Isolation Docker | Oui + caps dropped | Oui basique | Oui basique |
| Limites ressources | CPU+RAM | Non | Non |
| Multi-modeles | Ollama + Gemini | Ollama multi-provider | Multi-provider |
| Telegram natif | Oui | Non | Non |
| Cron jobs | Oui | Non | Non |
| Web scraping | Playwright | Non | Non |

**Avantages MoltBot** : proxy Squid (unique), isolation poussee, cron natif, Telegram natif.
**A ameliorer** : enrichir la memoire (memory-core vide), tester le pipeline de reponse Telegram end-to-end.

---

## 2c. Audit du 16 Fevrier 2026

### Problemes trouves

| # | Probleme | Severite | Fichier | Detail |
|---|----------|----------|---------|--------|
| 1 | Cle API Google en clair dans fichier git-tracked | CRITIQUE | `config/sandboxes/main/agent/models.json:28` | `"apiKey": "<REDACTED>"` en dur (doit etre `${GOOGLE_AI_STUDIO_KEY}`) |
| 2 | Cle API NVIDIA en clair dans fichier git-tracked | CRITIQUE | `config/sandboxes/main/agent/models.json:51` | `"apiKey": "<REDACTED>"` en dur (doit etre `${NVIDIA_API_KEY}`) |
| 3 | Cle API NVIDIA en clair dans script de test | HAUTE | `test_nvidia.sh:24` | `Authorization: Bearer <REDACTED>` hardcode |
| 4 | Gemini retourne billing/rate_limit error | BLOQUANT | Logs runtime | Bot muet - cascade complete echoue sur les 3 providers |
| 5 | Cron Morning Briefing cherche provider "anthropic" | BLOQUANT | `config/cron/jobs.json` state | Sessions cron isolees ne resolvent pas les providers de la config principale |
| 6 | Ollama retourne "billing error" au lieu de repondre | HAUTE | Logs runtime | Le modele `qwen2.5:0.5b` n'est probablement pas installe sur l'hote |
| 7 | Volume `C:/Users/timca/AppData/Local` monte en entier | HAUTE | `docker-compose.yml:19` | Expose tout AppData/Local (credentials navigateurs, tokens apps, etc.) dans le conteneur |
| 8 | `NODE_TLS_REJECT_UNAUTHORIZED=0` desactive TLS | MOYENNE | `docker-compose.yml:34`, `override:22` | Vulnerable aux attaques MITM (necessaire pour proxy Squid?) |
| 9 | Variables d'env dupliquees entre compose et override | MOYENNE | `docker-compose.yml` + `override.yml` | HTTP_PROXY, HTTPS_PROXY, NO_PROXY definis 2 fois |
| 10 | SOUL.md duplique avec divergences | MOYENNE | `sandboxes/agent-main-*/SOUL.md` vs `sandboxes/main/SOUL.md` | Version `main/` a des instructions Windows paths en plus |
| 11 | Caracteres corrompus (mojibake) dans SOUL.md | MOYENNE | `SOUL.md:22`, `TRAVEL_LOG.md` | "A chaque fois" -> "ï¿½ chaque fois" (encodage Latin-1 au lieu d'UTF-8) |
| 12 | Timeout message inconsistant dans index.js | BASSE | `workspace/skills/web-search/index.js:26` | Timeout = 45s mais message dit "60 seconds" |
| 13 | `memory/main.sqlite` supprime | BASSE | `config/memory/main.sqlite` | Base memoire supprimee (git status: ` D`) |
| 14 | OpenClaw outdated v2026.2.9 | BASSE | Logs | v2026.2.15 disponible (6 versions de retard) |
| 15 | `payload.sh` est du PowerShell | BASSE | `payload.sh` | Extension `.sh` mais contient `$json`, `Out-File` (PowerShell) |
| 16 | TRAVEL_LOG.md quasi vide | BASSE | `workspace/TRAVEL_LOG.md` | Aucune entree malgre instructions dans SOUL.md |
| 17 | `jobs.json.bak` identique a `jobs.json` | BASSE | `config/cron/jobs.json.bak` | Backup inutile (copie exacte) |

### Priorites de correction

**Immediat (bot casse):**
1. Verifier quota Google AI Studio et regenerer la cle si necessaire
2. Installer `qwen2.5:0.5b` sur l'hote Ollama pour que le fallback fonctionne
3. Corriger le cron Morning Briefing (probleme resolution provider "anthropic")

**Securite (avant tout commit git):**
4. Supprimer les cles API en dur de `models.json` (utiliser des variables d'env)
5. Supprimer ou gitignore `test_nvidia.sh` (cle NVIDIA en clair)
6. Restreindre le volume AppData/Local au strict minimum necessaire

**Ameliorations:**
7. Corriger l'encodage UTF-8 des fichiers SOUL.md et TRAVEL_LOG.md
8. Unifier les SOUL.md (garder une seule version)
9. Mettre a jour OpenClaw v2026.2.9 -> v2026.2.15
10. Corriger le message timeout dans index.js (dire 45s, pas 60s)

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
  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
  â”‚                                                      â”‚
  â”‚  DOCKER DESKTOP                                      â”‚
  â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”    â”‚
  â”‚  â”‚        RESEAU BRIDGE (172.25.0.0/24)         â”‚    â”‚
  â”‚  â”‚                                               â”‚    â”‚
  â”‚  â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”    â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”‚    â”‚
  â”‚  â”‚  â”‚  SQUID PROXY â”‚    â”‚     MOLTBOT        â”‚  â”‚    â”‚
  â”‚  â”‚  â”‚              â”‚â—„â”€â”€â–ºâ”‚                    â”‚  â”‚    â”‚
  â”‚  â”‚  â”‚  WHITELIST:  â”‚    â”‚  - 2 CPU max       â”‚  â”‚    â”‚
  â”‚  â”‚  â”‚  telegram    â”‚    â”‚  - 4GB RAM max     â”‚  â”‚    â”‚
  â”‚  â”‚  â”‚  google      â”‚    â”‚  - no-new-privs    â”‚  â”‚    â”‚
  â”‚  â”‚  â”‚  github      â”‚    â”‚  - caps dropped    â”‚  â”‚    â”‚
  â”‚  â”‚  â”‚  brave       â”‚    â”‚  - volumes montes  â”‚  â”‚    â”‚
  â”‚  â”‚  â”‚  npm         â”‚    â”‚    uniquement      â”‚  â”‚    â”‚
  â”‚  â”‚  â”‚  wikipedia   â”‚    â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â”‚    â”‚
  â”‚  â”‚  â”‚  etc.        â”‚                             â”‚    â”‚
  â”‚  â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜                             â”‚    â”‚
  â”‚  â”‚        â”‚                                      â”‚    â”‚
  â”‚  â”‚        â–¼                                      â”‚    â”‚
  â”‚  â”‚  TOUT DOMAINE NON LISTE = BLOQUE (403)        â”‚    â”‚
  â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜    â”‚
  â”‚                                                      â”‚
  â”‚  OLLAMA (localhost:11434)                             â”‚
  â”‚  - Accessible via Docker bridge (host.docker.internal)â”‚
  â”‚  - NON expose sur Internet                           â”‚
  â”‚  - Modeles: qwen2.5:7b, phi3:mini, tinyllama        â”‚
  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

### Couches de Protection

| Couche | Protection | Statut |
|--------|------------|--------|
| 1. Reseau | Proxy Squid + whitelist domaines | OK |
| 2. Isolation | Docker bridge reseau dedie | OK |
| 3. Ressources | Limites CPU (2) et RAM (4GB) | OK |
| 4. Privileges | no-new-privileges, capabilities dropped | OK |
| 5. Fichiers | Volumes montes uniquement (pas d'acces hote) | **ATTENTION** (AppData/Local monte) |
| 6. Auth | Token Gateway 256-bit | OK |
| 7. Sandbox | Desactive (Docker-in-Docker impossible) | N/A |

---

## 4. Configuration

### Structure du Projet

```
Moltbot-Hub/
â”œâ”€â”€ config/
â”‚   â”œâ”€â”€ clawdbot.json          # Config principale OpenClaw (3 providers)
â”‚   â”œâ”€â”€ cron/
â”‚   â”‚   â”œâ”€â”€ jobs.json          # 2 cron jobs (morning-briefing, heartbeat-12h)
â”‚   â”‚   â””â”€â”€ runs/              # Logs d'execution des cron jobs
â”‚   â””â”€â”€ sandboxes/
â”‚       â”œâ”€â”€ agent-main-0d71ad7a/  # Agent legacy (SOUL.md, IDENTITY.md, USER.md)
â”‚       â””â”€â”€ main/              # Agent actif
â”‚           â”œâ”€â”€ SOUL.md        # Personnalite + protocoles
â”‚           â”œâ”€â”€ TOOLS.md       # Notes outils Windows
â”‚           â”œâ”€â”€ agent/         # models.json, auth-profiles
â”‚           â””â”€â”€ sessions/      # Sessions actives
â”œâ”€â”€ workspace/
â”‚   â”œâ”€â”€ output/                # Fichiers generes par le bot
â”‚   â”œâ”€â”€ TRAVEL_LOG.md          # Journal des actions (quasi vide)
â”‚   â””â”€â”€ skills/
â”‚       â””â”€â”€ web-search/        # Skill custom Brave Search API
â”‚           â”œâ”€â”€ index.js       # Entry point (execSync wrapper)
â”‚           â”œâ”€â”€ search.js      # Brave API fetch via undici proxy
â”‚           â”œâ”€â”€ search.sh      # Version bash (curl)
â”‚           â””â”€â”€ skill.json     # Metadata skill
â”œâ”€â”€ squid.conf                 # Whitelist proxy Squid
â”œâ”€â”€ docker-compose.yml         # Config Docker principale
â”œâ”€â”€ docker-compose.override.yml # Config Squid + reseau bridge
â”œâ”€â”€ Dockerfile                 # Image Node 24 + OpenClaw + Playwright
â”œâ”€â”€ .env                       # Tokens (TELEGRAM, GOOGLE, NVIDIA, BRAVE)
â””â”€â”€ CLAUDE.md                  # Cette documentation
```

### Mapping des chemins (hote -> conteneur)

| Hote | Conteneur | Usage |
|------|-----------|-------|
| `./config/clawdbot.json` | `/root/.openclaw/openclaw.json` | Config principale |
| `./config/cron/` | `/root/.openclaw/cron/` | Cron jobs |
| `./config/sandboxes/` | `/root/.openclaw/agents/` | Profils agent (SOUL.md, etc.) |
| `./config/sandboxes/main/SOUL.md` | `/root/.openclaw/workspace/SOUL.md` | Personnalite agent |
| `./config/sandboxes/main/TOOLS.md` | `/root/.openclaw/workspace/TOOLS.md` | Notes outils |
| `./workspace/skills/` | `/app/skills/` | Skills ClawHub |
| `./workspace/` | `/app/workspace/` | Fichiers de travail |
| `C:/Users/timca/AppData/Local` | `/host/windows/local-appdata` | **Acces Windows** (cleanup disk) |

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
| 11/02 | Audit complet : 12 failles | Cles en dur, injection, IPC host, volumes legacy | Voir section 2b |
| 12/02 | Ollama inutilisable sur CPU | qwen2.5:7b trop lourd, modeles legers hallucinent | Switch vers Gemini 2.5 Flash comme modele principal |
| 12/02 | Ajout provider NVIDIA | Kimi K2.5 gratuit via NIM | 3eme fallback apres Gemini et Ollama |
| 16/02 | Bot muet (billing error) | Quota Gemini epuise + Ollama fallback KO | Voir section 2c |
| 16/02 | Audit code : 17 problemes | Cles en clair, volume AppData, cron casse, encodage | Voir section 2c |

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
