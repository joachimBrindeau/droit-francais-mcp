"""Serveur MCP — instance `FastMCP`, init paresseuse des clients PISTE,
décorateur défensif `safe_mcp_tool` et point d'entrée `main()`.

Les outils (`@mcp.tool`) vivent dans `droit_francais_mcp.tools` et les
ressources (`@mcp.resource`) dans `droit_francais_mcp.resources`. Ces deux
modules sont importés en fin de fichier pour déclencher l'enregistrement
auto via FastMCP.
"""

from __future__ import annotations

import copy
import logging
import sys
from functools import wraps
from typing import Any, Callable, TypeVar

from fastmcp import FastMCP

from droit_francais_mcp.judilibre.client import JudilibreAPI
from droit_francais_mcp.legifrance.client import LegifranceAPI

# ============================================================================
# CONFIGURATION ET INITIALISATION
# ============================================================================

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)],  # MCP exige stderr pour les logs
)
logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------------
# Init paresseuse des clients PISTE.
# ----------------------------------------------------------------------------
# Les clients ne sont plus construits au moment de l'import du module : ça
# rendait le module non-importable sans variables d'environnement valides
# (impactant les tests unitaires). On expose des accesseurs qui mémoïsent
# le résultat et stockent l'éventuelle erreur d'init dans `_init_errors`.

_init_errors: dict[str, str] = {}
_clients: dict[str, Any] = {}
_SENTINEL = object()


def _safe_init(cls: type[Any], label: str, key: str) -> Any | None:
    """Construit `cls(sandbox=False)` en capturant les erreurs d'init.

    L'exception capturée est stockée dans `_init_errors[key]` afin que les
    outils MCP puissent la rapporter à l'opérateur — plutôt qu'un générique
    « API non initialisée ».
    """
    try:
        return cls(sandbox=False)
    except Exception as e:
        msg = f"{type(e).__name__}: {e}"
        logger.exception(f"Erreur lors de l'initialisation de l'API {label}")
        _init_errors[key] = msg
        return None


def get_legifrance_api() -> LegifranceAPI | None:
    """Renvoie l'instance `LegifranceAPI` (construite à la première demande)."""
    if _clients.get("legifrance", _SENTINEL) is _SENTINEL:
        _clients["legifrance"] = _safe_init(LegifranceAPI, "LegiFrance", "legifrance")
    result: LegifranceAPI | None = _clients["legifrance"]
    return result


def get_judilibre_api() -> JudilibreAPI | None:
    """Renvoie l'instance `JudilibreAPI` (construite à la première demande)."""
    if _clients.get("judilibre", _SENTINEL) is _SENTINEL:
        _clients["judilibre"] = _safe_init(JudilibreAPI, "Judilibre", "judilibre")
    result: JudilibreAPI | None = _clients["judilibre"]
    return result


def reset_clients() -> None:
    """Réinitialise le cache d'instances et d'erreurs (utilisé par les tests)."""
    _clients.clear()
    _init_errors.clear()


# ----------------------------------------------------------------------------
# Initialisation de FastMCP
# ----------------------------------------------------------------------------

try:
    mcp = FastMCP("FR Légifrance et Judilibre MCP Server - Droit Français Officiel")
except Exception as e:
    logger.error(f"Échec de l'initialisation du serveur MCP: {e}")
    raise


# ----------------------------------------------------------------------------
# Décorateur défensif pour les outils MCP
# ----------------------------------------------------------------------------

F = TypeVar("F", bound=Callable[..., Any])


def safe_mcp_tool(error_label: str, on_error_return: Any) -> Callable[[F], F]:
    """Décorateur qui ajoute un `try/except` + `logger.exception` standardisé.

    Args:
        error_label: étiquette utilisée dans le message de log.
        on_error_return: valeur retournée si l'outil lève une exception
            (préserve le contrat de retour observé par les tests). Une copie
            profonde est renvoyée à chaque appel afin qu'une éventuelle mutation
            par l'appelant ne fuie pas vers les invocations suivantes.

    Ordre des décorateurs : `@mcp.tool` DOIT être appliqué AU-DESSUS de
    `@safe_mcp_tool`. Inverser l'ordre fait que FastMCP enregistre la fonction
    brute (non protégée), et `safe_mcp_tool` reçoit l'objet d'enregistrement
    FastMCP au lieu d'un callable.
    """

    def decorator(fn: F) -> F:
        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return fn(*args, **kwargs)
            except Exception:
                logger.exception(error_label)
                return copy.deepcopy(on_error_return)

        return wrapper  # type: ignore[return-value]

    return decorator


# ----------------------------------------------------------------------------
# Point d'entrée
# ----------------------------------------------------------------------------


def main() -> None:
    """Point d'entrée pour `python -m droit_francais_mcp` et la console-script."""
    mcp.run()


# ----------------------------------------------------------------------------
# Enregistrement des outils et ressources.
# ----------------------------------------------------------------------------
# Les imports en bas du fichier déclenchent l'évaluation des décorateurs
# `@mcp.tool` / `@mcp.resource` dans ces modules et leur enregistrement
# automatique sur l'instance `mcp` ci-dessus.

from droit_francais_mcp import resources as _resources  # noqa: E402, F401  (effets de bord)
from droit_francais_mcp import tools as _tools  # noqa: E402, F401  (effets de bord)

if __name__ == "__main__":
    main()
