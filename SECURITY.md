# Politique de sécurité

## Versions supportées

| Version | Supportée |
|---------|-----------|
| 1.3.x   | ✅ |
| 1.2.x   | ⚠️ correctifs critiques uniquement (jusqu'à v1.4.0) |
| < 1.2   | ❌ |

## Signaler une vulnérabilité

**Ne pas ouvrir d'issue GitHub publique.** Pour signaler une vulnérabilité,
utiliser l'un des canaux suivants :

1. **GitHub Security Advisories** (préféré) : onglet « Security » du dépôt
   → « Report a vulnerability ». Le rapport est privé et un identifiant
   GHSA est généré.
2. **Email** : ouvrir un Security Advisory privé via GitHub.

### Information attendue

- Description du problème + impact estimé.
- Étapes de reproduction (idéalement minimal repro).
- Version affectée du paquet.
- Optionnel : proposition de patch.

### Engagement de réponse

- Accusé de réception sous **48 heures** ouvrées.
- Première évaluation (sévérité, fix possible) sous **5 jours** ouvrés.
- Correctif :
  - **Critique** : patch dans les 7 jours, advisory publique après merge.
  - **Haute** : patch sous 14 jours.
  - **Moyenne / Basse** : intégré au prochain release mineur.

## Périmètre

### In-scope

- Fuite de credentials (env vars, fichier `.env`, tokens OAuth en cache).
- Injection de paramètres pouvant atteindre l'API PISTE.
- Bypass des validations côté client.
- Dépendances vulnérables (`pip-audit` est exécuté en local mais pas
  encore en CI — à venir).
- Comportement non documenté qui exposerait des données sensibles.

### Out-of-scope

- Vulnérabilités dans les **API PISTE** elles-mêmes (à signaler à
  https://piste.gouv.fr/).
- Vulnérabilités dans **fastmcp** (à signaler à
  https://github.com/jlowin/fastmcp).
- Problèmes nécessitant un accès local au filesystem du serveur MCP
  (le modèle de menace assume que celui qui lance le serveur a déjà ces
  privilèges).
- Déni de service contre la propre machine de l'utilisateur via une
  requête mal formée (l'usage est en local par Claude Desktop / Cursor).

## Bonnes pratiques pour les utilisateurs

- Ne **jamais** commiter `.env` (le `.gitignore` est explicite, vérifier
  avant chaque push).
- Régénérer les credentials PISTE en cas de doute (https://piste.gouv.fr/).
- Mettre à jour vers la dernière version stable régulièrement.
- Vérifier l'intégrité des releases via la signature `git tag -v vX.Y.Z`
  une fois la signature configurée (à venir).
