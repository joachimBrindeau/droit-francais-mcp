#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Client pour l'API Légifrance via PISTE.
Documentation de l'API Légifrance : https://piste.gouv.fr/api-dila-legifrance/

Copyright (c) 2025 Jean-Michel Tanguy
Licensed under the MIT License (see LICENSE file)

Remarques :
   Certaines parties de ce code ont été développées avec l’aide de Vibe Coding
   et d’outils d’intelligence artificielle.
"""

from datetime import date
from typing import Any, ClassVar, Dict, FrozenSet, List, Optional

import requests

from api_legifrance_query_builder import LegifranceQueryBuilder
from piste_auth import ERR_403_MESSAGE, PisteOAuthClient
from piste_utils import recursive_filter


class LegifranceAPI(PisteOAuthClient):
    """
    Client pour l'API Légifrance.
    """

    _API_LABEL = "Légifrance"
    _ALLOWED_KEYS: ClassVar[FrozenSet[str]] = frozenset({
        "id", "title", "text", "values", "datePublication", "startDate",
        "origine", "nature", "natureJuridiction", "solution", "numeroAffaire",
        "president", "avocats", "titre", "texte", "juridiction", "content",
    })
    _MAX_DEPTH: ClassVar[int] = 8

    def __init__(self, sandbox: bool = True):
        super().__init__(sandbox=sandbox)
        self.api_url = f"{self.base_url}/dila/legifrance/lf-engine-app"

    def ping(self) -> str:
        """
        Teste la connexion à l'endpoint de recherche avec un simple ping.

        Returns:
            "pong" si la connexion réussit.

        Raises:
            Exception: Si le ping échoue.
        """
        endpoint = f"{self.api_url}/search/ping"
        try:
            response = self._request("GET", endpoint)
            return response.text.strip()
        except requests.exceptions.HTTPError as e:
            error_msg = f"Erreur HTTP {e.response.status_code} lors du ping"
            if e.response.status_code == 403:
                error_msg += f"\n⚠️ {ERR_403_MESSAGE}"
            try:
                error_msg += f"\nRéponse: {e.response.text[:200]}"
            except Exception:
                pass
            raise Exception(error_msg)
        except requests.exceptions.RequestException as e:
            raise Exception(f"Erreur lors du ping: {e}")

    def search(
        self,
        query: Optional[str] = None,
        fond: Optional[str] = "ALL",
        field_type: str = "ALL",
        search_type: str = "TOUS_LES_MOTS_DANS_UN_CHAMP",
        code: Optional[str] = None,
        filters: Optional[Dict[str, List[str]]] = None,
        date_start: Optional[str] = None,
        date_end: Optional[str] = None,
        page_number: int = 0,
        page_size: int = 10,
        sort: Optional[str] = None,
        operator: str = "ET",
        advanced_search: bool = False,
        clean: bool = True,
    ) -> Any:
        """
        Effectue une recherche dans l'API Légifrance.

        Args:
            query (str): Terme(s) de recherche textuelle. Obligatoire.
            fond (str): Fonds de recherche (ALL par défaut).
                Valeurs possibles: voir `LegifranceQueryBuilder.FONDS`.
            field_type (str): Type de champ (ALL par défaut).
                Valeurs possibles: voir `LegifranceQueryBuilder.TYPE_CHAMP`.
            search_type (str): Type de recherche. Défaut: "TOUS_LES_MOTS_DANS_UN_CHAMP".
                Valeurs possibles: voir `LegifranceQueryBuilder.TYPE_RECHERCHE`.
            code (str): Nom du code (uniquement pour CODE_ETAT/CODE_DATE).
            filters (Dict[str, List[str]]): Filtres par facettes (NATURE, ETAT_JURIDIQUE, …).
            date_start (str): Date de début (YYYY-MM-DD). Seulement pour les fonds
                qui supportent les filtres date (voir LegifranceQueryBuilder.DATE_FILTER_FACETTES).
            date_end (str): Date de fin (YYYY-MM-DD). Nécessite date_start.
            page_number (int): Numéro de page. Défaut: 0.
            page_size (int): Résultats par page (max 50). Défaut: 10.
            sort (str): Ordre de tri. Voir LegifranceQueryBuilder.set_sort.
            operator (str): Opérateur global entre champs ("ET" ou "OU"). Défaut: "ET".
            advanced_search (bool): Active le mode recherche avancée. Défaut: False.
            clean (bool): Si True, nettoie la réponse pour ne conserver que les clés utiles.

        Returns:
            Les résultats de la recherche (liste, dict, ou "Aucun résultat").

        Raises:
            ValueError: Si query est absent ou si un paramètre n'est pas valide.
            Exception: Si la requête HTTP échoue.
        """
        endpoint = f"{self.api_url}/search"

        if query is None:
            raise ValueError("Le paramètre 'recherche' doit être fourni")

        query_builder = LegifranceQueryBuilder()

        fond = fond or "ALL"
        if fond not in query_builder.FONDS:
            raise ValueError(
                f"Fond invalide. Utilisez une des valeurs: {sorted(query_builder.FONDS)}"
            )
        query_builder.set_fond(fond)

        if search_type not in query_builder.TYPE_RECHERCHE:
            raise ValueError(
                f"Type de recherche invalide. Utilisez une des valeurs: {sorted(query_builder.TYPE_RECHERCHE)}"
            )
        if field_type not in query_builder.TYPE_CHAMP:
            raise ValueError(
                f"Type de champ invalide. Utilisez une des valeurs: {sorted(query_builder.TYPE_CHAMP)}"
            )

        critere = query_builder.create_criteria(query, search_type)
        query_builder.add_field(field_type, [critere])

        if fond in LegifranceQueryBuilder.CODE_FONDS and code:
            query_builder.add_filtre("TEXT_NOM_CODE", [code])

        if filters:
            for facette, valeurs in filters.items():
                query_builder.add_filtre(facette, valeurs)

        if date_start:
            query_builder.add_dates(date_start, date_end)

        if operator not in ("ET", "OU"):
            raise ValueError("L'opérateur doit être 'ET' ou 'OU'")
        query_builder.set_operator(operator)

        if advanced_search:
            query_builder.set_advanced_search(True)

        query_builder.set_pagination(page_number, page_size)

        if sort:
            query_builder.set_sort(sort)

        if fond in LegifranceQueryBuilder.VIGUEUR_DEFAULT_FONDS:
            query_builder.add_filtre("ARTICLE_LEGAL_STATUS", ["VIGUEUR"])

        payload = query_builder.build()

        try:
            response = self._request("POST", endpoint, json=payload)
            data = response.json()
            summary = self.clean(data) if clean else data
            return summary if summary else "Aucun résultat"

        except requests.exceptions.HTTPError as e:
            error_msg = f"Erreur HTTP {e.response.status_code}: {e}"
            if e.response.status_code == 403:
                error_msg += f"\n\n⚠️ {ERR_403_MESSAGE}"
            try:
                error_details = e.response.json()
                if isinstance(error_details, dict):
                    error_msg += f"\n\nDétails de la réponse API: {error_details}"
                    if "message" in error_details:
                        error_msg += f"\nMessage: {error_details['message']}"
                    if "error" in error_details:
                        error_msg += f"\nErreur: {error_details['error']}"
            except Exception:
                error_msg += f"\n\nRéponse brute: {e.response.text[:500]}"
            error_msg += f"\n\nEn-têtes de réponse: {dict(e.response.headers)}"
            raise Exception(f"Erreur lors de la recherche: {error_msg}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Erreur lors de la recherche: {e}")

    def consult(self, id_: str, clean: bool = True) -> Any:
        """
        Récupère un article ou texte spécifique depuis Légifrance.

        Args:
            id_: Identifiant (LEGIARTI…, LEGITEXT…, JURITEXT…, CNILTEXT…, KALITEXT…,
                KALIARTI…, ACCOTEXT…, ou autre pour JORF).
            clean: Si True, nettoie la réponse pour ne conserver que les clés utiles.

        Returns:
            Les données de l'article/texte.

        Raises:
            Exception: Si la requête HTTP échoue.
        """
        if "_" in id_:
            id_ = id_.split("_")[0]

        if id_.startswith("LEGIARTI") or id_.startswith("LEGISCTA"):
            endpoint = f"{self.api_url}/consult/getArticle"
            params = {"id": id_}
        elif id_.startswith("LEGITEXT"):
            endpoint = f"{self.api_url}/consult/legiPart"
            params = {"textId": id_, "date": date.today().isoformat()}
        elif id_.startswith("JURITEXT"):
            endpoint = f"{self.api_url}/consult/juri"
            params = {"textId": id_}
        elif id_.startswith("CNILTEXT"):
            endpoint = f"{self.api_url}/consult/cnil"
            params = {"textId": id_}
        elif id_.startswith("KALITEXT"):
            endpoint = f"{self.api_url}/consult/kaliText"
            params = {"id": id_}
        elif id_.startswith("KALIARTI"):
            endpoint = f"{self.api_url}/consult/kaliArticle"
            params = {"id": id_}
        elif id_.startswith("ACCOTEXT"):
            endpoint = f"{self.api_url}/consult/acco"
            params = {"id": id_}
        else:
            endpoint = f"{self.api_url}/consult/jorf"
            params = {"textCid": id_}

        try:
            response = self._request("POST", endpoint, json=params)
            api_response = response.json()
            return self.clean(api_response) if clean else api_response
        except requests.exceptions.RequestException as e:
            raise Exception(f"Erreur lors de la récupération de l'article: {e}")

    def clean(self, x: Any) -> Optional[Any]:
        """
        Nettoie une réponse Légifrance via le helper partagé `recursive_filter`.
        """
        return recursive_filter(x, self._ALLOWED_KEYS, max_depth=self._MAX_DEPTH)
