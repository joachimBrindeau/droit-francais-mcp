# Changelog

## [1.3.0] - 2026-05-28

### Refactoring structurel (compound-refactor revamp)

#### Layout — adoption de `src/droit_francais_mcp/`

- **Nouveau package** `src/droit_francais_mcp/` avec sous-packages `piste/`, `legifrance/`, `judilibre/`. Les 7 modules à plat du dépôt sont regroupés par domaine. Voir `docs/audits/2026-05-28-revamp-compound-refactor-droit-francais-mcp.md` pour le plan complet.
- **Renommages** : `droit_francais_MCP.py` → `server.py` ; `piste_utils.py` → `piste/filters.py` ; les modules `api_*.py` perdent leur préfixe.
- **Tests** déplacés vers `tests/` avec un `conftest.py` qui saute automatiquement les tests `integration` quand `PISTE_SANDBOX_CLIENT_ID`/`PISTE_SANDBOX_CLIENT_SECRET` sont absents.
- **`test_jupyter.py` → `examples/jupyter_exploration.py`** (le fichier n'a jamais été un test pytest mais un script d'exploration).

#### Outillage — pyproject comme source unique de vérité

- **`requirements.txt` et `requirements-dev.txt` supprimés** (la version `requirements.txt` était encodée en UTF-16 LE et drift-prone par rapport à pyproject). Toutes les dépendances vivent dans `pyproject.toml`.
- **`__version__.py` supprimé** ; la version est lue à l'exécution via `importlib.metadata.version("droit-francais-mcp")` depuis le package `__init__.py`.
- **flake8 + black + isort + safety + bandit → ruff** (1 outil au lieu de 5 ; couvre lint, formatage, tri d'imports, et règles de sécurité `S`). pip-audit reste recommandé pour l'audit de dépendances.
- **Bump `requires-python` ≥ 3.10** (Python 3.8 EOL 2024-10-14).
- **Cap `fastmcp >= 2.12.3,<3`** (FastMCP 3.x apporte des changements cassants).

#### Point d'entrée — `[project.scripts]`

- **Nouvelle console-script** `droit-francais-mcp = "droit_francais_mcp.server:main"`. Après `pip install`, l'exécutable est disponible directement.
- Recommandé pour les utilisateurs finaux : `uvx droit-francais-mcp` (sans installation) ou `pipx install droit-francais-mcp` (installation persistante).
- `python -m droit_francais_mcp` fonctionne également.

#### Adoption du wrapper HTTP partagé

- `PisteOAuthClient._request` (introduit en 1.2.1 mais non utilisé) est désormais adopté à tous les sites d'appel HTTP de `LegifranceAPI` et `JudilibreAPI`. ~60 lignes de boilerplate `try`/`headers`/`timeout`/`raise_for_status` éliminées.
- `safe_mcp_tool` utilise `logger.exception()` (avec traceback) et renvoie une copie profonde de `on_error_return` pour éviter le partage d'état muable entre appels.
- `_safe_init` capture désormais le détail de l'exception d'initialisation dans un dict module-level `_init_errors` ; les outils MCP rapportent la vraie raison plutôt qu'un générique "API non initialisée".
- Deux n-uplets de fonds en dur (`api_legifrance.py:174,196`) promus en `LegifranceQueryBuilder.CODE_FONDS` et `VIGUEUR_DEFAULT_FONDS`.

#### Documentation et nettoyage

- **`install.sh` / `install.bat` / `install.ps1` supprimés** — `uvx`/`pipx` couvre les trois plateformes sans script ad hoc.
- **`Légifrance.json`** (spec Swagger 2.0 de Légifrance, 308 KB) déplacé du root vers `docs/api-specs/legifrance-swagger-2.0.json`.
- Tests de caractérisation MCP ajoutés (`tests/test_characterization.py`) : pin du nombre/nom des 5 outils MCP, contrat d'erreur de `safe_mcp_tool`, mécanisme `_init_errors`, frozensets de fonds, timeout PISTE partagé.

### ⚠️ Rétro-compatibilité — Déprécations

- **`droit_francais_MCP.py` à la racine reste présent en shim** (4 lignes) pour les configurations `claude_desktop_config.json` qui référencent ce chemin absolu. Une `DeprecationWarning` est émise sur stderr (sûr en MCP stdio). **Ce shim sera retiré dans la v2.0** — les utilisateurs doivent migrer vers `droit-francais-mcp` (console-script), `uvx droit-francais-mcp`, ou `python -m droit_francais_mcp`.
- Les modules au top-level (`api_legifrance`, `api_judilibre`, `piste_auth`, `piste_utils`, etc.) ne sont **plus importables** depuis l'extérieur. Les consommateurs externes doivent passer par `droit_francais_mcp.legifrance.client.LegifranceAPI`, etc.

## [1.2.1] - 2025-01-21

### Corrections et améliorations

#### Scripts d'installation

- **install.bat** : Correction des chemins pour utiliser des slashes forward (/) au lieu de backslashes (\) dans la configuration Claude Desktop, garantissant une meilleure compatibilité cross-platform
- **install.ps1** : Amélioration de la gestion des chemins Windows avec conversion automatique des backslashes en slashes forward pour la configuration JSON de Claude Desktop

#### Gestion des logs

- **Niveau de logging** : Passage du niveau de logging de `DEBUG` à `WARNING` pour réduire la verbosité en production
- **Messages d'erreur** : Simplification des messages d'erreur retournés par les outils pour une meilleure lisibilité

#### Code

- **Suppression de l'import __version__** : Retrait de l'import non utilisé du module `__version__` dans le fichier principal, simplifiant l'initialisation du serveur MCP

## [1.2.0] - 2025-01-17

### Améliorations majeures

#### Système de ressources MCP

- **Ajout de 12 ressources de documentation intégrées** accessibles directement dans Claude
  - `legifrance://documentation/*` : 5 ressources (fonds, champs, types-recherche, options-tri, filtres-dates)
  - `judilibre://documentation/*` : 7 ressources (juridictions, chambres, localisations, types-decision, themes, solutions, options-tri)
- **Optimisation de la consommation de tokens** : La documentation technique est désormais accessible via des ressources au lieu d'être incluse dans chaque prompt
- **Accélération des réponses** : Réduction de la latence en évitant les appels systématiques à la documentation

#### 🏗️ Architecture et Code

- Nettoyage automatique des réponses API (suppression des valeurs `None` et vides)
- Amélioration de la gestion des erreurs avec messages plus explicites
- Harmonisation des commentaires et de la documentation

**⚠️ Changements de noms** : Les outils Légifrance et JudiLibre ont été renommés pour plus de cohérence et de clarté.

## [1.1.0] - Version - 2025-11-08

Outils MCP disponibles :

1. `rechercher_droit_francais()` - Recherche avancée Légifrance
2. `obtenir_article()` - Récupération d'articles juridiques
3. `rechercher_jurisprudence_judilibre()` - Recherche de jurisprudence
4. `obtenir_decision_judilibre()` - Récupération de décisions complètes
5. `obtenir_taxonomie_judilibre()` - Accès aux taxonomies

Cette version offre un accès complet et structuré aux API publiques du droit français (Légifrance et JudiLibre) via le protocole MCP. Le serveur est prêt pour une utilisation en production avec Claude Desktop et Cursor.

## [1.0.0] - Version initiale - 2025-10-19

Outils MCP disponibles :

1. `rechercher_droit_francais()` - Recherche avancée Légifrance
2. `obtenir_article()` - Récupération d'articles juridiques
3. `rechercher_jurisprudence_judilibre()` - Recherche de jurisprudence
4. `obtenir_decision_judilibre()` - Récupération de décisions complètes
5. `obtenir_taxonomie_judilibre()` - Accès aux taxonomies

Cette version initiale offre un accès complet et structuré aux API publiques du droit français (Légifrance et JudiLibre) via le protocole MCP. Le serveur est prêt pour une utilisation en production avec Claude Desktop.
