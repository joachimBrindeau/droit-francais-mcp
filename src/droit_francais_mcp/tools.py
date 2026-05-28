"""Outils MCP exposés aux clients (Légifrance + JudiLibre).

Chaque fonction `@mcp.tool` est protégée par `@safe_mcp_tool` (ordre :
`@mcp.tool` au-dessus). Les clients sont obtenus via les accesseurs paresseux
`get_legifrance_api()` / `get_judilibre_api()` afin que ce module soit
importable même sans variables d'environnement PISTE.
"""

from __future__ import annotations

import logging
from typing import Any

from droit_francais_mcp.legifrance.query_builder import LegifranceQueryBuilder
from droit_francais_mcp.server import (
    _init_errors,
    get_judilibre_api,
    get_legifrance_api,
    mcp,
    safe_mcp_tool,
)

logger = logging.getLogger(__name__)


# ============================================================================
# OUTILS LEGIFRANCE
# ============================================================================


@mcp.tool
@safe_mcp_tool("Erreur lors de la recherche Légifrance", on_error_return="Erreur lors de la recherche")
def rechercher_legifrance(
    recherche: str,
    fond: str = "ALL",
    type_champ: str = "ALL",
    type_recherche: str = "TOUS_LES_MOTS_DANS_UN_CHAMP",
    code: str | None = None,
    date_debut: str | None = None,
    date_fin: str | None = None,
    page: int = 0,
    page_taille: int = 20,
    tri: str | None = "PERTINENCE",
    operateur: str = "ET",
) -> Any:
    """
    Recherche avancée dans la base juridique Légifrance (codes, lois, jurisprudence, conventions).

    Args:
        recherche: Terme(s) de recherche. Ex: "mariage", "responsabilité civile"
        fond: Fonds (ALL, CODE_ETAT, LODA_ETAT, JORF, JURI, KALI, etc.). Défaut: "ALL"
        type_champ: Champ de recherche (ALL, TITLE, ARTICLE, etc.). Défaut: "ALL"
        type_recherche: Type de recherche : EXACTE, TOUS_LES_MOTS_DANS_UN_CHAMP, UN_DES_MOTS, AUCUN_DES_MOTS. Défaut: "TOUS_LES_MOTS_DANS_UN_CHAMP"
        code: Nom du code (ex: "Code civil") pour fonds CODE_ETAT/CODE_DATE. Défaut : None
        date_debut: Date de début pour filtres dates (YYYY-MM-DD) avec les fonds: JORF, LODA_DATE, LODA_ETAT, JURI, CETAT, JUFI, CONSTIT, KALI, CIRC, ACCO. Défaut : None
        date_fin: Date de fin pour filtres dates (YYYY-MM-DD) avec les fonds: JORF, LODA_DATE, LODA_ETAT, JURI, CETAT, JUFI, CONSTIT, KALI, CIRC, ACCO : Défaut : None
        page: Numéro de page. Défaut: 0
        page_taille: Résultats par page (max 50). Défaut: 20
        tri: Ordre de tri avec PERTINENCE, SIGNATURE_DATE_DESC, SIGNATURE_DATE_ASC, DATE_PUBLI_DESC, DATE_PUBLI_ASC Défaut: PERTINENCE
        operateur: Opérateur entre champs (ET, OU). Défaut: "ET"

    Returns:
        Liste de résultats avec métadonnées. Utiliser l'outil consult_legifrance(id) pour le contenu complet.

    Ressources utiles:
        - legifrance://documentation/fonds
        - legifrance://documentation/champs
        - legifrance://documentation/types-recherche
        - legifrance://documentation/filtres-dates
        - legifrance://documentation/options-tri
    """
    if not recherche or not recherche.strip():
        logger.error("Requête de recherche vide")
        return []

    api = get_legifrance_api()
    if api is None:
        err = _init_errors.get("legifrance", "raison inconnue")
        logger.error(f"API Légifrance non initialisée: {err}")
        return []

    # Source unique de vérité: LegifranceQueryBuilder.supports_date_filter().
    warning = None
    if (date_debut or date_fin) and not LegifranceQueryBuilder.supports_date_filter(fond):
        warning = [
            f"⚠️ ATTENTION: Les filtres de dates (date_debut/date_fin) sont ignorés pour le fond '{fond}'. "
            f"Les filtres de dates ne fonctionnent que pour les fonds: "
            f"{', '.join(sorted(LegifranceQueryBuilder.DATE_FILTER_FACETTES))}"
        ]
        date_debut = None
        date_fin = None

    search_results = api.search(
        query=recherche,
        fond=fond,
        field_type=type_champ,
        search_type=type_recherche,
        code=code,
        date_start=date_debut,
        date_end=date_fin,
        page_number=page,
        page_size=page_taille,
        sort=tri,
        operator=operateur,
    )

    search_results = search_results or []
    if warning:
        search_results = {"warning": warning, "results": search_results}

    return search_results


