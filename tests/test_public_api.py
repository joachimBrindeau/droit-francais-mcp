"""Pin de l'API publique exposée par `droit_francais_mcp.__init__`."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


EXPECTED_PUBLIC_SYMBOLS = frozenset(
    {
        "__version__",
        "JudilibreAPI",
        "LegifranceAPI",
        "LegifranceQueryBuilder",
        "PisteOAuthClient",
        "recursive_filter",
    }
)


def test_public_api_surface_matches_expected() -> None:
    """`from droit_francais_mcp import *` doit exposer exactement le set attendu."""
    import droit_francais_mcp as pkg

    assert hasattr(pkg, "__all__")
    assert frozenset(pkg.__all__) == EXPECTED_PUBLIC_SYMBOLS, (
        f"L'API publique a dérivé. Attendu={sorted(EXPECTED_PUBLIC_SYMBOLS)} "
        f"obtenu={sorted(pkg.__all__)}"
    )
    for symbol in EXPECTED_PUBLIC_SYMBOLS:
        assert hasattr(pkg, symbol), f"Symbole annoncé mais absent: {symbol}"


def test_version_is_string_version() -> None:
    """`__version__` doit être une string respectant `X.Y.Z`-ish."""
    import re

    from droit_francais_mcp import __version__

    assert isinstance(__version__, str)
    assert re.match(r"^\d+\.\d+\.\d+", __version__) or __version__ == "0.0.0+local"


def test_reexported_classes_are_the_real_classes() -> None:
    """Les ré-exports pointent bien vers les classes dans leur module d'origine."""
    from droit_francais_mcp import (
        JudilibreAPI,
        LegifranceAPI,
        LegifranceQueryBuilder,
        PisteOAuthClient,
        recursive_filter,
    )
    from droit_francais_mcp.judilibre.client import JudilibreAPI as JudilibreAPI_real
    from droit_francais_mcp.legifrance.client import LegifranceAPI as LegifranceAPI_real
    from droit_francais_mcp.legifrance.query_builder import (
        LegifranceQueryBuilder as LegifranceQueryBuilder_real,
    )
    from droit_francais_mcp.piste.auth import PisteOAuthClient as PisteOAuthClient_real
    from droit_francais_mcp.piste.filters import recursive_filter as recursive_filter_real

    assert LegifranceAPI is LegifranceAPI_real
    assert JudilibreAPI is JudilibreAPI_real
    assert LegifranceQueryBuilder is LegifranceQueryBuilder_real
    assert PisteOAuthClient is PisteOAuthClient_real
    assert recursive_filter is recursive_filter_real
