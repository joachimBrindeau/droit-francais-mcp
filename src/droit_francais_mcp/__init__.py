"""Serveur MCP pour interroger les API publiques du droit français (Légifrance + JudiLibre).

API publique du package : on ré-exporte les classes les plus susceptibles d'être
importées par des scripts externes ou des notebooks (`from droit_francais_mcp
import LegifranceAPI`). Les modules internes (`droit_francais_mcp.server`,
`droit_francais_mcp.tools`, `droit_francais_mcp.resources`) ne sont pas
considérés comme stables — ne pas y reposer depuis le code externe.
"""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

from droit_francais_mcp.judilibre.client import JudilibreAPI
from droit_francais_mcp.legifrance.client import LegifranceAPI
from droit_francais_mcp.legifrance.query_builder import LegifranceQueryBuilder
from droit_francais_mcp.piste.auth import PisteOAuthClient
from droit_francais_mcp.piste.filters import recursive_filter

try:
    __version__ = version("droit-francais-mcp")
except PackageNotFoundError:
    __version__ = "0.0.0+local"

__all__ = [
    "__version__",
    "JudilibreAPI",
    "LegifranceAPI",
    "LegifranceQueryBuilder",
    "PisteOAuthClient",
    "recursive_filter",
]
