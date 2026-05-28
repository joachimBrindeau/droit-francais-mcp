"""Tests unitaires (offline) pour les fonctions `@mcp.tool` de `droit_francais_mcp.tools`."""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from droit_francais_mcp import server as srv
from droit_francais_mcp.tools import (
    consulter_decision_judilibre as _consulter_decision_judilibre_tool,
)
from droit_francais_mcp.tools import (
    consulter_legifrance as _consulter_legifrance_tool,
)
from droit_francais_mcp.tools import (
    obtenir_taxonomie_judilibre as _obtenir_taxonomie_judilibre_tool,
)
from droit_francais_mcp.tools import (
    ping_legifrance as _ping_legifrance_tool,
)
from droit_francais_mcp.tools import (
    rechercher_jurisprudence_judilibre as _rechercher_jurisprudence_judilibre_tool,
)
from droit_francais_mcp.tools import (
    rechercher_legifrance as _rechercher_legifrance_tool,
)

# FastMCP enveloppe les fonctions décorées dans `FunctionTool` ; `.fn` expose
# la fonction originale (callable Python normal, idéal pour les tests unitaires).
rechercher_legifrance = _rechercher_legifrance_tool.fn
consulter_legifrance = _consulter_legifrance_tool.fn
ping_legifrance = _ping_legifrance_tool.fn
obtenir_taxonomie_judilibre = _obtenir_taxonomie_judilibre_tool.fn
rechercher_jurisprudence_judilibre = _rechercher_jurisprudence_judilibre_tool.fn
consulter_decision_judilibre = _consulter_decision_judilibre_tool.fn

pytestmark = pytest.mark.unit


@pytest.fixture(autouse=True)
def _reset_clients() -> Any:
    """Garantit que chaque test démarre avec un cache d'init propre."""
    srv.reset_clients()
    yield
    srv.reset_clients()


# ----------------------------------------------------------------------------
# ping_legifrance
# ----------------------------------------------------------------------------


def test_ping_legifrance_surfaces_init_error() -> None:
    """Si l'init du client échoue, le ping retourne un statut d'erreur structuré."""

    class _Boom:
        def __init__(self, sandbox: bool = False) -> None:
            raise RuntimeError("creds manquants")

    with patch.object(srv, "LegifranceAPI", _Boom):
        result = ping_legifrance()

    assert isinstance(result, dict)
    assert result["status"] == "error"
    assert "creds manquants" in result["details"]


def test_ping_legifrance_returns_ok_on_success() -> None:
    fake_api = MagicMock()
    fake_api.ping.return_value = "pong"
    srv._clients["legifrance"] = fake_api

    assert ping_legifrance() == {"status": "ok", "details": "pong"}


def test_ping_legifrance_returns_error_status_on_client_failure() -> None:
    """Une exception du client est capturée et retournée comme status=error."""
    fake_api = MagicMock()
    fake_api.ping.side_effect = RuntimeError("HTTP 503")
    srv._clients["legifrance"] = fake_api

    result = ping_legifrance()
    assert result["status"] == "error"
    assert "HTTP 503" in result["details"]


# ----------------------------------------------------------------------------
# rechercher_legifrance
# ----------------------------------------------------------------------------


def test_rechercher_legifrance_rejects_empty_query() -> None:
    """Une requête vide retourne `[]` sans toucher au client."""
    assert rechercher_legifrance(recherche="") == []
    assert rechercher_legifrance(recherche="   ") == []


def test_rechercher_legifrance_returns_empty_when_api_unavailable() -> None:
    """Si l'init du client échoue, l'outil retourne `[]` (et trace l'erreur)."""

    class _Boom:
        def __init__(self, sandbox: bool = False) -> None:
            raise RuntimeError("creds manquants")

    with patch.object(srv, "LegifranceAPI", _Boom):
        assert rechercher_legifrance(recherche="x") == []
        assert "legifrance" in srv._init_errors


def test_rechercher_legifrance_delegates_to_client_search() -> None:
    """Sur le chemin nominal, l'outil délègue à `client.search()` et propage le résultat."""
    fake_api = MagicMock()
    fake_api.search.return_value = [{"id": "X"}]
    srv._clients["legifrance"] = fake_api

    result = rechercher_legifrance(recherche="mariage", fond="JORF")

    fake_api.search.assert_called_once()
    assert result == [{"id": "X"}]


def test_rechercher_legifrance_warns_when_date_unsupported_by_fond() -> None:
    """Un `date_debut` sur un fond qui ne supporte pas les dates ajoute un warning."""
    fake_api = MagicMock()
    fake_api.search.return_value = [{"id": "X"}]
    srv._clients["legifrance"] = fake_api

    result = rechercher_legifrance(
        recherche="mariage",
        fond="ALL",  # ALL ne supporte pas les dates
        date_debut="2023-01-01",
    )

    assert isinstance(result, dict)
    assert "warning" in result
    assert "results" in result
    # `date_debut` doit avoir été nullifié avant l'appel client.
    call_kwargs = fake_api.search.call_args.kwargs
    assert call_kwargs["date_start"] is None
    assert call_kwargs["date_end"] is None


def test_rechercher_legifrance_falls_back_when_client_raises() -> None:
    """L'exception du client est interceptée par `@safe_mcp_tool`."""
    fake_api = MagicMock()
    fake_api.search.side_effect = RuntimeError("API down")
    srv._clients["legifrance"] = fake_api

    assert rechercher_legifrance(recherche="x") == "Erreur lors de la recherche"


