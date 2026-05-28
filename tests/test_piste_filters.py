"""Tests unitaires pour `piste.filters.recursive_filter`."""

from __future__ import annotations

import pytest

from droit_francais_mcp.piste.filters import recursive_filter

pytestmark = pytest.mark.unit

ALLOWED = frozenset({"id", "title", "text", "values"})


def test_filters_dict_keeps_only_allowed_keys() -> None:
    """Les clés hors `allowed_keys` (non récursives) sont droppées."""
    result = recursive_filter(
        {"id": "X", "title": "T", "ignored": "should_drop"},
        ALLOWED,
    )
    assert result == {"id": "X", "title": "T"}


def test_filters_drops_none_and_empty() -> None:
    """Les valeurs falsy sont droppées même si la clé est `allowed`."""
    result = recursive_filter(
        {"id": "X", "title": "", "text": None, "values": []},
        ALLOWED,
    )
    assert result == {"id": "X"}


def test_filters_recurses_into_nested_dict() -> None:
    """La descente est récursive ; les sous-dicts sont filtrés indépendamment."""
    result = recursive_filter(
        {
            "id": "X",
            "junk": "drop",
            "nested": {"title": "T", "junk": "drop"},
        },
        ALLOWED,
    )
    assert result == {"id": "X", "nested": {"title": "T"}}


def test_filters_collapses_empty_nested_dict() -> None:
    """Un sous-dict qui devient vide après filtrage est dropped (pas `{}`)."""
    result = recursive_filter(
        {"id": "X", "nested": {"junk": "drop"}},
        ALLOWED,
    )
    assert result == {"id": "X"}


def test_filters_preserves_list_of_strings() -> None:
    """Une liste 100 % string passe telle quelle (pas de filtrage par clé)."""
    result = recursive_filter(["a", "b", "c"], ALLOWED)
    assert result == ["a", "b", "c"]


def test_filters_recurses_into_list_of_dicts() -> None:
    """Les dicts dans une liste sont filtrés ; les éléments vides sont retirés."""
    result = recursive_filter(
        [
            {"id": "A", "junk": "drop"},
            {"junk": "only"},  # devient vide
            {"id": "B", "title": "T"},
        ],
        ALLOWED,
    )
    assert result == [{"id": "A"}, {"id": "B", "title": "T"}]


def test_filters_respects_max_depth() -> None:
    """Au-delà de `max_depth`, la descente renvoie None et le parent disparaît."""
    deep = {"id": "X", "level1": {"level2": {"level3": {"id": "Y"}}}}
    # max_depth=2 : la descente s'arrête à level2 (depth=2), level3 devient None.
    result = recursive_filter(deep, ALLOWED, max_depth=2)
    assert result == {"id": "X"}


def test_filters_returns_scalar_unchanged() -> None:
    """Un scalaire (str, int, bool) renvoyé tel quel à la profondeur 0."""
    assert recursive_filter("hello", ALLOWED) == "hello"
    assert recursive_filter(42, ALLOWED) == 42


def test_filters_empty_dict_returns_none() -> None:
    """Un dict vide ou entièrement filtré est représenté par None."""
    assert recursive_filter({}, ALLOWED) is None
    assert recursive_filter({"junk": "drop"}, ALLOWED) is None
