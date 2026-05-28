# Contribuer à droit-francais-mcp

Merci de l'intérêt pour ce serveur MCP ! Ce guide décrit le workflow de
contribution et les conventions à respecter pour qu'une PR puisse être mergée
sans friction.

## Démarrage rapide pour développer

```bash
git clone https://github.com/<votre-fork>/droit-francais-mcp.git
cd droit-francais-mcp

python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"        # installation éditable + outillage dev

# Variables d'environnement (.env optionnel pour les tests offline)
cp .env.example .env            # éditer avec vos identifiants PISTE sandbox
```

## Workflow

1. **Branche feature** depuis `main` (jamais commiter directement sur `main`).
2. **Atomicité** : un commit = une intention, idéalement reversible
   indépendamment.
3. **Conventional commits** recommandés (`feat:`, `fix:`, `refactor:`,
   `test:`, `docs:`, `build:`, `ci:`).
4. **PR** : description claire ; lier l'issue avec `Closes #N`.

## Gates locaux (équivalents au CI GitHub Actions)

Avant de pousser, lancer :

```bash
make format          # ruff format
make lint            # ruff check + mypy
make test            # pytest avec couverture
```

Ou directement :

```bash
ruff format src tests
ruff check src tests
mypy src
pytest -m "not integration"
```

Le CI fait tourner ces gates sur Python 3.10/3.11/3.12/3.13 (Linux) +
3.12 (macOS, Windows). Une PR avec des gates rouges ne sera pas mergée.

## Tests

- **Unit (offline)** : `pytest -m "not integration"` — pas de réseau, pas
  de credentials, doit passer en < 2 secondes.
- **Integration** : `pytest -m integration` — nécessite `PISTE_SANDBOX_CLIENT_ID`
  et `PISTE_SANDBOX_CLIENT_SECRET` dans `.env`. Saute automatiquement les
  tests si les vars manquent (voir `tests/conftest.py`).
- **Couverture** : objectif **≥ 85 %** sur le package (`make test` affiche
  le résumé). Un patch doit conserver ou améliorer la couverture.
- **Caractérisation** : `tests/test_characterization.py` pin du contrat
  d'API MCP. Modifier ces tests requiert un changelog explicite et
  l'accord du mainteneur (cf. CHANGELOG.md « Rétro-compatibilité »).

## Style

- **Ruff** est la SSOT (lint + format + import sort + sécurité S). Pas de
  black, flake8 ou isort séparés. La config vit dans `pyproject.toml`
  `[tool.ruff]`.
- **MyPy strict** : tout nouveau code doit passer `mypy src` (config
  `[tool.mypy] strict = true`). Pas de `# type: ignore` sans commentaire
  qui justifie.
- **Conventions FastMCP** :
  - Ordre des décorateurs : `@mcp.tool` AU-DESSUS de `@safe_mcp_tool`.
  - Tout `print()` interdit dans le code serveur — logs uniquement sur
    stderr (le protocole MCP réserve stdout pour le framing JSON-RPC).

## Architecture

```
src/droit_francais_mcp/
├── server.py         FastMCP instance, decorator, lazy init, main()
├── tools.py          @mcp.tool functions
├── resources.py      @mcp.resource markdown
├── piste/auth.py     OAuth client (base)
├── piste/filters.py  Recursive payload filter
├── legifrance/       Client + builder + descriptions
└── judilibre/        Client
```

Voir `docs/audits/` pour l'historique des refactors et décisions
architecturales.

## Signaler un bug / proposer une feature

Utiliser les templates dans `.github/ISSUE_TEMPLATE/` (ouvrir une issue
depuis l'onglet « Issues » applique automatiquement le bon template).

## Sécurité

Vulnérabilités → voir `SECURITY.md`. Ne **PAS** ouvrir d'issue publique
pour un problème de sécurité.
