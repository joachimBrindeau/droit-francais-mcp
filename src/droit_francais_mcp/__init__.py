"""Serveur MCP pour interroger les API publiques du droit français (Légifrance + JudiLibre)."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("droit-francais-mcp")
except PackageNotFoundError:
    __version__ = "0.0.0+local"

__all__ = ["__version__"]
