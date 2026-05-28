# 🏛️ Serveur MCP Droit Français

[![Version](https://img.shields.io/badge/version-1.2.1-blue.svg)](https://github.com/jmtanguy/DroitFrancaisMCP/releases)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![MCP](https://img.shields.io/badge/MCP-Compatible-purple)](https://modelcontextprotocol.io/)

Ce projet a pour objectif d’explorer l’intégration d’outils dans **Claude Desktop** via le protocole **Model Context Protocol (MCP)**.

Il s’inscrit dans une démarche d’expérimentation et de validation visant à comprendre comment l’orchestration d’outils peut améliorer la fiabilité, la pertinence et l’efficacité des modèles de langage (LLM) lorsqu’ils traitent des données techniques.

Dans ce cadre, l’accent est mis sur l’accès à des données juridiques fiables issues de sources officielles.

Le serveur MCP développé ici fournit une interface unifiée pour interroger les API publiques du droit français, notamment :

- Légifrance – pour la législation, les codes, les lois et les décrets
- JudiLibre – pour la jurisprudence et les décisions judiciaires

Grâce à ce serveur, il devient possible de rechercher et de consulter :

- 📖 Les codes juridiques français (Code civil, Code pénal, Code du travail, etc.)
- 📜 Les lois, ordonnances, décrets et arrêtés
- ⚖️ La jurisprudence de toutes les juridictions françaises
- 📰 Le Journal Officiel de la République Française (JORF)
- 🤝 Les conventions collectives
- 🏛️ Les décisions du Conseil d'État, de la Cour de cassation et des tribunaux

---

## 📋 Table des matières

- [Prérequis](#-prérequis)
- [Fonctionnalités](#-fonctionnalités)
- [Installation](#-installation)
- [Configuration](#configuration)
- [Utilisation](#utilisation)
- [Exemples d'utilisation](#-exemples-dutilisation)
- [Outils disponibles](#outils-disponibles)
- [Architecture](#architecture)
- [Tests](#-tests)
- [Licence](#-licence)
- [Liens utiles](#-liens-utiles)
- [Développement avec IA](#-développement-avec-ia)
- [Auteur](#-auteur)

---

## 🔑 Prérequis

### 1. Accès à l'API PISTE

**IMPORTANT** : Pour utiliser ce serveur, vous devez obligatoirement obtenir des accès aux API publiques via le site officiel **[PISTE](https://piste.gouv.fr/)**.

Afin de valider l'accès aux API, vous devez également valider les conditions d'utilisations pour les API Légifrance et Judilibre.

#### Comment obtenir vos accès

1. **Créer un compte** sur [piste.gouv.fr](https://piste.gouv.fr/)
2. **Demander l'accès** aux API suivantes :
   - **API Légifrance** : Recherche et consultation des textes juridiques
   - **API JudiLibre** : Recherche et consultation des décisions de justice
3. **Récupérer vos identifiants** :
   - `CLIENT_ID` : Identifiant client unique
   - `CLIENT_SECRET` : Clé secrète d'authentification

> 💡 **Note** : Les API PISTE sont gratuites mais nécessitent une inscription préalable. Comptez quelques jours pour l'activation de votre compte.

### 2. Système

- **Python 3.8+** (version recommandée : 3.10+)
- **pip** pour la gestion des paquets
- **Git** pour cloner le dépôt
- **Claude Desktop** ou **Cursor** (pour l'intégration MCP)

---

## ✨ Fonctionnalités

### 🔍 Recherche Légifrance

- **Recherche avancée** dans tous les fonds juridiques français
- **Filtres puissants** : par nature, date, juridiction, ministère, etc.
- **Consultation d'articles** : texte intégral avec métadonnées complètes
- **Multi-fonds** : codes, lois, JORF, jurisprudence, conventions collectives

### ⚖️ Recherche JudiLibre

- **Recherche de jurisprudence** dans toutes les juridictions françaises
- **Filtres contextuels** : juridiction, chambre, localisation, solution, thème
- **Texte intégral** des décisions avec zones structurées
- **Taxonomie complète** : accès aux listes de valeurs valides (chambres, formations, thèmes)

### 🛠️ Fonctionnalités techniques

- **Authentification OAuth 2.0** sécurisée
- **Gestion automatique des tokens**
- **Logging détaillé** pour le débogage
- **Mode Sandbox et Production**
- **Validation des paramètres**
- **Gestion d'erreurs**

---

## ⚡ Démarrage rapide (3 minutes)

1. **Prérequis** : Python 3.10+ et un compte [PISTE](https://piste.gouv.fr/).
2. **Installation** : `uvx droit-francais-mcp` (ou `pipx install droit-francais-mcp`).
3. **Configuration** : ajouter le bloc JSON ci-dessous à `claude_desktop_config.json`.
4. **Vérification** : redémarrer Claude Desktop ; l'outil `droit-francais` apparaît
   dans la liste MCP.

```json
{
  "mcpServers": {
    "droit-francais": {
      "command": "uvx",
      "args": ["droit-francais-mcp"],
      "env": {
        "PISTE_CLIENT_ID": "votre_id",
        "PISTE_CLIENT_SECRET": "votre_secret"
      }
    }
  }
}
```

Voir la section [Installation](#-installation) pour les détails (autres clients,
développement local) et [`docs/CAPABILITY_MAP.md`](docs/CAPABILITY_MAP.md) pour
la liste exhaustive des outils MCP exposés.

---

## 🚀 Installation

### Option 1 — Exécution éphémère via `uvx` (recommandée)

Aucune installation préalable. [`uv`](https://docs.astral.sh/uv/) télécharge le paquet, l'exécute dans un environnement isolé, puis nettoie.

```json
{
  "mcpServers": {
    "droit-francais": {
      "command": "uvx",
      "args": ["droit-francais-mcp"],
      "env": {
        "PISTE_CLIENT_ID": "votre_client_id",
        "PISTE_CLIENT_SECRET": "votre_client_secret"
      }
    }
  }
}
```

### Option 2 — Installation persistante via `pipx`

```bash
pipx install droit-francais-mcp
```

Puis dans `claude_desktop_config.json` :

```json
{
  "mcpServers": {
    "droit-francais": {
      "command": "droit-francais-mcp",
      "env": {
        "PISTE_CLIENT_ID": "votre_client_id",
        "PISTE_CLIENT_SECRET": "votre_client_secret"
      }
    }
  }
}
```

### Option 3 — Installation depuis le source (développeurs)

```bash
git clone https://github.com/joachimBrindeau/droit-francais-mcp.git
cd droit-francais-mcp

# Avec uv (recommandé — résolution + install ~10× plus rapide que pip)
uv sync --extra dev

# Ou avec pip
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

make test                          # tests offline (intégration sautés sans .env)
```

Le serveur peut alors être lancé via `droit-francais-mcp`,
`python -m droit_francais_mcp`, ou `fastmcp run` (qui lit `fastmcp.json`).

### Option 4 — `fastmcp run` avec `fastmcp.json`

Ce dépôt fournit un `fastmcp.json` à la racine. Avec [FastMCP CLI](https://gofastmcp.com/)
installé :

```bash
fastmcp run    # détecte fastmcp.json automatiquement
```

C'est utile pour le dev local quand on veut tester des modifications sans
réinstaller.

---

## ⚙️ Configuration

### 1. Créer le fichier d'environnement

```bash
# Copier le fichier exemple
cp .env.example .env
```

### 2. Remplir vos identifiants PISTE

Éditez le fichier `.env` avec vos vraies valeurs :

```bash
# Identifiants API PISTE Production
PISTE_CLIENT_ID=votre_client_id_production_ici
PISTE_CLIENT_SECRET=votre_client_secret_production_ici

# Identifiants API PISTE Sandbox (optionnel pour les tests)
PISTE_SANDBOX_CLIENT_ID=votre_client_id_sandbox_ici
PISTE_SANDBOX_CLIENT_SECRET=votre_client_secret_sandbox_ici
```

> ⚠️ **SÉCURITÉ** : Le fichier `.env` contient vos secrets et ne doit **JAMAIS** être commité dans Git !

### 3. Configuration des clients MCP

#### Configuration Claude Desktop

Pour utiliser le serveur avec Claude Desktop, vérifier cette configuration dans :

**macOS/Linux** : `~/.config/claude-desktop/claude_desktop_config.json`
**Windows** : `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "droit-francais": {
      "command": "/chemin/absolu/vers/DroitFrancaisMCP/.venv/bin/python3",
      "args": ["/chemin/absolu/vers/DroitFrancaisMCP/droit_francais_MCP.py"]
    }
  }
}
```

> 💡 **Conseil** : Remplacez `/chemin/absolu/vers/` par le chemin complet vers votre répertoire.

#### Configuration Cursor

Pour utiliser le serveur avec Cursor, ajoutez cette configuration dans votre fichier de configuration MCP (généralement `~/.cursor/mcp.json` ou dans les paramètres de Cursor) :

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
> - `<PATH_TO_DroitFrancaisMCP>` par le chemin complet vers votre répertoire DroitFrancaisMCP
> - `<PATH_TO_ENV_FILE>` par le chemin complet vers votre fichier `.env` contenant les identifiants PISTE

---

## 📖 Utilisation

### Démarrage du serveur

#### Avec Claude Desktop

1. Redémarrez Claude Desktop
2. Le serveur devrait apparaître dans la liste des serveurs MCP disponibles
3. Vous pouvez maintenant utiliser les outils directement dans Claude

#### Avec Cursor

1. Redémarrez Cursor
2. Le serveur devrait apparaître dans la liste des serveurs MCP disponibles
3. Vous pouvez maintenant utiliser les outils directement dans Cursor via le protocole MCP

## 💡 Exemples d'utilisation

Dans Claude Desktop ou Cursor, essayez ces requêtes en langage naturel :

### 📖 Recherche dans les Codes

```text
Recherche-moi les articles sur le mariage dans le Code civil
```

→ Claude utilisera `rechercher_legifrance()` avec les paramètres appropriés

```text
Trouve les articles du Code du travail concernant le licenciement économique
```

→ Recherche ciblée dans le fond CODE_ETAT

### ⚖️ Recherche de jurisprudence

```text
Quels sont les arrêts récents de la Cour de cassation concernant le licenciement pour faute grave ?
```

→ Claude utilisera `rechercher_jurisprudence_judilibre()` avec filtres de date et de thème

```text
Trouve les décisions de la Chambre sociale sur le harcèlement moral depuis 2020
```

→ Recherche avec filtre de chambre et période

### 🔍 Recherches avancées

```text
Liste les décisions de la Cour d'appel de Paris sur la responsabilité médicale en 2023
```

→ Utilisation des filtres de localisation, juridiction et date

```text
Cherche dans le JORF les décrets publiés en janvier 2024 concernant l'environnement
```

→ Recherche avec filtres de fond, date et mot-clé

Claude ou Cursor identifiera automatiquement les outils MCP adaptés pour interroger les sources officielles et vous présentera les résultats correspondants.

---

## 🛠️ Outils disponibles

### Légifrance

| Outil | Description |
|-------|-------------|
| `rechercher_legifrance()` | Recherche avancée multi-critères dans tous les fonds juridiques (codes, lois, JORF, jurisprudence, conventions collectives) |
| `consulter_legifrance()` | Récupération du texte intégral d'un article/texte avec métadonnées complètes |

**Paramètres principaux** :

- `recherche` : Terme(s) de recherche
- `fond` : Fonds de recherche (ALL, CODE_ETAT, LODA_ETAT, JORF, JURI, KALI, etc.)
- `type_champ` : Champ de recherche (ALL, TITLE, ARTICLE, etc.)
- `type_recherche` : Type de recherche (TOUS_LES_MOTS_DANS_UN_CHAMP, UN_DES_MOTS, EXACTE)
- `code` : Nom du code pour recherche spécifique (ex: "Code civil")
- `date_debut`, `date_fin` : Filtres de dates (format YYYY-MM-DD)
- `page`, `page_taille` : Pagination des résultats
- `tri` : Ordre de tri (PERTINENCE, SIGNATURE_DATE_DESC, etc.)

### JudiLibre

| Outil | Description |
|-------|-------------|
| `rechercher_jurisprudence_judilibre()` | Recherche de décisions de justice avec filtres avancés (juridiction, chambre, thème, solution, dates) |
| `consulter_decision_judilibre()` | Récupération du texte intégral d'une décision avec zones structurées |
| `obtenir_taxonomie_judilibre()` | Accès aux listes de valeurs valides (chambres, juridictions, localisations, thèmes, solutions) |

**Paramètres principaux** :

- `recherche` : Texte de recherche
- `juridiction` : Code juridiction (cc, ca, tj, ta, caa, ce, tc, crc)
- `chambre` : Code chambre (civ1, civ2, civ3, comm, soc, cr, etc.)
- `localisation` : Code siège de juridiction (ex: ca_paris, tj75101)
- `type_decision` : Type de décision (arret, ordonnance, qpc, saisie)
- `theme` : Matière juridique
- `solution` : Type de solution (cassation, rejet, annulation, etc.)
- `date_debut`, `date_fin` : Intervalle de dates
- `tri` : Tri (scorepub, score, date)
- `ordre` : Sens du tri (desc, asc)

### 📚 Ressources de documentation intégrées

Le serveur MCP expose également des ressources de documentation accessibles directement dans Claude :

**Légifrance** :

- `legifrance://documentation/fonds` - Liste des fonds de recherche disponibles
- `legifrance://documentation/champs` - Types de champs de recherche
- `legifrance://documentation/types-recherche` - Types de recherche disponibles
- `legifrance://documentation/options-tri` - Options de tri
- `legifrance://documentation/filtres-dates` - Guide des filtres de dates

**JudiLibre** :

- `judilibre://documentation/juridictions` - Codes de juridictions
- `judilibre://documentation/chambres` - Chambres de la Cour de cassation
- `judilibre://documentation/localisations` - Codes de localisations (sièges)
- `judilibre://documentation/types-decision` - Types de décision
- `judilibre://documentation/themes` - Thèmes (matières juridiques)
- `judilibre://documentation/solutions` - Types de solutions
- `judilibre://documentation/options-tri` - Options de tri

Ces ressources permettent à Claude d'accéder à la documentation technique sans que vous ayez besoin de la fournir manuellement.

---

## 🏗️ Architecture

```text
DroitFrancaisMCP/
├── droit_francais_MCP.py              # Serveur MCP principal
├── api_legifrance.py                  # Client API Légifrance
├── api_legifrance_query_builder.py   # Constructeur de requêtes Légifrance
├── api_judilibre.py                   # Client API JudiLibre
├── __version__.py                     # Informations de version
├── test_api_legifrance.py             # Tests Légifrance
├── test_api_judilibre.py              # Tests JudiLibre
├── pyproject.toml                     # Configuration du projet
├── .env.example                       # Template de configuration
├── README.md                          # Documentation
├── CHANGELOG.md                       # Historique des versions
├── LICENSE                            # Licence MIT
├── install.sh                         # Script d'installation (macOS/Linux)
└── install.ps1                        # Script d'installation (Windows)
```

### Composants principaux

- **`droit_francais_MCP.py`** : Serveur MCP qui expose les outils via FastMCP avec documentation complète des ressources
- **`api_legifrance.py`** : Client pour l'API Légifrance avec authentification OAuth 2.0
- **`api_legifrance_query_builder.py`** : Constructeur de requêtes complexes pour Légifrance
- **`api_judilibre.py`** : Client pour l'API JudiLibre avec gestion automatique des tokens
- **`__version__.py`** : Centralisation des informations de version du projet
- **Tests** : Scripts de validation et exemples d'utilisation des APIs

---

## 🧪 Tests

### Tester l'API Légifrance

```bash
python3 test_api_legifrance.py
```

### Tester l'API JudiLibre

```bash
python3 test_api_judilibre.py
```

### Avec pytest

```bash
pytest test_api_legifrance.py -v
pytest test_api_judilibre.py -v
```

---

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

## 🔗 Liens utiles

- [Site officiel PISTE](https://piste.gouv.fr/) - Demande d'accès aux API
- [Model Context Protocol](https://modelcontextprotocol.io/) - Spécification MCP
- [Claude Desktop](https://claude.ai/download) - Application Claude
- [Cursor](https://cursor.sh/) - Éditeur de code avec support MCP

---

## 🤖 Développement avec IA

Ce projet a été développé avec l'assistance d'outils d'intelligence artificielle :

- **Claude** (Anthropic) - Assistant de développement et génération de code
- **GitHub Copilot** - Autocomplétion de code

L'utilisation de ces outils a permis d'accélérer le développement tout en maintenant une qualité de code élevée et une documentation complète. Tous les éléments générés ont été revus, validés et adaptés aux besoins spécifiques du projet.

> 💡 **Transparence** : Cette mention permet aux contributeurs et utilisateurs de comprendre le contexte de création du projet.

---

## 👤 Auteur

Jean-Michel Tanguy
