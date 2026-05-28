"""Tests unitaires pour `piste.auth.PisteOAuthClient` (chemins d'init et token caching)."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any
from unittest.mock import patch

import pytest

from droit_francais_mcp.piste.auth import (
    PISTE_HTTP_TIMEOUT,
    PISTE_PROD_API_URL,
    PISTE_PROD_OAUTH_URL,
    PISTE_SANDBOX_API_URL,
    PISTE_SANDBOX_OAUTH_URL,
    PisteOAuthClient,
)

pytestmark = pytest.mark.unit


def test_sandbox_init_picks_sandbox_urls(monkeypatch: pytest.MonkeyPatch) -> None:
    """Le mode sandbox lit `PISTE_SANDBOX_*` et utilise les URL sandbox."""
    monkeypatch.setenv("PISTE_SANDBOX_CLIENT_ID", "sandbox-id")
    monkeypatch.setenv("PISTE_SANDBOX_CLIENT_SECRET", "sandbox-secret")
    client = PisteOAuthClient(sandbox=True)
    assert client.client_id == "sandbox-id"
    assert client.client_secret == "sandbox-secret"
    assert client.token_url == PISTE_SANDBOX_OAUTH_URL
    assert client.base_url == PISTE_SANDBOX_API_URL


def test_prod_init_picks_prod_urls(monkeypatch: pytest.MonkeyPatch) -> None:
    """Le mode production lit `PISTE_CLIENT_*` et utilise les URL prod."""
    monkeypatch.setenv("PISTE_CLIENT_ID", "prod-id")
    monkeypatch.setenv("PISTE_CLIENT_SECRET", "prod-secret")
    client = PisteOAuthClient(sandbox=False)
    assert client.client_id == "prod-id"
    assert client.client_secret == "prod-secret"
    assert client.token_url == PISTE_PROD_OAUTH_URL
    assert client.base_url == PISTE_PROD_API_URL


def test_sandbox_missing_creds_raises_valueerror(monkeypatch: pytest.MonkeyPatch) -> None:
    """Sans `PISTE_SANDBOX_CLIENT_ID/SECRET`, l'init lève `ValueError`."""
    # `load_dotenv` est appelé dans __init__ et re-peuple les vars depuis .env ;
    # on le neutralise pour le test pour pouvoir vraiment supprimer les vars.
    monkeypatch.setattr("droit_francais_mcp.piste.auth.load_dotenv", lambda **_: None)
    monkeypatch.delenv("PISTE_SANDBOX_CLIENT_ID", raising=False)
    monkeypatch.delenv("PISTE_SANDBOX_CLIENT_SECRET", raising=False)
    with pytest.raises(ValueError, match="identifiants PISTE Sandbox sont manquants"):
        PisteOAuthClient(sandbox=True)


def test_prod_missing_creds_raises_valueerror(monkeypatch: pytest.MonkeyPatch) -> None:
    """Sans `PISTE_CLIENT_ID/SECRET`, l'init prod lève `ValueError`."""
    monkeypatch.setattr("droit_francais_mcp.piste.auth.load_dotenv", lambda **_: None)
    monkeypatch.delenv("PISTE_CLIENT_ID", raising=False)
    monkeypatch.delenv("PISTE_CLIENT_SECRET", raising=False)
    with pytest.raises(ValueError, match="identifiants PISTE Production sont manquants"):
        PisteOAuthClient(sandbox=False)


def test_get_access_token_caches_token(monkeypatch: pytest.MonkeyPatch) -> None:
    """Un token valide en cache évite un nouvel appel HTTP."""
    monkeypatch.setenv("PISTE_SANDBOX_CLIENT_ID", "id")
    monkeypatch.setenv("PISTE_SANDBOX_CLIENT_SECRET", "secret")
    client = PisteOAuthClient(sandbox=True)
    client.access_token = "cached-token"
    client.token_expires_at = datetime.now() + timedelta(seconds=3600)

    with patch("droit_francais_mcp.piste.auth.requests.post") as post:
        token = client.get_access_token()

    assert token == "cached-token"
    post.assert_not_called()


def test_get_access_token_refreshes_when_expired(monkeypatch: pytest.MonkeyPatch) -> None:
    """Un token expiré déclenche un appel HTTP."""
    monkeypatch.setenv("PISTE_SANDBOX_CLIENT_ID", "id")
    monkeypatch.setenv("PISTE_SANDBOX_CLIENT_SECRET", "secret")
    client = PisteOAuthClient(sandbox=True)
    client.access_token = "stale-token"
    client.token_expires_at = datetime.now() - timedelta(seconds=10)

    fake_response = type(
        "R",
        (),
        {
            "raise_for_status": lambda self: None,
            "json": lambda self: {"access_token": "new-token", "expires_in": 3600},
        },
    )()
    with patch("droit_francais_mcp.piste.auth.requests.post", return_value=fake_response) as post:
        token = client.get_access_token()

    assert token == "new-token"
    post.assert_called_once()


def test_request_applies_timeout_and_method(monkeypatch: pytest.MonkeyPatch) -> None:
    """`_request` applique PISTE_HTTP_TIMEOUT et la bonne méthode HTTP."""
    monkeypatch.setenv("PISTE_SANDBOX_CLIENT_ID", "id")
    monkeypatch.setenv("PISTE_SANDBOX_CLIENT_SECRET", "secret")
    client = PisteOAuthClient(sandbox=True)

    captured: dict[str, Any] = {}

    class _Resp:
        status_code = 200

        def raise_for_status(self) -> None:
            return None

    def _fake_request(**kwargs: Any) -> _Resp:
        captured.update(kwargs)
        return _Resp()

    with (
        patch.object(PisteOAuthClient, "_get_api_headers", return_value={"H": "v"}),
        patch("droit_francais_mcp.piste.auth.requests.request", _fake_request),
    ):
        response = client._request("POST", "https://example.invalid/x", json={"a": 1})

    assert response.status_code == 200
    assert captured.get("method") == "POST"
    assert captured.get("url") == "https://example.invalid/x"
    assert captured.get("timeout") == PISTE_HTTP_TIMEOUT
    assert captured.get("json") == {"a": 1}
