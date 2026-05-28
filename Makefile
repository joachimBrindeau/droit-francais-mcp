# Makefile pour DroitFrancaisMCP
# Simplifie les tâches courantes de développement

.PHONY: help install install-dev lock test test-quick lint format format-check security clean run update init version check-all

# Couleurs pour l'affichage
RED=\033[0;31m
GREEN=\033[0;32m
YELLOW=\033[1;33m
NC=\033[0m # No Color

help:  ## Afficher cette aide
	@echo "$(GREEN)DroitFrancaisMCP - Commandes disponibles$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'

install:  ## Installer les dépendances de production (uv si dispo, sinon pip)
	@echo "$(GREEN)Installation depuis pyproject.toml...$(NC)"
	@if command -v uv >/dev/null 2>&1; then \
		uv pip install . ; \
	else \
		pip install . ; \
	fi
	@echo "$(GREEN)✓ Installation terminée$(NC)"

install-dev:  ## Installer en mode éditable avec extras dev (uv si dispo)
	@echo "$(GREEN)Installation en mode éditable avec extras dev...$(NC)"
	@if command -v uv >/dev/null 2>&1; then \
		uv sync --extra dev ; \
	else \
		pip install -e ".[dev]" ; \
	fi
	@echo "$(GREEN)✓ Installation terminée$(NC)"

lock:  ## Régénérer uv.lock (commit le fichier après modification de pyproject.toml)
	@echo "$(GREEN)Génération du lockfile uv...$(NC)"
	uv lock
	@echo "$(GREEN)✓ uv.lock à jour$(NC)"

test:  ## Lancer les tests
	@echo "$(GREEN)Lancement des tests...$(NC)"
	pytest --cov=. --cov-report=term-missing --cov-report=html
	@echo "$(GREEN)✓ Tests terminés - voir htmlcov/index.html pour le rapport$(NC)"

test-quick:  ## Lancer les tests sans coverage
	@echo "$(GREEN)Lancement des tests rapides...$(NC)"
	pytest -v
	@echo "$(GREEN)✓ Tests terminés$(NC)"

lint:  ## Vérifier la qualité du code (ruff + mypy)
	@echo "$(GREEN)Vérification du code...$(NC)"
	@echo "$(YELLOW)→ ruff check$(NC)"
	ruff check src tests
	@echo "$(YELLOW)→ MyPy$(NC)"
	mypy --install-types --non-interactive --ignore-missing-imports src || true
	@echo "$(GREEN)✓ Vérification terminée$(NC)"

format:  ## Formater le code avec ruff (lint --fix + format)
	@echo "$(GREEN)Formatage du code...$(NC)"
	ruff check --fix src tests
	ruff format src tests
	@echo "$(GREEN)✓ Formatage terminé$(NC)"

format-check:  ## Vérifier le formatage sans modifier
	@echo "$(GREEN)Vérification du formatage...$(NC)"
	ruff format --check src tests
	@echo "$(GREEN)✓ Formatage OK$(NC)"

security:  ## Vérifier les vulnérabilités (ruff S + pip-audit)
	@echo "$(GREEN)Scan de sécurité...$(NC)"
	ruff check --select S src tests
	pip-audit || true
	@echo "$(GREEN)✓ Scan terminé$(NC)"

clean:  ## Nettoyer les fichiers temporaires
	@echo "$(GREEN)Nettoyage...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.log" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache .mypy_cache .coverage htmlcov/ dist/ build/
	@echo "$(GREEN)✓ Nettoyage terminé$(NC)"

run:  ## Lancer le serveur MCP
	@echo "$(GREEN)Démarrage du serveur MCP...$(NC)"
	python3 -m droit_francais_mcp

update:  ## Mettre à jour les dépendances
	@echo "$(GREEN)Mise à jour des dépendances...$(NC)"
	pip list --outdated
	@echo ""
	@echo "$(YELLOW)Pour mettre à jour un package:$(NC)"
	@echo "  pip install --upgrade <package>"
	@echo "  Puis ajuster les bornes de version dans pyproject.toml"

check-all: format lint test security  ## Tout vérifier (format, lint, test, security)
	@echo "$(GREEN)✓ Toutes les vérifications sont terminées !$(NC)"

init:  ## Initialiser l'environnement de développement
	@echo "$(GREEN)Initialisation de l'environnement...$(NC)"
	python3 -m venv .venv
	@echo "$(YELLOW)Activez l'environnement virtuel :$(NC)"
	@echo "  source .venv/bin/activate  (Linux/macOS)"
	@echo "  .venv\\Scripts\\activate     (Windows)"
	@echo ""
	@echo "$(YELLOW)Puis installez les dépendances :$(NC)"
	@echo "  make install-dev   # installe en mode éditable avec extras [dev]"
	@echo ""
	@echo "$(YELLOW)Pour les utilisateurs finaux (sans clone du dépôt) :$(NC)"
	@echo "  uvx droit-francais-mcp                # exécution éphémère"
	@echo "  pipx install droit-francais-mcp       # installation persistante"


version:  ## Afficher la version (source unique: pyproject.toml)
	@python3 -c "from importlib.metadata import version, metadata; m = metadata('droit-francais-mcp'); print(f'Version: {version(\"droit-francais-mcp\")}\nAuteur: {m.get(\"Author\") or m.get(\"Author-email\") or \"n/c\"}')"

.DEFAULT_GOAL := help
