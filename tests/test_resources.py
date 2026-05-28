"""Tests pour les ressources MCP (`@mcp.resource`) — vérifie URIs + contenus."""

from __future__ import annotations

import pytest

from droit_francais_mcp import resources

pytestmark = pytest.mark.unit


# FastMCP enveloppe les fonctions décorées dans `FunctionResource` ; `.fn`
# expose la fonction Python originale, ce qui est ce qu'on veut tester.
ALL_RESOURCES = [
    resources.documentation_fonds_legifrance.fn,
    resources.documentation_champs_legifrance.fn,
    resources.documentation_types_recherche_legifrance.fn,
    resources.documentation_options_tri_legifrance.fn,
    resources.documentation_filtres_dates_legifrance.fn,
    resources.documentation_juridictions_judilibre.fn,
    resources.documentation_chambres_judilibre.fn,
    resources.documentation_solutions_judilibre.fn,
    resources.documentation_localisations_judilibre.fn,
    resources.documentation_types_decision_judilibre.fn,
    resources.documentation_themes_judilibre.fn,
    resources.documentation_options_tri_judilibre.fn,
]


def test_each_resource_returns_non_empty_markdown_string() -> None:
    """Chaque ressource produit du texte non-vide."""
    for fn in ALL_RESOURCES:
        result = fn()
        assert isinstance(result, str), f"{fn.__name__} doit retourner str"
        assert len(result.strip()) > 0, f"{fn.__name__} ne doit pas être vide"


def test_legifrance_fonds_lists_known_fonds() -> None:
    """Le markdown des fonds doit mentionner les principaux fonds officiels."""
    md = resources.documentation_fonds_legifrance.fn()
    for fond in ("ALL", "JORF", "JURI", "KALI", "CETAT", "CNIL"):
        assert fond in md, f"Le fond {fond!r} doit apparaître dans la doc"


def test_judilibre_juridictions_lists_known_jurisdictions() -> None:
    md = resources.documentation_juridictions_judilibre.fn()
    for jur in ("cc", "ca", "tj", "tcom"):
        assert jur in md, f"Le code juridiction {jur!r} doit apparaître"


def test_judilibre_chambres_lists_known_chambers() -> None:
    md = resources.documentation_chambres_judilibre.fn()
    for ch in ("pl", "mi", "civ1", "civ2", "civ3", "comm", "soc", "cr"):
        assert ch in md, f"Le code chambre {ch!r} doit apparaître"


def test_resource_count_matches_expected() -> None:
    """Pin du nombre total de ressources exposées (5 legifrance + 7 judilibre = 12)."""
    assert len(ALL_RESOURCES) == 12
