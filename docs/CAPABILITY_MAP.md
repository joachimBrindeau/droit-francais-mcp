# Capability Map — droit-francais-mcp

Ce document liste chaque capacité exposée par le serveur MCP. Toute évolution
(ajout / suppression / modification de signature) DOIT être reflétée ici.

Cf. [ce-agent-native-architecture / action-parity-discipline](https://every.to/) pour le rationale.

## Outils MCP (`@mcp.tool`)

| Tool | Endpoint PISTE | Méthode client Python | Notes |
|------|----------------|-----------------------|-------|
| `rechercher_legifrance` | `POST /search` (Légifrance) | `LegifranceAPI.search` | Recherche multi-fonds |
| `consulter_legifrance` | `POST /consult/{getArticle,legiPart,juri,cnil,kaliText,kaliArticle,acco,jorf}` | `LegifranceAPI.consult` | Routage par préfixe d'ID |
| `ping_legifrance` | `GET /search/ping` (Légifrance) | `LegifranceAPI.ping` | Diagnostic OAuth + connectivité |
| `obtenir_taxonomie_judilibre` | `GET /taxonomy` (JudiLibre) | `JudilibreAPI.taxonomy` | Listes de valeurs valides |
| `rechercher_jurisprudence_judilibre` | `GET /search` (JudiLibre) | `JudilibreAPI.search` | Recherche jurisprudence |
| `consulter_decision_judilibre` | `GET /decision` (JudiLibre) | `JudilibreAPI.consult` | Détails d'une décision |

**Parité** : chaque méthode publique des clients Python (`LegifranceAPI`,
`JudilibreAPI`) a un outil MCP correspondant. ✅

## Ressources MCP (`@mcp.resource`)

| URI | Sujet | Source |
|-----|-------|--------|
| `legifrance://context` | Workflow recommandé pour la recherche juridique (à lire en début de session) | `resources.py` |
| `legifrance://documentation/fonds` | Fonds Légifrance disponibles | `resources.py` |
| `legifrance://documentation/champs` | Types de champs de recherche | `resources.py` |
| `legifrance://documentation/types-recherche` | Modes de recherche (EXACTE, TOUS_LES_MOTS, …) | `resources.py` |
| `legifrance://documentation/options-tri` | Options de tri Légifrance | `resources.py` |
| `legifrance://documentation/filtres-dates` | Compatibilité fond ↔ filtre date | `resources.py` |
| `judilibre://documentation/juridictions` | Codes juridictions (cc/ca/tj/tcom) | `resources.py` |
| `judilibre://documentation/chambres` | Codes chambres Cour de cassation | `resources.py` |
| `judilibre://documentation/solutions` | Solutions (cassation, rejet, …) | `resources.py` |
| `judilibre://documentation/localisations` | Codes sièges (ca_paris, tj75101, …) | `resources.py` |
| `judilibre://documentation/types-decision` | Types (arret, ordonnance, qpc, saisie) | `resources.py` |
| `judilibre://documentation/themes` | Matières juridiques | `resources.py` |
| `judilibre://documentation/options-tri` | Options de tri JudiLibre | `resources.py` |

## Capacité opérationnelle dérivée (chaînages)

Ces capacités ne sont pas des outils dédiés : l'agent les compose à partir des
primitives ci-dessus. Documentées ici pour les utilisateurs.

| Capacité utilisateur | Composition |
|----------------------|-------------|
| « Trouve les arrêts récents de la Cour de cassation sur le harcèlement » | `obtenir_taxonomie_judilibre(taxonomy_id="chamber", context_value="cc")` puis `rechercher_jurisprudence_judilibre(recherche="harcèlement", juridiction="cc")` puis `consulter_decision_judilibre(decision_id=…)` pour les détails |
| « Cite l'article du Code civil sur le mariage » | `rechercher_legifrance(recherche="mariage", fond="CODE_ETAT", code="Code civil")` puis `consulter_legifrance(id="LEGIARTI…")` |
| « Vérifie que l'API Légifrance répond » | `ping_legifrance()` |

## Out-of-scope (intentionnel)

| Capacité | Raison de non-implémentation |
|----------|------------------------------|
| Écriture / mutation côté PISTE | Les API publiques PISTE sont en lecture seule. CRUD complet inapplicable. |
| Cache de résultats côté serveur | L'agent gère sa propre mémoire de session. Pas de duplication. |
| Authentification utilisateur | Le serveur MCP s'exécute localement avec les credentials de l'utilisateur via `.env`. |
| Réponse partielle / pagination automatique | Le serveur expose la pagination native (`page`, `page_taille`) ; l'agent décide la stratégie. |

## Évolution

Toute modification de cette table = modification du contrat MCP. Cf.
`tests/test_characterization.py::test_mcp_tool_count_and_names` et
`tests/test_resources.py::test_resource_count_matches_expected` qui pinent
le compte.
