#!/usr/bin/env python3
"""
Client pour l'API JudiLibre via PISTE.
Documentation de l'API JudiLibre : https://piste.gouv.fr/api-judilibre/

Copyright (c) 2025 Jean-Michel Tanguy
Licensed under the MIT License (see LICENSE file)

Remarques :
   Certaines parties de ce code ont été développées avec l’aide de Vibe Coding
   et d’outils d’intelligence artificielle.
"""

from typing import Any, ClassVar, Dict, FrozenSet, List

import requests

from droit_francais_mcp.piste.auth import PisteOAuthClient
from droit_francais_mcp.piste.filters import recursive_filter


class JudilibreAPI(PisteOAuthClient):
    """
    Client OAuth pour l'API JudiLibre.
    """

    API_LABEL = "Judilibre"
    ALLOWED_KEYS: ClassVar[FrozenSet[str]] = frozenset({
        "text", "id", "jurisdiction", "chamber", "formation", "type", "theme",
        "publication", "decision_date", "solution", "score",
    })
    MAX_DEPTH: ClassVar[int] = 5

    DEFAULT_JURISDICTIONS: ClassVar[tuple[str, ...]] = ("cc", "ca", "tj", "tcom")
    VALID_OPERATORS: ClassVar[frozenset[str]] = frozenset({"or", "and", "exact"})
    VALID_SORTS: ClassVar[frozenset[str]] = frozenset({"score", "scorepub", "date"})
    VALID_ORDERS: ClassVar[frozenset[str]] = frozenset({"asc", "desc"})

    def __init__(self, sandbox: bool = True):
        super().__init__(sandbox=sandbox)
        self.api_url = f"{self.base_url}/cassation/judilibre/v1.0"

    def search(
        self,
        query: str | None = None,
        field: List[str] | None = None,
        operator: str = "and",
        type: List[str] | None = None,
        theme: List[str] | None = None,
        chamber: List[str] | None = None,
        formation: List[str] | None = None,
        jurisdiction: List[str] | None = None,
        location: List[str] | None = None,
        publication: List[str] | None = None,
        solution: List[str] | None = None,
        date_start: str | None = None,
        date_end: str | None = None,
        sort: str = "scorepub",
        order: str = "desc",
        page_size: int = 50,
        page: int = 0,
        resolve_references: bool = True,
        withFileOfType: List[str] | None = None,
        particularInterest: bool = False,
    ) -> Any:
        """
        Effectue une recherche dans la base JudiLibre (décisions de justice).

        Args:
            query: Termes de recherche.
            field: Champs/zones ciblés (motivations, dispositif, …).
            operator: "or", "and" (défaut), ou "exact".
            type: Filtre par nature de décision (arret, qpc, ordonnance, …).
            theme: Filtre par matière.
            chamber: Filtre par chambre — utiliser les CLÉS (pl, mi, civ1, …).
            formation: Filtre par formation.
            jurisdiction: Filtre par juridiction. Par défaut: toutes les juridictions
                ("cc", "ca", "tj", "tcom").
            location: Filtre par code du siège (ca_paris, tj75101, …).
            publication: Filtre par niveau de publication.
            solution: Filtre par type de solution.
            date_start / date_end: Intervalle de dates (YYYY-MM-DD).
            sort: "score", "scorepub" (défaut), ou "date".
            order: "asc" ou "desc" (défaut).
            page_size: Nombre de résultats par page (max 50).
            page: Numéro de page (0-indexé).
            resolve_references: Si True, ajoute les intitulés complets aux références.
            withFileOfType: Filtre par type de documents associés.
            particularInterest: Restreint aux décisions à intérêt particulier.

        Returns:
            Résultats paginés.

        Raises:
            ValueError: Si un paramètre n'est pas valide.
            Exception: Si la requête HTTP échoue.
        """
        if page_size > 50:
            raise ValueError("page_size ne peut pas dépasser 50")
        if operator not in self.VALID_OPERATORS:
            raise ValueError("operator doit être 'or', 'and' ou 'exact'")
        if sort not in self.VALID_SORTS:
            raise ValueError("sort doit être 'score', 'scorepub' ou 'date'")
        if order not in self.VALID_ORDERS:
            raise ValueError("order doit être 'asc' ou 'desc'")

        endpoint = f"{self.api_url}/search"

        if jurisdiction is None:
            jurisdiction = list(self.DEFAULT_JURISDICTIONS)

        params: Dict[str, Any] = {
            "operator": operator,
            "sort": sort,
            "order": order,
            "page_size": page_size,
            "page": page,
            "resolve_references": "true" if resolve_references else "false",
            "particularInterest": "true" if particularInterest else "false",
        }

        for name, value in {
            "query": query,
            "field": field,
            "type": type,
            "theme": theme,
            "chamber": chamber,
            "formation": formation,
            "jurisdiction": jurisdiction,
            "location": location,
            "publication": publication,
            "solution": solution,
            "date_start": date_start,
            "date_end": date_end,
            "withFileOfType": withFileOfType,
        }.items():
            if value:
                params[name] = value

        try:
            response = self._request("GET", endpoint, params=params)
            return self.clean(response.json())
        except requests.exceptions.RequestException as e:
            raise Exception(f"Erreur lors de la recherche JudiLibre: {e}")

    def consult(
        self,
        decision_id: str,
        resolve_references: bool = False,
        query: str | None = None,
        operator: str = "and",
    ) -> Any:
        """
        Récupère le contenu intégral d'une décision JudiLibre.

        Args:
            decision_id: Identifiant unique de la décision.
            resolve_references: Si True, ajoute les intitulés complets.
            query: Termes à surligner dans la réponse.
            operator: "or", "and" (défaut), ou "exact".

        Returns:
            La décision complète.

        Raises:
            ValueError: Si decision_id est vide ou si operator n'est pas valide.
            Exception: Si la requête HTTP échoue.
        """
        if not decision_id or not decision_id.strip():
            raise ValueError(
                "L'identifiant de la décision est obligatoire et ne peut pas être vide"
            )
        if operator not in self.VALID_OPERATORS:
            raise ValueError("operator doit être 'or', 'and' ou 'exact'")

        endpoint = f"{self.api_url}/decision"
        params: Dict[str, Any] = {
            "id": decision_id,
            "resolve_references": "true" if resolve_references else "false",
        }
        if query:
            params["query"] = query
            params["operator"] = operator

        try:
            response = self._request("GET", endpoint, params=params)
            return self.clean(response.json())
        except requests.exceptions.RequestException as e:
            raise Exception(f"Erreur lors de la récupération de la décision '{decision_id}': {e}")

    def taxonomy(
        self,
        taxonomy_id: str | None = None,
        key: str | None = None,
        value: str | None = None,
        context_value: str | None = None,
    ) -> Any:
        """
        Récupère les taxonomies (couples clé/valeur) employées par la recherche
        JudiLibre.

        Args:
            taxonomy_id: Identifiant de la taxonomie (type, jurisdiction, chamber, …).
            key: Clé du terme dont on veut l'intitulé.
            value: Intitulé dont on veut la clé.
            context_value: Contexte (pour chamber/location notamment).

        Returns:
            Données de taxonomie (dict ou list selon les paramètres).

        Raises:
            ValueError: Si les paramètres sont incompatibles.
            Exception: Erreurs de requête API.
        """
        endpoint = f"{self.api_url}/taxonomy"
        params: Dict[str, Any] = {}

        if key and value:
            raise ValueError("Les paramètres 'key' et 'value' sont mutuellement exclusifs")
        if (key or value) and not taxonomy_id:
            raise ValueError("Le paramètre 'taxonomy_id' est requis avec 'key' ou 'value'")

        if taxonomy_id:
            params["id"] = taxonomy_id
        if key:
            params["key"] = key
        if value:
            params["value"] = value
        if context_value:
            params["context_value"] = context_value

        if not params:
            return {
                "type": "Types de décision (arrêt, ordonnance, QPC, etc.)",
                "jurisdiction": "Juridictions (Cour de cassation, cours d'appel, tribunaux, etc.)",
                "chamber": "Chambres de la Cour de cassation (civile, sociale, criminelle, etc.)",
                "formation": "Formations des juridictions",
                "publication": "Niveaux de publication (bulletin, rapport, lettre, etc.)",
                "theme": "Matières juridiques (nomenclature Cour de cassation)",
                "solution": "Types de solution (cassation, rejet, annulation, etc.)",
                "field": "Champs et zones de contenu (exposé, moyens, motivations, dispositif, etc.)",
                "zones": "Zones de contenu des décisions",
                "location": "Codes des sièges de juridiction (cours d'appel, tribunaux)",
                "filetype": "Types de documents associés (rapports, avis, communiqués, etc.)",
            }

        try:
            response = self._request("GET", endpoint, params=params)
            data = response.json()
            return data.get("result", data)
        except requests.exceptions.RequestException as e:
            if taxonomy_id:
                raise Exception(
                    f"Erreur lors de la récupération de la taxonomie '{taxonomy_id}': {e}"
                )
            raise Exception(f"Erreur lors de la récupération des taxonomies: {e}")

    def clean(self, x: Any) -> Any | None:
        """
        Nettoie une réponse JudiLibre via le helper partagé `recursive_filter`.
        """
        return recursive_filter(x, self.ALLOWED_KEYS, max_depth=self.MAX_DEPTH)
