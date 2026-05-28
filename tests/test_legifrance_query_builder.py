"""Tests unitaires (offline) pour `LegifranceQueryBuilder`."""

from __future__ import annotations

import pytest

from droit_francais_mcp.legifrance.query_builder import LegifranceQueryBuilder

pytestmark = pytest.mark.unit


def test_supports_date_filter_for_known_fonds() -> None:
    assert LegifranceQueryBuilder.supports_date_filter("JORF") is True
    assert LegifranceQueryBuilder.supports_date_filter("KALI") is True


def test_supports_date_filter_rejects_unknown_or_unsupported() -> None:
    assert LegifranceQueryBuilder.supports_date_filter("ALL") is False
    assert LegifranceQueryBuilder.supports_date_filter("CNIL") is False
    assert LegifranceQueryBuilder.supports_date_filter("UNKNOWN_FOND") is False


def test_date_filter_facette_returns_correct_facette() -> None:
    assert LegifranceQueryBuilder.date_filter_facette("JORF") == "DATE_PUBLICATION"
    assert LegifranceQueryBuilder.date_filter_facette("JURI") == "DATE_DECISION"
    assert LegifranceQueryBuilder.date_filter_facette("KALI") == "DATE_SIGNATURE"
    assert LegifranceQueryBuilder.date_filter_facette("CNIL") is None


def test_set_fond_accepts_known() -> None:
    q = LegifranceQueryBuilder()
    q.set_fond("JORF")
    assert q.query["fond"] == "JORF"


def test_set_fond_rejects_unknown() -> None:
    q = LegifranceQueryBuilder()
    with pytest.raises(ValueError, match="Fonds invalide"):
        q.set_fond("INVALID_FOND")


def test_build_returns_dict() -> None:
    q = LegifranceQueryBuilder()
    q.set_fond("JORF")
    payload = q.build()
    assert isinstance(payload, dict)
    assert payload["fond"] == "JORF"
    assert "recherche" in payload


def test_set_operator_accepts_et_ou() -> None:
    q = LegifranceQueryBuilder()
    q.set_operator("ET")
    assert q.query["recherche"]["operateur"] == "ET"
    q.set_operator("OU")
    assert q.query["recherche"]["operateur"] == "OU"


def test_set_pagination_caps_page_size_at_50() -> None:
    q = LegifranceQueryBuilder()
    q.set_pagination(page_number=2, page_size=999)
    assert q.query["recherche"]["pageSize"] == 50
    assert q.query["recherche"]["pageNumber"] == 2


def test_code_fonds_classvar_contents() -> None:
    assert LegifranceQueryBuilder.CODE_FONDS == frozenset({"CODE_ETAT", "CODE_DATE"})


def test_vigueur_default_fonds_classvar_contents() -> None:
    assert LegifranceQueryBuilder.VIGUEUR_DEFAULT_FONDS == frozenset(
        {"JORF", "CODE_ETAT", "CODE_DATE", "LODA_DATE", "LODA_ETAT"}
    )
