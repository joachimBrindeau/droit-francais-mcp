"""Tests pour le module `droit_francais_mcp.__main__` (entry-point `python -m`)."""

from __future__ import annotations

from unittest.mock import patch

import pytest

pytestmark = pytest.mark.unit


def test_main_module_imports_without_side_effects() -> None:
    """`import droit_francais_mcp.__main__` ne déclenche pas `mcp.run()`."""
    with patch("droit_francais_mcp.server.mcp.run") as run:
        import droit_francais_mcp.__main__  # noqa: F401

    run.assert_not_called()


def test_main_module_exposes_main_callable() -> None:
    """Le module `__main__` ré-exporte la fonction `main`."""
    from droit_francais_mcp.__main__ import main

    assert callable(main)


def test_main_module_main_delegates_to_mcp_run() -> None:
    """L'appel à `main()` délègue à `mcp.run()`."""
    from droit_francais_mcp.__main__ import main

    with patch("droit_francais_mcp.server.mcp.run") as run:
        main()

    run.assert_called_once_with()
