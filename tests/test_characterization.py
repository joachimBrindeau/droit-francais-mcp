#!/usr/bin/env python3
"""
Tests de caractérisation MCP — pins comportementaux pour la couche serveur.

Ces tests fixent le contrat observable du serveur MCP (nombre d'outils,
décorateur safe_mcp_tool, mécanisme _init_errors, frozensets de fonds) afin
de détecter toute régression introduite par les boucliers structurels (déplacement
vers src/, renommage de modules, relocation des tests).
"""

from __future__ import annotations

import logging
from typing import Any
from unittest.mock import patch

import pytest

pytestmark = pytest.mark.unit


# ----------------------------------------------------------------------------
# safe_mcp_tool — contrat de retour & journalisation
# ----------------------------------------------------------------------------


def test_safe_mcp_tool_returns_deep_copy_on_error() -> None:
    """Une mutation du retour d'erreur ne doit pas fuir vers l'appel suivant."""
    from droit_francais_mcp.server import safe_mcp_tool

    payload = {"erreur": "boom", "details": []}

    @safe_mcp_tool("label", on_error_return=payload)
    def fails() -> Any:
        raise RuntimeError("simulated")

    first = fails()
    assert first == {"erreur": "boom", "details": []}
    # Mute le retour
    first["details"].append("MUTATED")
    first["erreur"] = "MUTATED"
    second = fails()
    # L'appel suivant doit voir le payload original
    assert second == {"erreur": "boom", "details": []}, (
        "safe_mcp_tool a renvoyé un objet partagé — la mutation du premier appel "
        "a fui vers le second"
    )


def test_safe_mcp_tool_logs_exception_with_traceback(caplog: pytest.LogCaptureFixture) -> None:
    """L'exception doit être journalisée via logger.exception (avec traceback)."""
    from droit_francais_mcp.server import safe_mcp_tool

    @safe_mcp_tool("test-label", on_error_return=None)
    def fails() -> Any:
        raise ValueError("payload de test")

    with caplog.at_level(logging.ERROR, logger="droit_francais_mcp.server"):
        assert fails() is None

    matching = [r for r in caplog.records if "test-label" in r.message]
    assert matching, "safe_mcp_tool n'a pas journalisé l'étiquette d'erreur"
    # logger.exception attache exc_info ; logger.error simple ne le ferait pas.
    assert any(r.exc_info is not None for r in matching), (
        "safe_mcp_tool doit utiliser logger.exception (avec traceback) — la "
        "stack trace est manquante dans les enregistrements de log"
    )


def test_safe_mcp_tool_passthrough_on_success() -> None:
    """En l'absence d'exception, la valeur de retour est intacte."""
    from droit_francais_mcp.server import safe_mcp_tool

    @safe_mcp_tool("label", on_error_return={"erreur": "fallback"})
    def ok() -> Any:
        return {"data": [1, 2, 3]}

    assert ok() == {"data": [1, 2, 3]}


# ----------------------------------------------------------------------------
# _init_errors — capture des erreurs d'initialisation
# ----------------------------------------------------------------------------


def test_init_errors_dict_exists() -> None:
    """Le module expose un dict module-level _init_errors."""
    from droit_francais_mcp import server as srv

    assert hasattr(srv, "_init_errors"), (
        "Le mécanisme _init_errors doit être exposé au niveau module"
    )
    assert isinstance(srv._init_errors, dict)


def test_safe_init_captures_exception_message() -> None:
    """_safe_init doit capturer l'exception et la stocker dans _init_errors."""
    from droit_francais_mcp.server import _init_errors, _safe_init

    class _Boom:
        def __init__(self, sandbox: bool = True) -> None:  # noqa: D401
            raise ValueError("PISTE_CLIENT_ID manquant")

    _init_errors.pop("test_key", None)
    result = _safe_init(_Boom, "Test", "test_key")
    assert result is None
    assert "test_key" in _init_errors
    assert "PISTE_CLIENT_ID manquant" in _init_errors["test_key"]
    _init_errors.pop("test_key", None)


def test_lazy_accessors_memoize(monkeypatch: pytest.MonkeyPatch) -> None:
    """get_legifrance_api / get_judilibre_api ne construisent qu'une fois."""
    from droit_francais_mcp import server as srv

    construction_count = {"value": 0}

    class _Counter:
        def __init__(self, sandbox: bool = False) -> None:  # noqa: D401
            construction_count["value"] += 1

    srv.reset_clients()
    monkeypatch.setattr(srv, "LegifranceAPI", _Counter)

    srv.get_legifrance_api()
    srv.get_legifrance_api()
    srv.get_legifrance_api()
    assert construction_count["value"] == 1, (
        f"L'accesseur paresseux doit mémoïser : {construction_count['value']} constructions"
    )
    srv.reset_clients()


