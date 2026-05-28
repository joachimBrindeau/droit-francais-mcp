"""Ressources MCP — documentation détaillée exposée aux clients (Légifrance + JudiLibre).

Chaque fonction `@mcp.resource` retourne un court markdown listant les codes
ou catégories acceptés par les outils. Le contenu est statique : c'est de la
documentation utilisateur, pas un appel API.
"""

from __future__ import annotations

from droit_francais_mcp.server import mcp


@mcp.resource("legifrance://context")
def context_recherche_juridique() -> str:
    """Workflow recommandé pour la recherche juridique avec ce serveur MCP.

    À lire en début de session : l'agent y trouve le pattern type
    "taxonomy → search → consult" et la façon de composer les outils.
    """
    return """
# Workflow de recherche juridique — droit-francais-mcp

Ce serveur MCP donne accès à deux familles d'API publiques de l'État français :

- **Légifrance** : législation (codes, lois, décrets, JORF, jurisprudence administrative)
- **JudiLibre** : jurisprudence judiciaire (Cour de cassation, cours d'appel, tribunaux)

## Pattern recommandé

1. **Découverte des valeurs valides** — si l'utilisateur emploie un nom métier
   (« 1ère chambre civile », « Cour d'appel de Paris ») plutôt qu'un code
   technique (`civ1`, `ca_paris`), commencer par interroger les ressources
   `legifrance://documentation/*` ou `judilibre://documentation/*` ou utiliser
   `obtenir_taxonomie_judilibre`.
2. **Recherche large** — utiliser `rechercher_legifrance` (textes) ou
   `rechercher_jurisprudence_judilibre` (décisions) avec les filtres pertinents.
   Les résultats contiennent des `id` mais pas le texte intégral.
3. **Consultation ciblée** — pour chaque résultat pertinent, appeler
   `consulter_legifrance(id=…)` ou `consulter_decision_judilibre(decision_id=…)`
   pour obtenir le texte complet.
4. **Diagnostic en cas de problème** — `ping_legifrance` confirme la connectivité
   et la validité du token OAuth.

## Choix du fond Légifrance

| Question utilisateur | Fond approprié |
|----------------------|----------------|
| Article d'un code (Code civil, Code pénal…) | `CODE_ETAT` + `code="…"` |
| Loi / décret / arrêté | `LODA_ETAT` ou `LODA_DATE` |
| Journal Officiel | `JORF` |
| Jurisprudence Cour de cassation (avant 2023) | `JURI` |
| Décision Conseil d'État | `CETAT` |
| Décision Conseil Constitutionnel | `CONSTIT` |
| Convention collective | `KALI` |
| CNIL | `CNIL` |
| Aucune préférence / recherche transversale | `ALL` |

## Filtres de date — fonds compatibles

`JORF`, `LODA_DATE`, `LODA_ETAT`, `JURI`, `CETAT`, `JUFI`, `CONSTIT`, `KALI`,
`CIRC`, `ACCO` acceptent `date_debut`/`date_fin`. Les autres fonds (`ALL`,
`CODE_*`, `CNIL`) ignorent ces filtres avec un warning.

## Idiomes JudiLibre

- Pour la Cour de cassation, **utiliser les CODES** de chambre (`pl`, `civ1`,
  `civ2`, `civ3`, `comm`, `soc`, `cr`, …), pas les noms complets.
- `juridiction` par défaut = toutes (`cc`, `ca`, `tj`, `tcom`).
- `tri="scorepub"` (défaut) combine pertinence et niveau de publication —
  préférable à `score` pour la jurisprudence cassationnelle.

## Erreurs fréquentes

- **403 Forbidden** — votre compte PISTE n'est probablement pas abonné à
  l'API concernée. Vérifier sur https://piste.gouv.fr/.
- **400 Bad Request sur OAuth** — credentials expirés ou révoqués.
  Régénérer sur https://piste.gouv.fr/.
- **« API non initialisée »** — variables d'environnement `PISTE_CLIENT_ID`
  / `PISTE_CLIENT_SECRET` manquantes. Le message d'erreur inclut le détail
  capturé à l'init.
"""


@mcp.resource("legifrance://documentation/fonds")
def documentation_fonds_legifrance() -> str:
    """Fonds de recherche Légifrance disponibles."""
    return """
# FONDS LÉGIFRANCE

**ALL** (défaut): Tous les fonds | **CODE_ETAT/CODE_DATE**: Codes consolidés | **LODA_ETAT/LODA_DATE**: Lois, Ordonnances, Décrets, Arrêtés | **JORF**: Journal Officiel | **JURI**: Jurisprudence judiciaire | **CETAT**: Conseil d'État | **JUFI**: Cour des comptes | **CONSTIT**: Conseil Constitutionnel | **KALI**: Conventions collectives | **ACCO**: Accords d'entreprise | **CIRC**: Circulaires | **CNIL**: CNIL
"""


@mcp.resource("legifrance://documentation/champs")
def documentation_champs_legifrance() -> str:
    """Types de champs de recherche Légifrance."""
    return """
# CHAMPS DE RECHERCHE

**ALL** (défaut): Tous les champs | **TITLE**: Titre | **ARTICLE**: Contenu articles | **TEXTE**: Texte complet | **NUM_ARTICLE**: N° article | **NOR**: N° ordre réglementaire | **NUM**: N° texte | **RESUMES**: Résumés jurisprudence | **MINISTERE**: Ministère | **IDCC**: Convention collective | **MOTS_CLES**: Mots-clés
"""


