#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Client OAuth 2.0 partagé pour les API PISTE (Légifrance + JudiLibre).

Copyright (c) 2025 Jean-Michel Tanguy
Licensed under the MIT License (see LICENSE file)
"""

import os
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import requests
from dotenv import load_dotenv

PISTE_SANDBOX_OAUTH_URL = "https://sandbox-oauth.piste.gouv.fr/api/oauth/token"
PISTE_PROD_OAUTH_URL = "https://oauth.piste.gouv.fr/api/oauth/token"
PISTE_SANDBOX_API_URL = "https://sandbox-api.piste.gouv.fr"
PISTE_PROD_API_URL = "https://api.piste.gouv.fr"

PISTE_HTTP_TIMEOUT = 30  # seconds; applied to every PISTE request

ERR_403_MESSAGE = (
    "Erreur 403 Forbidden - Causes possibles:\n"
    "1. Votre compte n'est pas abonné à cette API PISTE\n"
    "2. Les permissions nécessaires ne sont pas activées\n"
    "3. Vérifiez votre abonnement sur https://piste.gouv.fr/"
)


class PisteOAuthClient:
    """
    Base class pour les clients PISTE — gère l'authentification OAuth 2.0
    Client-Credentials, la mise en cache du token, et les en-têtes API.

    Les sous-classes (LegifranceAPI, JudilibreAPI) définissent `api_url`
    en concaténant `self.base_url` avec leur chemin spécifique.
    """

    API_LABEL: str = "PISTE"  # surcharger dans les sous-classes pour les messages d'erreur

    def __init__(self, sandbox: bool = True):
        """
        Initialise le client OAuth.

        Args:
            sandbox: True pour l'environnement sandbox, False pour la production.

        Raises:
            ValueError: Si les identifiants PISTE correspondants ne sont pas définis dans .env.
        """
        load_dotenv(verbose=False)
        if sandbox:
            self.client_id = os.getenv("PISTE_SANDBOX_CLIENT_ID")
            self.client_secret = os.getenv("PISTE_SANDBOX_CLIENT_SECRET")
            self.token_url = PISTE_SANDBOX_OAUTH_URL
            self.base_url = PISTE_SANDBOX_API_URL
            env_var_id, env_var_secret = "PISTE_SANDBOX_CLIENT_ID", "PISTE_SANDBOX_CLIENT_SECRET"
            label = "Sandbox"
        else:
            self.client_id = os.getenv("PISTE_CLIENT_ID")
            self.client_secret = os.getenv("PISTE_CLIENT_SECRET")
            self.token_url = PISTE_PROD_OAUTH_URL
            self.base_url = PISTE_PROD_API_URL
            env_var_id, env_var_secret = "PISTE_CLIENT_ID", "PISTE_CLIENT_SECRET"
            label = "Production"

        if not self.client_id or not self.client_secret:
            raise ValueError(
                f"Les identifiants PISTE {label} sont manquants. "
                f"Veuillez définir {env_var_id} et {env_var_secret} "
                "dans votre fichier .env. "
                "Consultez .env.example pour un exemple de configuration."
            )

        self.access_token: Optional[str] = None
        self.token_expires_at: Optional[datetime] = None

    def get_access_token(self) -> str:
        """
        Récupère un access token via OAuth 2.0 Client-Credentials.

        Le token est mis en cache jusqu'à 60 s avant son expiration.

        Returns:
            Le token Bearer.

        Raises:
            Exception: Si l'obtention du token échoue.
        """
        if self.access_token and self.token_expires_at and datetime.now() < self.token_expires_at:
            return self.access_token

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        }
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": "openid",
        }

        try:
            response = requests.post(
                self.token_url,
                headers=headers,
                data=data,
                timeout=PISTE_HTTP_TIMEOUT,
            )
            response.raise_for_status()

            token_data = response.json()
            access_token: str = token_data["access_token"]
            self.access_token = access_token

            expires_in = token_data.get("expires_in", 3600)
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)

            return access_token

        except requests.exceptions.RequestException as e:
            raise Exception(f"Erreur lors de l'obtention du token {self.API_LABEL}: {e}")

    def _get_api_headers(self) -> Dict[str, str]:
        """En-têtes standard pour les appels API PISTE authentifiés."""
        token = self.get_access_token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _request(
        self,
        method: str,
        url: str,
        *,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None,
    ) -> requests.Response:
        """
        Appel HTTP authentifié avec timeout standard.

        Lève `requests.exceptions.HTTPError` pour 4xx/5xx (les appelants gèrent
        le 403 de manière spécifique). Les autres `RequestException` sont
        propagées et habituellement converties en `Exception` par les appelants.
        """
        merged_headers = self._get_api_headers()
        if headers:
            merged_headers.update(headers)
        response = requests.request(
            method=method,
            url=url,
            headers=merged_headers,
            params=params,
            json=json,
            data=data,
            timeout=PISTE_HTTP_TIMEOUT,
        )
        response.raise_for_status()
        return response
