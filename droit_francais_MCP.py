#!/usr/bin/env python3
"""DEPRECATED — shim de rétro-compatibilité.

Ce fichier était le point d'entrée historique du serveur MCP. Il a été migré
vers le package `droit_francais_mcp` (voir `src/droit_francais_mcp/server.py`).

Ce shim est conservé pour les utilisateurs dont la configuration MCP (par
exemple `claude_desktop_config.json`) référence un chemin absolu vers ce
fichier. Il sera retiré dans la v2.0.

Migration recommandée :

    {
      "mcpServers": {
        "droit-francais": {
          "command": "droit-francais-mcp",
          "env": {"PISTE_CLIENT_ID": "...", "PISTE_CLIENT_SECRET": "..."}
        }
      }
    }

ou via `uvx` (sans installation préalable) :

    {"command": "uvx", "args": ["droit-francais-mcp"]}
"""

from __future__ import annotations

import sys
import warnings

# DeprecationWarning + message stderr (stderr est le seul canal sûr en MCP
# stdio — stdout est réservé au framing JSON-RPC).
_DEPRECATION_MESSAGE = (
    "droit_francais_MCP.py est déprécié et sera retiré dans la v2.0. "
    "Utilisez la console-script `droit-francais-mcp` ou "
    "`python -m droit_francais_mcp`."
)
warnings.warn(_DEPRECATION_MESSAGE, DeprecationWarning, stacklevel=2)
print(f"DEPRECATION: {_DEPRECATION_MESSAGE}", file=sys.stderr)

from droit_francais_mcp.server import main  # noqa: E402  (after stderr message)

if __name__ == "__main__":
    main()
