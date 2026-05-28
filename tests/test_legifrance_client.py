"""Tests unitaires (mocks) pour `LegifranceAPI` — chemins offline + validations.

Le fichier `test_legifrance_client_integration.py` couvre les chemins avec PISTE
réel ; ces tests-ci utilisent des mocks de `_request` pour couvrir le code client
sans toucher au réseau, et tournent dans la gate offline du CI.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, patch

import pytest
import requests

from droit_francais_mcp.legifrance.client import LegifranceAPI

pytestmark = pytest.mark.unit


@pytest.fixture
def api(monkeypatch: pytest.MonkeyPatch) -> LegifranceAPI:
    """LegifranceAPI sandbox avec env vars factices (pas d'OAuth réel)."""
    monkeypatch.setenv("PISTE_SANDBOX_CLIENT_ID", "id")
    monkeypatch.setenv("PISTE_SANDBOX_CLIENT_SECRET", "secret")
    return LegifranceAPI(sandbox=True)


def _make_response(json_data: Any = None, text: str = "", status_code: int = 200) -> MagicMock:
    resp = MagicMock()
    resp.status_code = status_code
    resp.text = text
    resp.json.return_value = json_data
    resp.raise_for_status = MagicMock()
    return resp


# ----------------------------------------------------------------------------
# ping
# ----------------------------------------------------------------------------


def test_ping_returns_text_on_success(api: LegifranceAPI) -> None:
    with patch.object(LegifranceAPI, "_request", return_value=_make_response(text="pong\n")):
        assert api.ping() == "pong"


def test_ping_wraps_http_error_with_403_hint(api: LegifranceAPI) -> None:
    err_resp = MagicMock()
    err_resp.status_code = 403
    err_resp.text = "Forbidden body"
    http_err = requests.exceptions.HTTPError(response=err_resp)
    with patch.object(LegifranceAPI, "_request", side_effect=http_err):
        with pytest.raises(Exception, match="Erreur HTTP 403"):
            api.ping()


def test_ping_wraps_generic_request_exception(api: LegifranceAPI) -> None:
    with patch.object(
        LegifranceAPI,
        "_request",
        side_effect=requests.exceptions.ConnectionError("net down"),
    ):
        with pytest.raises(Exception, match="Erreur lors du ping"):
            api.ping()


# ----------------------------------------------------------------------------
# search — validations (toutes offline)
# ----------------------------------------------------------------------------


def test_search_requires_query(api: LegifranceAPI) -> None:
    with pytest.raises(ValueError, match="doit être fourni"):
        api.search(query=None)


def test_search_rejects_invalid_fond(api: LegifranceAPI) -> None:
    with pytest.raises(ValueError, match="Fond invalide"):
        api.search(query="x", fond="INVALID_FOND")


def test_search_rejects_invalid_search_type(api: LegifranceAPI) -> None:
    with pytest.raises(ValueError, match="Type de recherche invalide"):
        api.search(query="x", search_type="BOGUS_SEARCH")


def test_search_rejects_invalid_field_type(api: LegifranceAPI) -> None:
    with pytest.raises(ValueError, match="Type de champ invalide"):
        api.search(query="x", field_type="BOGUS_FIELD")


def test_search_rejects_invalid_operator(api: LegifranceAPI) -> None:
    with pytest.raises(ValueError, match="opérateur doit être"):
        api.search(query="x", operator="XOR")


# ----------------------------------------------------------------------------
# search — happy path
# ----------------------------------------------------------------------------


def test_search_returns_aucun_resultat_on_empty_response(api: LegifranceAPI) -> None:
    with patch.object(LegifranceAPI, "_request", return_value=_make_response(json_data={})):
        assert api.search(query="mariage", fond="JORF") == "Aucun résultat"


def test_search_returns_cleaned_payload_when_present(api: LegifranceAPI) -> None:
    raw = {
        "results": [
            {"id": "LEGIARTI42", "title": "Article 42", "ignored": "drop_me"},
        ],
        "_meta": "drop_me_too",
    }
    with patch.object(LegifranceAPI, "_request", return_value=_make_response(json_data=raw)):
        result = api.search(query="mariage", fond="JORF")
    assert isinstance(result, dict)
    assert "results" in result


def test_search_can_disable_cleaning(api: LegifranceAPI) -> None:
    """Avec `clean=False`, la réponse brute traverse intacte."""
    raw = {"results": [{"id": "x", "_ignored": "kept"}], "_meta": "kept"}
    with patch.object(LegifranceAPI, "_request", return_value=_make_response(json_data=raw)):
        result = api.search(query="x", fond="JORF", clean=False)
    assert result == raw


def test_search_wraps_http_error_with_status_code(api: LegifranceAPI) -> None:
    err_resp = MagicMock()
    err_resp.status_code = 500
    err_resp.json.return_value = {"error": "server fault"}
    err_resp.text = "{}"
    err_resp.headers = {}
    http_err = requests.exceptions.HTTPError(response=err_resp)
    with patch.object(LegifranceAPI, "_request", side_effect=http_err):
        with pytest.raises(Exception, match="Erreur HTTP 500"):
            api.search(query="x")


# ----------------------------------------------------------------------------
# consult — routes selon le préfixe de l'ID
# ----------------------------------------------------------------------------


@pytest.mark.parametrize(
    "id_prefix,endpoint_suffix",
    [
        ("LEGIARTI", "/consult/getArticle"),
        ("LEGISCTA", "/consult/getArticle"),
        ("LEGITEXT", "/consult/legiPart"),
        ("JURITEXT", "/consult/juri"),
        ("CNILTEXT", "/consult/cnil"),
        ("KALITEXT", "/consult/kaliText"),
        ("KALIARTI", "/consult/kaliArticle"),
        ("ACCOTEXT", "/consult/acco"),
        ("JORFXXX", "/consult/jorf"),  # fallback (pas de préfixe connu)
    ],
)
def test_consult_routes_by_prefix(api: LegifranceAPI, id_prefix: str, endpoint_suffix: str) -> None:
    captured: dict[str, Any] = {}

    def fake_request(method: str, url: str, *, json: Any = None, **_: Any) -> MagicMock:
        captured["url"] = url
        captured["params"] = json
        return _make_response(json_data={"data": "ok"})

    with patch.object(LegifranceAPI, "_request", side_effect=fake_request):
        api.consult(f"{id_prefix}000123456")

    assert endpoint_suffix in captured["url"]


def test_consult_strips_suffix_after_underscore(api: LegifranceAPI) -> None:
    """Les IDs `XXX_yyy` sont tronqués à la première underscore."""
    captured: dict[str, Any] = {}

    def fake_request(method: str, url: str, *, json: Any = None, **_: Any) -> MagicMock:
        captured["params"] = json
        return _make_response(json_data={"data": "ok"})

    with patch.object(LegifranceAPI, "_request", side_effect=fake_request):
        api.consult("LEGIARTI42_v2")
    assert "LEGIARTI42" in str(captured["params"])
    assert "_v2" not in str(captured["params"])


def test_consult_can_disable_cleaning(api: LegifranceAPI) -> None:
    raw = {"data": "raw", "_meta": "kept_when_disabled"}
    with patch.object(LegifranceAPI, "_request", return_value=_make_response(json_data=raw)):
        assert api.consult("LEGIARTI42", clean=False) == raw


def test_consult_wraps_request_exception(api: LegifranceAPI) -> None:
    with patch.object(
        LegifranceAPI,
        "_request",
        side_effect=requests.exceptions.ConnectionError("net down"),
    ):
        with pytest.raises(Exception, match="Erreur lors de la récupération"):
            api.consult("LEGIARTI42")
