"""Configuration partagée des tests.

Charge `.env` au démarrage de la session et saute les tests marqués
`integration` quand les identifiants PISTE sandbox ne sont pas disponibles —
évite les 53 échecs OAuth 400 « bruyants » qui masqueraient un vrai problème.
"""

from __future__ import annotations

import os
from typing import List

import pytest
from dotenv import load_dotenv

_REQUIRED_SANDBOX_ENV = ("PISTE_SANDBOX_CLIENT_ID", "PISTE_SANDBOX_CLIENT_SECRET")


def pytest_configure(config: pytest.Config) -> None:
    """Charge `.env` une seule fois en début de session."""
    load_dotenv(verbose=False)


def pytest_collection_modifyitems(
    config: pytest.Config, items: List[pytest.Item]
) -> None:
    """Skip les tests `integration` si les credentials PISTE sandbox manquent.

    L'utilisateur peut forcer l'exécution avec `-m integration` + des creds
    valides dans `.env`. En CI sans creds, l'absence d'identifiants est traitée
    comme un environnement non-applicable plutôt qu'une régression.
    """
    missing = [name for name in _REQUIRED_SANDBOX_ENV if not os.getenv(name)]
    if not missing:
        return
    reason = (
        f"Tests d'intégration sautés : variables manquantes {missing}. "
        f"Renseigner `.env` (voir `.env.example`) pour exécuter."
    )
    skip_marker = pytest.mark.skip(reason=reason)
    for item in items:
        if "integration" in item.keywords:
            item.add_marker(skip_marker)