def test_lazy_accessors_caches_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    """Une init qui échoue doit être mémoïsée (pas de retry à chaque appel)."""
    from droit_francais_mcp import server as srv

    attempts = {"value": 0}

    class _Boom:
        def __init__(self, sandbox: bool = False) -> None:  # noqa: D401
            attempts["value"] += 1
            raise RuntimeError("init failed")

    srv.reset_clients()
    monkeypatch.setattr(srv, "LegifranceAPI", _Boom)

    assert srv.get_legifrance_api() is None
    assert srv.get_legifrance_api() is None
    assert srv.get_legifrance_api() is None
    assert attempts["value"] == 1, (
        f"Une init en échec doit être mémoïsée : {attempts['value']} tentatives"
    )
    assert "legifrance" in srv._init_errors
    srv.reset_clients()


# ----------------------------------------------------------------------------
# Couche MCP — pin du nombre d'outils enregistrés et de leur nommage
# ----------------------------------------------------------------------------


EXPECTED_TOOL_NAMES = frozenset(
    {
        "rechercher_legifrance",
        "consulter_legifrance",
        "ping_legifrance",
        "obtenir_taxonomie_judilibre",
        "rechercher_jurisprudence_judilibre",
        "consulter_decision_judilibre",
    }
)


def _registered_tool_names(mcp: Any) -> frozenset[str]:
    """Récupère les noms d'outils enregistrés en s'adaptant à l'API FastMCP courante."""
    # FastMCP 2.10+ : list_tools() coroutine ; 2.12+ : _tool_manager._tools dict.
    candidates = ("_tools", "_tool_manager")
    for attr in candidates:
        obj = getattr(mcp, attr, None)
        if obj is None:
            continue
        if isinstance(obj, dict):
            return frozenset(obj.keys())
        inner = getattr(obj, "_tools", None)
        if isinstance(inner, dict):
            return frozenset(inner.keys())
    # Fallback : asynchrone (non utilisé ici)
    raise AssertionError(
        f"Impossible de récupérer les outils enregistrés via FastMCP : tentatives {candidates}"
    )


def test_mcp_tool_count_and_names() -> None:
    """Le serveur MCP enregistre exactement les 5 outils attendus."""
    from droit_francais_mcp.server import mcp

    tool_names = _registered_tool_names(mcp)
    assert tool_names == EXPECTED_TOOL_NAMES, (
        f"Dérive du nombre/nom d'outils MCP : attendu={sorted(EXPECTED_TOOL_NAMES)} "
        f"obtenu={sorted(tool_names)}"
    )


# ----------------------------------------------------------------------------
# Frozensets de fonds — pin des nouvelles SSOT (CODE_FONDS, VIGUEUR_DEFAULT_FONDS)
# ----------------------------------------------------------------------------


def test_code_fonds_frozenset() -> None:
    """CODE_FONDS doit contenir exactement les fonds acceptant TEXT_NOM_CODE."""
    from droit_francais_mcp.legifrance.query_builder import LegifranceQueryBuilder

    assert frozenset({"CODE_ETAT", "CODE_DATE"}) == LegifranceQueryBuilder.CODE_FONDS


def test_vigueur_default_fonds_frozenset() -> None:
    """VIGUEUR_DEFAULT_FONDS doit lister les fonds où ARTICLE_LEGAL_STATUS=VIGUEUR est imposé par défaut."""
    from droit_francais_mcp.legifrance.query_builder import LegifranceQueryBuilder

    assert (
        frozenset(
            {
                "JORF",
                "CODE_ETAT",
                "CODE_DATE",
                "LODA_DATE",
                "LODA_ETAT",
            }
        )
        == LegifranceQueryBuilder.VIGUEUR_DEFAULT_FONDS
    )


# ----------------------------------------------------------------------------
# PisteOAuthClient._request — pin du chemin d'appel HTTP partagé
# ----------------------------------------------------------------------------


def test_piste_oauth_client_request_uses_shared_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    """Tous les appels HTTP des sous-classes doivent passer par _request — qui applique le timeout PISTE_HTTP_TIMEOUT."""
    from droit_francais_mcp.piste.auth import PISTE_HTTP_TIMEOUT

    captured: dict = {}

    class _FakeResp:
        status_code = 200
        text = "pong"

        def raise_for_status(self) -> None:
            return None

        def json(self) -> Any:
            return {}

    def _fake_request(**kwargs: Any) -> _FakeResp:
        captured.update(kwargs)
        return _FakeResp()

    import requests as _req

    monkeypatch.setattr(_req, "request", _fake_request)

    # Bypass auth pour le test du wrapper HTTP isolément.
    from droit_francais_mcp.piste.auth import PisteOAuthClient

    with patch.object(
        PisteOAuthClient, "_get_api_headers", return_value={"Authorization": "Bearer T"}
    ):
        # On ne peut pas instancier PisteOAuthClient sans creds — on lui mock __init__.
        client = PisteOAuthClient.__new__(PisteOAuthClient)
        response = client._request("GET", "https://example.invalid/probe")

    assert response.text == "pong"
    assert captured.get("timeout") == PISTE_HTTP_TIMEOUT, (
        f"_request doit appliquer le timeout PISTE_HTTP_TIMEOUT — obtenu {captured.get('timeout')!r}"
    )
    assert captured.get("method") == "GET"
    assert captured.get("url") == "https://example.invalid/probe"