@mcp.resource("legifrance://documentation/types-recherche")
def documentation_types_recherche_legifrance() -> str:
    """Types de recherche Légifrance."""
    return """
# TYPES DE RECHERCHE

**EXACTE** (défaut, recommandé): Expression exacte | **TOUS_LES_MOTS_DANS_UN_CHAMP**: Tous les mots présents (ET) | **UN_DES_MOTS**: Au moins un mot (OU) | **AUCUN_DES_MOTS**: Exclusion de mots | **AUCUNE_CORRESPONDANCE_A_CETTE_EXPRESSION**: Exclusion expression exacte
"""


@mcp.resource("legifrance://documentation/options-tri")
def documentation_options_tri_legifrance() -> str:
    """Options de tri Légifrance."""
    return """
# TRI DES RÉSULTATS

**PERTINENCE** (recommandé): Score de pertinence | **SIGNATURE_DATE_DESC**: Date signature récente→ancienne | **SIGNATURE_DATE_ASC**: Date signature ancienne→récente | **DATE_PUBLI_DESC**: Date publication récente→ancienne | **DATE_PUBLI_ASC**: Date publication ancienne→récente
"""


@mcp.resource("legifrance://documentation/filtres-dates")
def documentation_filtres_dates_legifrance() -> str:
    """Filtres de dates Légifrance."""
    return """
# FILTRES DE DATES

Format: YYYY-MM-DD (date_debut obligatoire, date_fin optionnel)

⚠️ **FONDS COMPATIBLES**: JORF, LODA_DATE, LODA_ETAT (DATE_PUBLICATION) | JURI, CETAT, JUFI, CONSTIT (DATE_DECISION) | KALI, CIRC, ACCO (DATE_SIGNATURE)

❌ **INCOMPATIBLES**: ALL, CODE_DATE, CODE_ETAT, CNIL (filtres ignorés avec avertissement)

Note: DATE_PUBLICATION ≠ DATE_DECISION ≠ DATE_SIGNATURE. Pour jurisprudence: date de décision, pas de mise en ligne.
"""


@mcp.resource("judilibre://documentation/juridictions")
def documentation_juridictions_judilibre() -> str:
    """Juridictions Judilibre."""
    return """
# JURIDICTIONS

**cc**: Cour de cassation | **ca**: Cours d'appel | **tj**: Tribunaux judiciaires | **tcom**: Tribunaux de commerce
"""


@mcp.resource("judilibre://documentation/chambres")
def documentation_chambres_judilibre() -> str:
    """Chambres Cour de cassation."""
    return """
# CHAMBRES (Cour de cassation)

**pl**: Assemblée plénière | **mi**: Chambre mixte | **civ1**: 1ère civ. | **civ2**: 2e civ. | **civ3**: 3e civ. | **comm**: Commerciale | **soc**: Sociale | **cr**: Criminelle | **creun**: Chambres réunies | **ordo**: Ordonnance | **allciv**: Toutes civ. | **other**: Autre

Note: Claude convertit automatiquement les noms complets en codes.
"""


@mcp.resource("judilibre://documentation/solutions")
def documentation_solutions_judilibre() -> str:
    """Solutions des décisions."""
    return """
# SOLUTIONS

**cassation**: Cassation | **cassation_partielle**: Cassation partielle | **rejet**: Rejet | **annulation**: Annulation | **irrecevabilite**: Irrecevabilité | **desistement**: Désistement | **non-lieu**: Non-lieu | **qpc**: QPC
"""


@mcp.resource("judilibre://documentation/localisations")
def documentation_localisations_judilibre() -> str:
    """Localisations (sièges de juridictions)."""
    return """
# LOCALISATIONS

**Cours d'appel**: ca_<ville> (ex: ca_paris, ca_lyon) | **Tribunaux judiciaires**: tj<INSEE> (ex: tj75101=Paris, tj69123=Lyon) | **Tribunaux commerce**: tcom<INSEE>

Utiliser `obtenir_taxonomie_judilibre(taxonomy_id="location", context_value="ca|tj|tcom")` pour liste complète. Claude convertit automatiquement les noms de villes.
"""


@mcp.resource("judilibre://documentation/types-decision")
def documentation_types_decision_judilibre() -> str:
    """Types de décision."""
    return """
# TYPES DE DÉCISION

**arret**: Juridictions collégiales (cc, ca, ce, caa, crc) | **ordonnance**: Juge unique, référés, toutes juridictions | **qpc**: QPC (cc, ce uniquement) | **saisie**: Saisies (tj uniquement)
"""


@mcp.resource("judilibre://documentation/themes")
def documentation_themes_judilibre() -> str:
    """Thèmes juridiques."""
    return """
# THÈMES (Matières juridiques)

Liste longue (centaines). Catégories: **Civil** (responsabilité, contrats, famille, successions) | **Commercial** (sociétés, concurrence, PI, proc. collectives) | **Travail** (licenciement, salaires, sécurité sociale) | **Pénal** (infractions, procédure, peines) | **Admin** (fonction publique, urbanisme) | **Fiscal** (IR, TVA, IS)

Utiliser `obtenir_taxonomie_judilibre(taxonomy_id="theme")` pour codes exacts. Explorer sans filtre puis affiner.
"""


@mcp.resource("judilibre://documentation/options-tri")
def documentation_options_tri_judilibre() -> str:
    """Options de tri Judilibre."""
    return """
# TRI

**scorepub** (défaut, recommandé): Pertinence + publication (Bulletin>Rapport>Lettre>Communiqué>Non publié) | **score**: Pertinence seule | **date**: Date décision

**Ordre**: desc (défaut, récent→ancien) | asc (ancien→récent)
"""