# ----------------------------------------------------------------------------
# consulter_legifrance
# ----------------------------------------------------------------------------


def test_consulter_legifrance_rejects_empty_id() -> None:
    assert consulter_legifrance(id="") == {"erreur": "L'ID de l'article ne peut pas être vide"}
    assert consulter_legifrance(id="   ") == {"erreur": "L'ID de l'article ne peut pas être vide"}


def test_consulter_legifrance_surfaces_init_error() -> None:
    class _Boom:
        def __init__(self, sandbox: bool = False) -> None:
            raise RuntimeError("init failed: env missing")

    with patch.object(srv, "LegifranceAPI", _Boom):
        result = consulter_legifrance(id="LEGIARTI42")

    assert isinstance(result, dict)
    assert "init failed" in result["erreur"]


def test_consulter_legifrance_delegates_to_client() -> None:
    fake_api = MagicMock()
    fake_api.consult.return_value = {"id": "LEGIARTI42", "text": "..."}
    srv._clients["legifrance"] = fake_api

    assert consulter_legifrance(id="LEGIARTI42") == {"id": "LEGIARTI42", "text": "..."}
    fake_api.consult.assert_called_once_with("LEGIARTI42")


# ----------------------------------------------------------------------------
# obtenir_taxonomie_judilibre
# ----------------------------------------------------------------------------


def test_obtenir_taxonomie_surfaces_init_error() -> None:
    class _Boom:
        def __init__(self, sandbox: bool = False) -> None:
            raise RuntimeError("init failed")

    with patch.object(srv, "JudilibreAPI", _Boom):
        result = obtenir_taxonomie_judilibre(taxonomy_id="chamber")

    assert isinstance(result, dict)
    assert "erreur" in result


def test_obtenir_taxonomie_delegates_to_client() -> None:
    fake_api = MagicMock()
    fake_api.taxonomy.return_value = {"chamber": "civ1"}
    srv._clients["judilibre"] = fake_api

    assert obtenir_taxonomie_judilibre(taxonomy_id="chamber") == {"chamber": "civ1"}
    fake_api.taxonomy.assert_called_once_with(
        taxonomy_id="chamber", key=None, value=None, context_value=None
    )


# ----------------------------------------------------------------------------
# rechercher_jurisprudence_judilibre
# ----------------------------------------------------------------------------


def test_rechercher_jurisprudence_surfaces_init_error() -> None:
    class _Boom:
        def __init__(self, sandbox: bool = False) -> None:
            raise RuntimeError("init failed")

    with patch.object(srv, "JudilibreAPI", _Boom):
        result = rechercher_jurisprudence_judilibre(recherche="x")

    assert isinstance(result, list)
    assert len(result) == 1
    assert "erreur" in result[0]


def test_rechercher_jurisprudence_wraps_scalars_in_lists() -> None:
    """Les paramètres scalaires (juridiction=`cc`) sont convertis en `["cc"]`."""
    fake_api = MagicMock()
    fake_api.search.return_value = []
    srv._clients["judilibre"] = fake_api

    rechercher_jurisprudence_judilibre(
        recherche="x",
        juridiction="cc",
        chambre="civ1",
        type_decision="arret",
        theme="civ",
        solution="cassation",
    )

    kwargs = fake_api.search.call_args.kwargs
    assert kwargs["jurisdiction"] == ["cc"]
    assert kwargs["chamber"] == ["civ1"]
    assert kwargs["type"] == ["arret"]
    assert kwargs["theme"] == ["civ"]
    assert kwargs["solution"] == ["cassation"]


def test_rechercher_jurisprudence_passes_none_for_unset_scalars() -> None:
    fake_api = MagicMock()
    fake_api.search.return_value = []
    srv._clients["judilibre"] = fake_api

    rechercher_jurisprudence_judilibre(recherche="x")

    kwargs = fake_api.search.call_args.kwargs
    assert kwargs["jurisdiction"] is None
    assert kwargs["chamber"] is None


# ----------------------------------------------------------------------------
# consulter_decision_judilibre
# ----------------------------------------------------------------------------


def test_consulter_decision_rejects_empty_id() -> None:
    assert consulter_decision_judilibre(decision_id="") == {
        "erreur": "L'ID de la décision ne peut pas être vide"
    }
    assert consulter_decision_judilibre(decision_id="   ") == {
        "erreur": "L'ID de la décision ne peut pas être vide"
    }


def test_consulter_decision_surfaces_init_error() -> None:
    class _Boom:
        def __init__(self, sandbox: bool = False) -> None:
            raise RuntimeError("init failed")

    with patch.object(srv, "JudilibreAPI", _Boom):
        result = consulter_decision_judilibre(decision_id="abc")

    assert isinstance(result, dict)
    assert "erreur" in result


def test_consulter_decision_delegates_to_client() -> None:
    fake_api = MagicMock()
    fake_api.consult.return_value = {"id": "abc", "text": "..."}
    srv._clients["judilibre"] = fake_api

    assert consulter_decision_judilibre(decision_id="abc") == {"id": "abc", "text": "..."}
    fake_api.consult.assert_called_once_with(decision_id="abc")