@mcp.tool
@safe_mcp_tool(
    "Erreur lors de la récupération de l'article",
    on_error_return={"erreur": "Erreur de récupération d'article"},
)
def consulter_legifrance(id: str) -> Any:
    """
    Récupère le texte intégral d'un article juridique depuis Légifrance.

    Cette fonction est la DEUXIÈME ÉTAPE après toute recherche pour obtenir le contenu complet.

    Args:
        id: ID de l'article (LEGIARTI..., LEGITEXT..., JURITEXT..., etc.)
                   Obtenu depuis les résultats de recherche (metadata 'id')

    Returns:
        Le contenu juridique
    """
    if not id or not id.strip():
        logger.error("ID article vide")
        return {"erreur": "L'ID de l'article ne peut pas être vide"}

    api = get_legifrance_api()
    if api is None:
        err = _init_errors.get("legifrance", "raison inconnue")
        logger.error(f"API Légifrance non initialisée: {err}")
        return {"erreur": f"L'API Légifrance n'est pas initialisée ({err})"}

    return api.consult(id)


# ============================================================================
# OUTILS JUDILIBRE
# ============================================================================


@mcp.tool
@safe_mcp_tool(
    "Erreur lors de la récupération de la taxonomie",
    on_error_return={"erreur": "Erreur taxonomie"},
)
def obtenir_taxonomie_judilibre(
    taxonomy_id: str | None = None,
    key: str | None = None,
    value: str | None = None,
    context_value: str | None = None,
) -> Any:
    """
    Récupère les valeurs valides pour les filtres de recherche Judilibre (juridictions, chambres, solutions, etc.).
    Utiliser les ressources en priorité pour connaître les valeurs possibles avant d'utiliser cette fonction.

    Args:
        taxonomy_id: Type de taxonomie (jurisdiction, chamber, solution, theme, location, etc.)
        key: Clé pour obtenir l'intitulé complet
        value: Intitulé pour obtenir la clé
        context_value: Contexte pour certaines taxonomies (cc, ca, tj)

    Returns:
        Données de taxonomie (liste ou dict selon les paramètres)

    Exemples d'usage:
        - obtenir_taxonomie_judilibre() → toutes les taxonomies
        - obtenir_taxonomie_judilibre(taxonomy_id="chamber", context_value="cc") → chambres Cour de cassation
        - obtenir_taxonomie_judilibre(taxonomy_id="location", context_value="ca") → cours d'appel

    Ressources utiles:
        - judilibre://documentation/juridictions
        - judilibre://documentation/chambres
        - judilibre://documentation/solutions
    """
    logger.debug(
        f"APPEL: obtenir_taxonomie_judilibre(taxonomy_id='{taxonomy_id}', key='{key}', value='{value}', context_value='{context_value}')"
    )

    api = get_judilibre_api()
    if api is None:
        err = _init_errors.get("judilibre", "raison inconnue")
        logger.error(f"API Judilibre non initialisée: {err}")
        return {"erreur": f"L'API Judilibre n'est pas initialisée ({err})"}

    return api.taxonomy(taxonomy_id=taxonomy_id, key=key, value=value, context_value=context_value)


