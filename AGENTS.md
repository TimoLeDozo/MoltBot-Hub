# Contexte public pour les agents

Ce fichier est lu par Codex et par tout agent compatible AGENTS.md. Claude lit CLAUDE.md, Gemini et
Antigravity lisent GEMINI.md : les trois disent la même chose.

MoltBot-Hub est une vitrine. Elle documente une architecture et une ambition. Elle ne reçoit jamais de
copie du système exploité.

## Règles

- Aucun secret, jeton, cookie, fichier `.env` ou identifiant.
- Aucune adresse IP, topologie réelle, commande d'accès ou nom de machine.
- Aucun journal d'exécution ni inventaire matériel.
- Les schémas restent conceptuels et les affirmations restent vérifiables.
- Une ambition se présente comme une ambition, pas comme une capacité déjà prouvée.
- Écriture : phrases courtes, aucun tiret cadratin, aucun point-virgule.

## Qui fait quoi

| IA | Rôle | Ce qu'elle ne fait pas |
|---|---|---|
| Claude Opus 5.5 | Pilote : cadrage, découpage, relecture, livrables clients | Le code mécanique qu'un exécutant peut faire |
| Claude Fable 5.1 | Juge : enquête, contre-expertise, relecture critique des sessions | Le code de production |
| Codex | Exécutant : missions bornées en atelier jetable, correctifs, tests, travail de nuit | Décider, publier, toucher un service en production |
| Gemini, via Antigravity | Second avis : multimodal, recherche longue, relecture lourde | Modifier sans brief écrit |
| Qwen et Gemma, en local | Tri, classement, extraction, embeddings, données privées | Rendre seuls un verdict final |
| Hermes | Agent de messagerie : résumé du jour, état, décisions, alertes | Traiter de gros volumes |
