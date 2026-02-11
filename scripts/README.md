# Scripts de Monitoring OpenClaw

## monitor-bot.sh

Script de monitoring complet du bot OpenClaw.

### Usage

```bash
bash scripts/monitor-bot.sh
```

### Ce qu'il vérifie

1. **État du conteneur** - Vérifie que le conteneur est actif
2. **Ressources** - CPU et RAM (limites: 2 CPU / 4G RAM)
3. **Services actifs** - Gateway, Browser, Telegram
4. **Erreurs récentes** - Logs de la dernière heure
5. **Sessions actives** - Nombre de sessions en cours
6. **Sécurité** - Permissions, sandboxing
7. **Recommandations** - Alertes si problème détecté

### Automatisation (Optionnel)

Pour exécuter le monitoring toutes les 5 minutes, utiliser le Task Scheduler Windows :

1. Ouvrir Task Scheduler
2. Créer une tâche de base
3. Déclencheur : Toutes les 5 minutes
4. Action : Démarrer un programme
5. Programme : `C:\Program Files\Git\bin\bash.exe`
6. Arguments : `scripts/monitor-bot.sh`
7. Répertoire : `c:\Users\timca\OneDrive\Documents\Moltbot-Hub`

### Output

Le script affiche un rapport complet avec des indicateurs visuels :
- ✅ OK
- ⚠️  Avertissement
- ℹ️  Information