@mcp.tool
@safe_mcp_tool(
    "Erreur lors de la recherche Judilibre",
    on_error_return="Erreur lors de la recherche Judilibre",
)
def rechercher_jurisprudence_judilibre(
    recherche: str | None = None,
    juridiction: str | None = None,
    localisation: str | None = None,
    chambre: str | None = None,
    type_decision: str | None = None,
    theme: str | None = None,
    solution: str | None = None,
    date_debut: str | None = None,
    date_fin: str | None = None,
    tri: str = "scorepub",
    ordre: str = "desc",
    nombre_resultats: int = 20,
    page: int = 0,
) -> Any:
    """
    Recherche de jurisprudence dans la base Judilibre (décisions de toutes les juridictions françaises).
    À utiliser en priorité pour la recherche jurisprudentielle.

    Args:
        recherche: Texte de recherche
        juridiction: Code juridiction (cc, ca, tj, tcom). Défaut : None (toutes)
        localisation: Code siège (ca_paris, tj06088, etc.). Défaut : None
        chambre: Code chambre - CLÉS: "pl", "mi", "civ1", "civ2", "civ3", "comm", "soc", "cr". Défaut : None
        type_decision: Type de décision (arret, ordonnance, qpc, saisie). Défaut : None
        theme: Code matière juridique. Défaut : None
        solution: Solution (cassation, rejet, annulation, etc.). Défaut : None
        date_debut: Date début ISO (ex: 2023-01-15). Défaut : None
        date_fin: Date fin ISO (ex: 2023-12-15). Défaut : None
        tri: Ordre de tri (scorepub, score, date). Défaut: "scorepub"
        ordre: Sens du tri (desc, asc). Défaut: "desc"
        nombre_resultats: Résultats par page (max 50). Défaut: 20
        page: Numéro de page (0-indexé). Défaut : 0

    Returns:
        Liste de décisions. Utiliser obtenir_decision_judilibre(id) pour le texte complet.

    Ressources utiles:
        - judilibre://documentation/juridictions
        - judilibre://documentation/chambres
        - judilibre://documentation/localisations
        - judilibre://documentation/types-decision
        - judilibre://documentation/themes
        - judilibre://documentation/solutions
        - judilibre://documentation/options-tri
    """
    api = get_judilibre_api()
    if api is None:
        err = _init_errors.get("judilibre", "raison inconnue")
        logger.error(f"API Judilibre non initialisée: {err}")
        return [{"erreur": f"L'API Judilibre n'est pas initialisée ({err})"}]

    # Conversion des paramètres scalaires en listes pour l'API JudiLibre.
    jurisdiction_list = [juridiction] if juridiction else None
    location_list = [localisation] if localisation else None
    chamber_list = [chambre] if chambre else None
    type_list = [type_decision] if type_decision else None
    theme_list = [theme] if theme else None
    solution_list = [solution] if solution else None

    return api.search(
        query=recherche,
        jurisdiction=jurisdiction_list,
        location=location_list,
        chamber=chamber_list,
        type=type_list,
        theme=theme_list,
        solution=solution_list,
        date_start=date_debut,
        date_end=date_fin,
        sort=tri,
        order=ordre,
        page_size=nombre_resultats,
        page=page,
        resolve_references=True,
    )


@mcp.tool
@safe_mcp_tool(
    "Erreur lors de la récupération de la décision",
    on_error_return={"erreur": "Erreur récupération décision"},
)
def consulter_decision_judilibre(decision_id: str) -> Any:
    """
    Récupère le contenu d'une décision de justice depuis Judilibre.

    Cette fonction est la DEUXIÈME ÉTAPE après rechercher_jurisprudence_judilibre() pour obtenir le texte complet.

    Args:
        decision_id: ID unique de la décision (champ 'id' des résultats de recherche)

    Returns:
        La décision complète.
    """
    logger.debug(f"APPEL: obtenir_decision_judilibre(decision_id='{decision_id}')")

    if not decision_id or not decision_id.strip():
        logger.error("ID décision vide")
        return {"erreur": "L'ID de la décision ne peut pas être vide"}

    api = get_judilibre_api()
    if api is None:
        err = _init_errors.get("judilibre", "raison inconnue")
        logger.error(f"API Judilibre non initialisée: {err}")
        return {"erreur": f"L'API Judilibre n'est pas initialisée ({err})"}

    return api.consult(decision_id=decision_id)
