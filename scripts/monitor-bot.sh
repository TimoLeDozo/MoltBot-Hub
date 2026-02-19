#!/bin/bash
# Script de monitoring OpenClaw Bot
# Usage: bash scripts/monitor-bot.sh

echo "=== Monitoring OpenClaw Bot ==="
echo ""
echo "Date: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 1. État du conteneur
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. ÉTAT DU CONTENEUR"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
docker ps --filter "name=moltbot_hub" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || echo "⚠️  Conteneur non trouvé ou arrêté"
echo ""

# 2. Utilisation des ressources
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2. RESSOURCES (Limites: CPU 2.0 / RAM 4G)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
docker stats moltbot_hub --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}" 2>/dev/null || echo "⚠️  Impossible de récupérer les stats"
echo ""

# 3. Services actifs (Gateway, Browser, Telegram)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3. SERVICES ACTIFS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
docker logs moltbot_hub --tail 100 2>/dev/null | grep -E "gateway.*listening|Browser.*ready|Telegram.*ok" | tail -3 || echo "⚠️  Aucun log de service trouvé"
echo ""

# 4. Erreurs récentes (dernière heure)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4. ERREURS RÉCENTES (dernière heure)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
ERRORS=$(docker logs moltbot_hub --since 1h 2>&1 | grep -i "error\|critical\|fatal" | grep -v "Config invalid" | tail -5)
if [ -z "$ERRORS" ]; then
    echo "✅ Aucune erreur détectée"
else
    echo "$ERRORS"
fi
echo ""

# 5. Sessions actives
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "5. SESSIONS ACTIVES"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
SESSION_COUNT=$(docker exec moltbot_hub bash -c "ls -1 /root/.openclaw/agents/main/sessions/*.json 2>/dev/null | wc -l")
if [ "$SESSION_COUNT" -gt 0 ]; then
    echo "📊 Sessions: $SESSION_COUNT"
    docker exec moltbot_hub bash -c "ls -lh /root/.openclaw/agents/main/sessions/*.json 2>/dev/null | tail -3"
else
    echo "ℹ️  Aucune session active"
fi
echo ""

# 6. Sécurité - Vérification des permissions
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "6. VÉRIFICATION SÉCURITÉ"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
CONFIG_PRESENT=$(docker exec moltbot_hub bash -c "stat -c '%a' /root/.openclaw/openclaw.json 2>/dev/null")
if [ -n "$CONFIG_PRESENT" ]; then
    echo "✅ Config openclaw.json: présente (perm: ${CONFIG_PRESENT})"
else
    echo "⚠️  Config openclaw.json introuvable dans le conteneur"
fi

# Sandboxing intentionnellement désactivé (Docker-in-Docker impossible dans cette config)
echo "ℹ️  Sandboxing: Désactivé intentionnellement (Docker-in-Docker impossible)"
echo "✅  Isolation: no-new-privileges + cap_drop ALL + proxy Squid whitelist"
echo ""

# 7. Recommandations
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "7. RECOMMANDATIONS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Vérifier utilisation mémoire
MEM_PERCENT=$(docker stats moltbot_hub --no-stream --format "{{.MemPerc}}" 2>/dev/null | sed 's/%//')
if [ -n "$MEM_PERCENT" ]; then
    MEM_INT=$(echo "$MEM_PERCENT" | cut -d'.' -f1)
    if [ "$MEM_INT" -gt 80 ]; then
        echo "⚠️  Mémoire élevée (${MEM_PERCENT}%) - Considérer redémarrage"
    else
        echo "✅ Utilisation mémoire normale (${MEM_PERCENT}%)"
    fi
fi

# Vérifier uptime
UPTIME=$(docker inspect moltbot_hub --format='{{.State.StartedAt}}' 2>/dev/null)
if [ -n "$UPTIME" ]; then
    echo "ℹ️  Conteneur démarré: $UPTIME"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Monitoring terminé - $(date '+%H:%M:%S')"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
