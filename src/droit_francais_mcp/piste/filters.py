#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utilitaires partagés entre les clients PISTE (Légifrance + JudiLibre).

Copyright (c) 2025 Jean-Michel Tanguy
Licensed under the MIT License (see LICENSE file)
"""

from typing import Any, FrozenSet, Optional


def recursive_filter(
    x: Any,
    allowed_keys: FrozenSet[str],
    depth: int = 0,
    max_depth: int = 8,
) -> Optional[Any]:
    """
    Nettoie récursivement un dict/list en ne conservant que les clés `allowed_keys`
    et en supprimant les valeurs None/vides. La descente s'arrête à `max_depth`.

    Args:
        x: Donnée à filtrer (dict, list, ou scalaire).
        allowed_keys: Ensemble des clés à conserver à tous les niveaux.
        depth: Profondeur courante (usage interne récursif).
        max_depth: Profondeur maximale (au-delà, retourne None).

    Returns:
        La structure filtrée — ou `None` si elle est vide ou si la profondeur
        max est atteinte.
    """
    if depth >= max_depth:
        return None

    if isinstance(x, dict):
        cleaned: dict = {}
        for k, v in x.items():
            if not v:
                continue
            if k in allowed_keys and not isinstance(v, (dict, list)):
                cleaned[k] = v
            elif isinstance(v, (dict, list)):
                cleaned_value = recursive_filter(v, allowed_keys, depth + 1, max_depth)
                if cleaned_value:
                    cleaned[k] = cleaned_value
        return cleaned if cleaned else None

    if isinstance(x, list):
        if x and all(isinstance(item, str) for item in x):
            return x
        filtered = [
            cleaned_v
            for v in x
            if v and (cleaned_v := recursive_filter(v, allowed_keys, depth + 1, max_depth)) is not None
        ]
        return filtered if filtered else None

    return x
