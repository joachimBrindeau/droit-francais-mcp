# 🚀 Guide de démarrage rapide

Guide pour démarrer avec **DroitFrancaisMCP** en 5 minutes.

---

## ⚡ Installation express

### 1. Prérequis

- Python 3.10+ installé
- Accès API PISTE ([demander ici](https://piste.gouv.fr/))
- (Recommandé) [`uv`](https://docs.astral.sh/uv/) ou [`pipx`](https://pipx.pypa.io/) installé

### 2. Installation — 1 commande

#### Option A — `uvx` (zéro install, recommandé)

Rien à installer : on configure directement Claude Desktop / Cursor pour appeler `uvx droit-francais-mcp` (voir étape 4).

#### Option B — `pipx` (installation persistante)

```bash
pipx install droit-francais-mcp
```

#### Option C — depuis le source

```bash
git clone https://github.com/jmtanguy/DroitFrancaisMCP.git
cd DroitFrancaisMCP
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
```

### 3. Configuration des identifiants PISTE

Les identifiants peuvent être fournis :

- soit via le bloc `env` du JSON MCP (voir étape 4),
- soit via un fichier `.env` à la racine du projet (utile en dev avec `pip install -e .`).

```bash
# Optionnel : copier le template puis éditer
cp .env.example .env
```

Remplir :

```bash
PISTE_CLIENT_ID=votre_client_id
PISTE_CLIENT_SECRET=votre_secret
```

### 4. Configurer Claude Desktop ou Cursor

```json
{
  "mcpServers": {
    "droit-francais": {
      "command": "uvx",
      "args": ["droit-francais-mcp"],
      "env": {
        "PISTE_CLIENT_ID": "votre_client_id",
        "PISTE_CLIENT_SECRET": "votre_secret"
      }
    }
  }
}
```

Remplacer `command` par `droit-francais-mcp` (sans `args`) si l'option B (pipx) a été choisie.

Démarrer Claude Desktop ou Cursor — l'outil `droit-francais` apparaît dans la barre MCP.

✅ **C'est tout ! Le serveur est prêt.**

---

## 🎯 Configuration des clients MCP

### Claude Desktop

Ajouter dans `~/.config/claude-desktop/claude_desktop_config.json` :

```json
{
  "mcpServers": {
    "droit-francais": {
      "command": "/chemin/vers/DroitFrancaisMCP/.venv/bin/python3",
      "args": ["/chemin/vers/DroitFrancaisMCP/droit_francais_MCP.py"]
    }
  }
}
```

Redémarrer Claude Desktop → Le serveur apparaît !

### Cursor

Ajouter dans votre fichier de configuration MCP Cursor (généralement `~/.cursor/mcp.json` ou dans les paramètres) :

```json
{
  "mcpServers": {
    "DroitFrancaisMCP": {
      "command": "<PATH_TO_DroitFrancaisMCP>/.venv/bin/python3",
      "args": [
        "-u",
        "<PATH_TO_DroitFrancaisMCP>/droit_francais_MCP.py"
      ],
      "cwd": "<PATH_TO_DroitFrancaisMCP>",
      "env": {
        "PYTHONPATH": "<PATH_TO_DroitFrancaisMCP>",
        "PYTHONUNBUFFERED": "1",
        "PYTHONIOENCODING": "utf-8"
      },
      "envFile": "<PATH_TO_ENV_FILE>",
      "description": "MCP server for French legal research (Légifrance, JudiLibre)",
      "enabled": true
    }
  }
}
```

> 💡 **Remplacez** :
>
> - `<PATH_TO_DroitFrancaisMCP>` par le chemin complet vers votre répertoire
> - `<PATH_TO_ENV_FILE>` par le chemin complet vers votre fichier `.env`

Redémarrer Cursor → Le serveur apparaît !

---

## 🧪 Premier test

Dans Claude Desktop ou Cursor, essayez :

```text
Recherche-moi les articles sur le mariage dans le Code civil
```

Ou directement avec pytest :

```bash
pytest test_api_legifrance.py -v
```

---

## 📚 Commandes utiles

### Avec Make (recommandé)

```bash
make help          # Voir toutes les commandes
make install-dev   # Installer dépendances dev
make test          # Lancer les tests
make format        # Formater le code
make lint          # Vérifier le code
make security      # Scan de sécurité
make clean         # Nettoyer
```

### Sans Make

```bash
# Tests
pytest --cov=. --cov-report=html

# Format
black --line-length 100 .

# Lint
flake8 .

# Sécurité
safety check
```

---

## 🔧 Développement

### Structure du projet

```text
DroitFrancaisMCP/
├── droit_francais_MCP.py      # Serveur MCP principal
├── api_legifrance.py           # Client Légifrance
├── api_judilibre.py            # Client JudiLibre
├── requirements.txt            # Dépendances (3 seulement !)
└── .env                        # Configuration (à créer)
```

### Outils disponibles (5)

1. `rechercher_droit_francais()` - Recherche Légifrance
2. `obtenir_article()` - Article complet
3. `rechercher_jurisprudence_judilibre()` - Recherche jurisprudence
4. `obtenir_decision_judilibre()` - Décision complète
5. `obtenir_taxonomie_judilibre()` - Taxonomies

---

## 🐛 Dépannage

### Erreur d'import

```bash
# Vérifier l'environnement virtuel
which python3  # Doit pointer vers .venv/

# Réinstaller
pip install -r requirements.txt
```

### Erreur d'authentification

```bash
# Vérifier .env
cat .env | grep PISTE

# Tester les identifiants sur piste.gouv.fr
```

### Tests qui échouent

```bash
# Vérifier les logs
cat droit_francais_mcp.log

# Mode sandbox pour tester sans vrais appels
# Modifier dans le code : sandbox=True
```

---

## 📖 Documentation complète

- [README.md](README.md) - Documentation détaillée
- [CHANGELOG.md](CHANGELOG.md) - Historique des versions

---

## 🆘 Besoin d'aide ?

1. Consultez la [documentation PISTE](https://piste.gouv.fr/)

---

Bonne utilisation ! 🎉

Version 1.1.0 - Jean-Michel Tanguy
