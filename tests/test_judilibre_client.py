"""Tests unitaires (mocks) pour `JudilibreAPI` — chemins offline + validations."""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, patch

import pytest
import requests

from droit_francais_mcp.judilibre.client import JudilibreAPI

pytestmark = pytest.mark.unit


@pytest.fixture
def api(monkeypatch: pytest.MonkeyPatch) -> JudilibreAPI:
    monkeypatch.setenv("PISTE_SANDBOX_CLIENT_ID", "id")
    monkeypatch.setenv("PISTE_SANDBOX_CLIENT_SECRET", "secret")
    return JudilibreAPI(sandbox=True)


def _make_response(json_data: Any = None, status_code: int = 200) -> MagicMock:
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = json_data
    resp.raise_for_status = MagicMock()
    return resp


# ----------------------------------------------------------------------------
# search — validations
# ----------------------------------------------------------------------------


def test_search_rejects_page_size_above_50(api: JudilibreAPI) -> None:
    with pytest.raises(ValueError, match="page_size ne peut pas dépasser 50"):
        api.search(page_size=51)


def test_search_rejects_invalid_operator(api: JudilibreAPI) -> None:
    with pytest.raises(ValueError, match="operator doit être"):
        api.search(operator="XOR")


def test_search_rejects_invalid_sort(api: JudilibreAPI) -> None:
    with pytest.raises(ValueError, match="sort doit être"):
        api.search(sort="random")


def test_search_rejects_invalid_order(api: JudilibreAPI) -> None:
    with pytest.raises(ValueError, match="order doit être"):
        api.search(order="up")


# ----------------------------------------------------------------------------
# search — happy path + paramètres
# ----------------------------------------------------------------------------


def test_search_applies_default_jurisdictions(api: JudilibreAPI) -> None:
    """Sans `jurisdiction` explicite, la liste par défaut est appliquée."""
    captured: dict[str, Any] = {}

    def fake_request(method: str, url: str, *, params: Any = None, **_: Any) -> MagicMock:
        captured["params"] = params
        return _make_response(json_data={"results": []})

    with patch.object(JudilibreAPI, "_request", side_effect=fake_request):
        api.search(query="x")

    assert captured["params"]["jurisdiction"] == list(JudilibreAPI.DEFAULT_JURISDICTIONS)


def test_search_passes_optional_params_when_set(api: JudilibreAPI) -> None:
    captured: dict[str, Any] = {}

    def fake_request(method: str, url: str, *, params: Any = None, **_: Any) -> MagicMock:
        captured["params"] = params
        return _make_response(json_data={"results": []})

    with patch.object(JudilibreAPI, "_request", side_effect=fake_request):
        api.search(query="abc", theme=["civ"], chamber=["civ1"], date_start="2023-01-01")

    assert captured["params"]["query"] == "abc"
    assert captured["params"]["theme"] == ["civ"]
    assert captured["params"]["chamber"] == ["civ1"]
    assert captured["params"]["date_start"] == "2023-01-01"


def test_search_omits_unset_optional_params(api: JudilibreAPI) -> None:
    """Les paramètres `None`/falsy ne traversent pas vers la requête."""
    captured: dict[str, Any] = {}

    def fake_request(method: str, url: str, *, params: Any = None, **_: Any) -> MagicMock:
        captured["params"] = params
        return _make_response(json_data={"results": []})

    with patch.object(JudilibreAPI, "_request", side_effect=fake_request):
        api.search(query="x")

    assert "theme" not in captured["params"]
    assert "chamber" not in captured["params"]
    assert "date_start" not in captured["params"]


def test_search_wraps_request_exception(api: JudilibreAPI) -> None:
    with (
        patch.object(
            JudilibreAPI,
            "_request",
            side_effect=requests.exceptions.ConnectionError("net down"),
        ),
        pytest.raises(Exception, match="Erreur lors de la recherche JudiLibre"),
    ):
        api.search(query="x")


# ----------------------------------------------------------------------------
# consult
# ----------------------------------------------------------------------------


def test_consult_requires_non_empty_id(api: JudilibreAPI) -> None:
    with pytest.raises(ValueError, match="identifiant de la décision"):
        api.consult(decision_id="")


def test_consult_requires_non_whitespace_id(api: JudilibreAPI) -> None:
    with pytest.raises(ValueError, match="identifiant de la décision"):
        api.consult(decision_id="   ")


def test_consult_rejects_invalid_operator(api: JudilibreAPI) -> None:
    with pytest.raises(ValueError, match="operator doit être"):
        api.consult(decision_id="abc", operator="XOR")


def test_consult_passes_id_and_query(api: JudilibreAPI) -> None:
    captured: dict[str, Any] = {}

    def fake_request(method: str, url: str, *, params: Any = None, **_: Any) -> MagicMock:
        captured["params"] = params
        return _make_response(json_data={"results": [{"id": "abc"}]})

    with patch.object(JudilibreAPI, "_request", side_effect=fake_request):
        api.consult(decision_id="abc", query="mot", operator="and")

    assert captured["params"]["id"] == "abc"
    assert captured["params"]["query"] == "mot"
    assert captured["params"]["operator"] == "and"


def test_consult_wraps_request_exception(api: JudilibreAPI) -> None:
    with (
        patch.object(
            JudilibreAPI,
            "_request",
            side_effect=requests.exceptions.ConnectionError("net down"),
        ),
        pytest.raises(Exception, match="Erreur lors de la récupération de la décision"),
    ):
        api.consult(decision_id="abc")


# ----------------------------------------------------------------------------
# taxonomy
# ----------------------------------------------------------------------------


def test_taxonomy_returns_index_when_no_params(api: JudilibreAPI) -> None:
    """Sans aucun argument, taxonomy() retourne le dict de descriptions intégré."""
    result = api.taxonomy()
    assert isinstance(result, dict)
    assert "type" in result
    assert "jurisdiction" in result


def test_taxonomy_rejects_key_and_value_together(api: JudilibreAPI) -> None:
    with pytest.raises(ValueError, match="mutuellement exclusifs"):
        api.taxonomy(taxonomy_id="chamber", key="cc", value="cc")


def test_taxonomy_requires_id_with_key(api: JudilibreAPI) -> None:
    with pytest.raises(ValueError, match="taxonomy_id"):
        api.taxonomy(key="cc")


def test_taxonomy_calls_api_when_id_given(api: JudilibreAPI) -> None:
    captured: dict[str, Any] = {}

    def fake_request(method: str, url: str, *, params: Any = None, **_: Any) -> MagicMock:
        captured["params"] = params
        return _make_response(json_data={"result": {"ok": True}})

    with patch.object(JudilibreAPI, "_request", side_effect=fake_request):
        result = api.taxonomy(taxonomy_id="chamber")

    assert captured["params"]["id"] == "chamber"
    assert result == {"ok": True}


def test_taxonomy_wraps_request_exception_with_id(api: JudilibreAPI) -> None:
    with (
        patch.object(
            JudilibreAPI,
            "_request",
            side_effect=requests.exceptions.ConnectionError("net down"),
        ),
        pytest.raises(Exception, match="récupération de la taxonomie 'chamber'"),
    ):
        api.taxonomy(taxonomy_id="chamber")
