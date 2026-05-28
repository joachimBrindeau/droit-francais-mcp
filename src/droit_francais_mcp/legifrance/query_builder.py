#!/usr/bin/env python3
"""
Générateur de requêtes pour l'API Légifrance
Basé sur SearchRequestDTO de la documentation Swagger

Copyright (c) 2025 Jean-Michel Tanguy
Licensed under the MIT License (see LICENSE file)

Remarques :
   Certaines parties de ce code ont été développées avec l’aide de Vibe Coding
   et d’outils d’intelligence artificielle.
"""

from typing import Any, ClassVar, Dict, FrozenSet, List


class LegifranceQueryBuilder:
    """Générateur de requêtes pour l'API Légifrance"""

    # Valeurs valides pour le type de recherche
    TYPE_RECHERCHE: ClassVar[FrozenSet[str]] = frozenset(
        {
            "UN_DES_MOTS",
            "EXACTE",
            "TOUS_LES_MOTS_DANS_UN_CHAMP",
            "AUCUN_DES_MOTS",
            "AUCUNE_CORRESPONDANCE_A_CETTE_EXPRESSION",
        }
    )

    # Valeurs valides pour le type de champ (cf. ressource MCP `legifrance://documentation/champs`).
    TYPE_CHAMP: ClassVar[FrozenSet[str]] = frozenset(
        {
            "ALL",
            "TITLE",
            "TABLE",
            "NOR",
            "NUM",
            "ADVANCED_TEXTE_ID",
            "NUM_DELIB",
            "NUM_DEC",
            "NUM_ARTICLE",
            "ARTICLE",
            "MINISTERE",
            "VISA",
            "NOTICE",
            "VISA_NOTICE",
            "TRAVAUX_PREP",
            "SIGNATURE",
            "NOTA",
            "NUM_AFFAIRE",
            "ABSTRATS",
            "RESUMES",
            "TEXTE",
            "ECLI",
            "NUM_LOI_DEF",
            "TYPE_DECISION",
            "NUMERO_INTERNE",
            "REF_PUBLI",
            "RESUME_CIRC",
            "TEXTE_REF",
            "TITRE_LOI_DEF",
            "RAISON_SOCIALE",
            "MOTS_CLES",
            "IDCC",
        }
    )

    # Descriptions détaillées des types de champs
    FONDS: ClassVar[FrozenSet[str]] = frozenset(
        {
            "ALL",
            "JORF",
            "CNIL",
            "CETAT",
            "JURI",
            "JUFI",
            "CONSTIT",
            "KALI",
            "CODE_DATE",
            "CODE_ETAT",
            "LODA_DATE",
            "LODA_ETAT",
            "CIRC",
            "ACCO",
        }
    )

    # Source de vérité unique: quels fonds supportent un filtre par date
    # et quelle facette utiliser. Utilisée par add_dates() ET par la couche MCP
    # (`droit_francais_MCP.rechercher_legifrance`) pour la validation.
    DATE_FILTER_FACETTES: ClassVar[Dict[str, str]] = {
        "JORF": "DATE_PUBLICATION",
        "LODA_DATE": "DATE_PUBLICATION",
        "LODA_ETAT": "DATE_PUBLICATION",
        "JURI": "DATE_DECISION",
        "CETAT": "DATE_DECISION",
        "JUFI": "DATE_DECISION",
        "CONSTIT": "DATE_DECISION",
        "KALI": "DATE_SIGNATURE",
        "CIRC": "DATE_SIGNATURE",
        "ACCO": "DATE_SIGNATURE",
    }

    # Fonds qui acceptent le filtre TEXT_NOM_CODE (recherche par nom de code).
    CODE_FONDS: ClassVar[FrozenSet[str]] = frozenset({"CODE_ETAT", "CODE_DATE"})

    # Fonds pour lesquels la couche client applique par défaut le filtre
    # ARTICLE_LEGAL_STATUS=VIGUEUR (textes actuellement en vigueur).
    VIGUEUR_DEFAULT_FONDS: ClassVar[FrozenSet[str]] = frozenset(
        {
            "JORF",
            "CODE_ETAT",
            "CODE_DATE",
            "LODA_DATE",
            "LODA_ETAT",
        }
    )

    @classmethod
    def supports_date_filter(cls, fond: str) -> bool:
        """Indique si le fond accepte un filtre date_debut/date_fin."""
        return fond in cls.DATE_FILTER_FACETTES

    @classmethod
    def date_filter_facette(cls, fond: str) -> str | None:
        """Renvoie la facette de date utilisée par le fond, ou `None`."""
        return cls.DATE_FILTER_FACETTES.get(fond)

    # Descriptions détaillées des fonds
    def __init__(self) -> None:
        self.query: Dict[str, Any] = {
            "fond": "",
            "recherche": {
                "champs": [],
                "filtres": [],
                "pageNumber": 1,
                "pageSize": 50,
                "operateur": "ET",
                "sort": "PERTINENCE",
                "secondSort": "DATE_DESC",
                "typePagination": "DEFAUT",
            },
        }

    def set_fond(self, fond: str) -> "LegifranceQueryBuilder":
        """
        Définit le fonds de recherche.

        Args:
            fond (str): Fonds sur lequel appliquer la recherche.
                Pour rechercher dans tous les fonds, utiliser 'ALL'.
                Pour les fonds LODA et CODE, deux types de recherche existent :
                - _DATE : recherche par date de version (CODE_DATE, LODA_DATE)
                - _ETAT : recherche par état juridique (CODE_ETAT, LODA_ETAT)

                Valeurs possibles:
                - JORF : Journal Officiel de la République Française
                - CNIL : Commission Nationale de l'Informatique et des Libertés
                - CETAT : Conseil d'État
                - JURI : Jurisprudence judiciaire
                - JUFI : Jurisprudence financière
                - CONSTIT : Conseil Constitutionnel
                - KALI : Conventions collectives
                - CODE_DATE : Codes consolidés (par date)
                - CODE_ETAT : Codes consolidés (par état juridique)
                - LODA_DATE : Lois, Ordonnances, Décrets, Arrêtés (par date)
                - LODA_ETAT : Lois, Ordonnances, Décrets, Arrêtés (par état)
                - ALL : Tous les fonds
                - CIRC : Circulaires et instructions
                - ACCO : Accords d'entreprise

        Returns:
            LegifranceQueryBuilder: Instance pour chaînage des méthodes

        Raises:
            ValueError: Si le fonds spécifié n'est pas valide
        """
        if fond not in self.FONDS:
            raise ValueError(f"Fonds invalide. Utilisez une des valeurs: {sorted(self.FONDS)}")
        self.query["fond"] = fond
        return self

    def add_field(
        self, type_champ: str, criteres: List[Dict[str, Any]], operateur: str = "ET"
    ) -> "LegifranceQueryBuilder":
        """
        Ajoute un champ de recherche (objet ChampDTO dans l'API Légifrance).

        Cette méthode permet de définir dans quel champ de document effectuer la recherche
        et quels critères de recherche y appliquer.

        Args:
            type_champ (str): Type de champ dans lequel rechercher.
                Il est possible d'utiliser 'ALL' pour rechercher dans tous les champs.

                Valeurs possibles (selon ChampDTO de l'API):
                - ALL : Tous les champs
                - TITLE : Titre du texte
                - TABLE : Table des matières
                - NOR : Numéro d'ordre réglementaire
                - NUM : Numéro du texte
                - ADVANCED_TEXTE_ID : Identifiant technique du texte
                - NUM_DELIB : Numéro de délibération
                - NUM_DEC : Numéro de décision
                - NUM_ARTICLE : Numéro d'article
                - ARTICLE : Contenu des articles
                - MINISTERE : Ministère émetteur
                - VISA : Visas du texte
                - NOTICE : Notice du texte
                - VISA_NOTICE : Visas et notice combinés
                - TRAVAUX_PREP : Travaux préparatoires
                - SIGNATURE : Signataires
                - NOTA : Nota du texte
                - NUM_AFFAIRE : Numéro d'affaire (jurisprudence)
                - ABSTRATS : Résumés/abstracts
                - RESUMES : Résumés
                - TEXTE : Contenu textuel complet
                - ECLI : Identifiant ECLI (jurisprudence européenne)
                - NUM_LOI_DEF : Numéro de loi déférée
                - TYPE_DECISION : Type de décision
                - NUMERO_INTERNE : Numéro interne
                - REF_PUBLI : Référence de publication
                - RESUME_CIRC : Résumé de circulaire
                - TEXTE_REF : Texte de référence
                - TITRE_LOI_DEF : Titre de loi déférée
                - RAISON_SOCIALE : Raison sociale (accords d'entreprise)
                - MOTS_CLES : Mots-clés
                - IDCC : Identifiant de convention collective

            criteres (List[Dict]): Liste des critères/groupes de critères de recherche pour ce champ.
                Chaque critère doit être créé avec la méthode create_critere().
                Les critères définissent les mots ou expressions à rechercher dans le champ.

            operateur (str, optional): Opérateur entre les critères de recherche.
                Défaut: "ET"
                Valeurs possibles:
                - "ET" : Tous les critères doivent être satisfaits (AND logique)
                - "OU" : Au moins un critère doit être satisfait (OR logique)

        Returns:
            LegifranceQueryBuilder: Instance pour chaînage des méthodes

        Raises:
            ValueError: Si le type de champ spécifié n'est pas valide

        Example:
            >>> search = LegifranceQueryBuilder()
            >>> critere1 = search.create_critere("mariage", "EXACTE")
            >>> critere2 = search.create_critere("divorce", "UN_DES_MOTS")
            >>> search.add_champ("TITLE", [critere1, critere2], "OU")
        """
        if type_champ not in self.TYPE_CHAMP:
            raise ValueError(
                f"Type de champ invalide. Utilisez une des valeurs: {sorted(self.TYPE_CHAMP)}"
            )

        champ = {"typeChamp": type_champ, "criteres": criteres, "operateur": operateur}
        self.query["recherche"]["champs"].append(champ)
        return self

    def create_criteria(
        self,
        valeur: str,
        type_recherche: str = "TOUS_LES_MOTS_DANS_UN_CHAMP",
        operateur: str = "ET",
        proximite: int | None = None,  # Nombre maximum de mots entre les termes recherchés,
        criteres: List[Dict[str, Any]] | None = None,
    ) -> Dict[str, Any]:
        """
        Crée un critère de recherche (objet CritereDTO dans l'API Légifrance).

        Un critère définit ce qui doit être recherché dans un champ spécifique.
        Les critères peuvent être imbriqués pour créer des groupes de critères complexes.

        Args:
            valeur (str): Mot(s) ou expression recherchés.
                Exemples: "dispositions", "mariage pour tous", "Code civil"

            type_recherche (str, optional): Type de recherche effectuée.
                Défaut: "UN_DES_MOTS"

                Valeurs possibles (selon CritereDTO de l'API):
                - "UN_DES_MOTS" : Au moins un des mots doit être présent
                - "EXACTE" : L'expression exacte doit être présente
                - "TOUS_LES_MOTS_DANS_UN_CHAMP" : Tous les mots doivent être présents dans le champ
                - "AUCUN_DES_MOTS" : Aucun des mots ne doit être présent (exclusion)
                - "AUCUNE_CORRESPONDANCE_A_CETTE_EXPRESSION" : L'expression ne doit pas être présente (exclusion)

            operateur (str, optional): Opérateur entre les sous-critères (si criteres est défini).
                Défaut: "ET"
                Valeurs possibles:
                - "ET" : Tous les sous-critères doivent être satisfaits (AND logique)
                - "OU" : Au moins un sous-critère doit être satisfait (OR logique)

            proximite (int, optional): Proximité maximum entre les mots du champ valeur.
                La proximité représente la distance maximale, en mots, entre deux termes recherchés.
                Par exemple, proximite=2 signifie qu'au maximum 2 mots peuvent séparer les termes recherchés.
                Défaut: None (pas de contrainte de proximité)

                Exemple:
                    Avec valeur="fonction publique" et proximite=3, les expressions suivantes seront trouvées:
                    - "fonction publique" (0 mots entre)
                    - "fonction de la publique" (2 mots entre)
                    - "fonction territoriale ou publique" (2 mots entre)
                    Mais pas: "fonction de la République publique" (3 mots entre, dépasse la limite)

            criteres (List[Dict], optional): Sous-critère/Sous-groupe de critères.
                Permet de créer des requêtes imbriquées complexes.
                Chaque élément doit être un dictionnaire créé avec create_critere().
                Défaut: None (pas de sous-critères)

                Exemple de structure imbriquée:
                    critere_parent avec sous-critères:
                    - critere_enfant_1: "soins" ET
                    - critere_enfant_2: "fonction publique" (avec proximité)

        Returns:
            Dict: Dictionnaire représentant le critère, conforme au format CritereDTO de l'API

        Raises:
            ValueError: Si le type de recherche spécifié n'est pas valide

        Examples:
            >>> # Recherche simple d'un mot
            >>> search = LegifranceQueryBuilder()
            >>> critere = search.create_critere("mariage", "EXACTE")

            >>> # Recherche avec proximité
            >>> critere = search.create_critere("fonction publique", "TOUS_LES_MOTS_DANS_UN_CHAMP", proximite=3)

            >>> # Recherche avec sous-critères imbriqués
            >>> sous_critere1 = search.create_critere("soins", "UN_DES_MOTS")
            >>> sous_critere2 = search.create_critere("fonction publique", "TOUS_LES_MOTS_DANS_UN_CHAMP", proximite=3)
            >>> critere_parent = search.create_critere(
            ...     "dispositions",
            ...     "UN_DES_MOTS",
            ...     operateur="ET",
            ...     proximite=2,
            ...     criteres=[sous_critere1, sous_critere2]
            ... )
        """
        if type_recherche not in self.TYPE_RECHERCHE:
            raise ValueError(
                f"Type de recherche invalide. Utilisez une des valeurs: {sorted(self.TYPE_RECHERCHE)}"
            )

        critere: Dict[str, Any] = {
            "valeur": valeur,
            "typeRecherche": type_recherche,
            "operateur": operateur,
        }

        if proximite is not None:
            critere["proximite"] = proximite

        if criteres is not None:
            critere["criteres"] = criteres

        return critere

    def add_filtre(self, facette: str, valeurs: List[str]) -> "LegifranceQueryBuilder":
        """
        Ajoute un filtre par valeurs (objet FiltreDTO dans l'API Légifrance).

        Les filtres permettent de restreindre les résultats selon des critères spécifiques
        comme la nature du texte, la juridiction, etc. La requête est effectuée automatiquement
        avec un opérateur ET entre les filtres listés.

        Args:
            facette (str): Nom de la facette => nom du filtre.
                Les facettes disponibles dépendent du fonds recherché et sont retournées
                dynamiquement dans les réponses de l'API (SearchResponseDTO.facets).

                **FACETTES COMMUNES À PLUSIEURS FONDS:**

                - **NATURE** : Nature du texte
                  Valeurs possibles: LOI, ORDONNANCE, ARRETE, DECRET, CODE, CIRCULAIRE,
                                    CONSTITUTION, TRAITE, ACCORD, CONVENTION, REGLEMENT, etc.

                - **ETAT_JURIDIQUE** (ou legalStatus) : État juridique du texte
                  Valeurs possibles: VIGUEUR, ABROGE, ABROGE_DIFF, VIGUEUR_DIFF,
                                    VIGUEUR_ETEN, VIGUEUR_NON_ETEN, PERIME, ANNULE,
                                    MODIFIE, DISJOINT, SUBSTITUE, TRANSFERE, INITIALE,
                                    MODIFIE_MORT_NE, SANS_ETAT, DENONCE, REMPLACE

                **FACETTES SPÉCIFIQUES AUX FONDS JURIDICTIONNELS (CETAT, JURI, JUFI, CONSTIT):**

                - **JURIDICTION** : Juridiction émettrice
                  Valeurs possibles: Conseil d'État, Cour de cassation, Cour des comptes,
                                    Conseil constitutionnel, Tribunal administratif,
                                    Cour d'appel, etc.

                - **JURIDICTION_NATURE** : Nature de la juridiction
                  Valeurs possibles: TRIBUNAL_ADMINISTRATIF, COURS_APPEL, COURS_COMPTES,
                                    CONSEIL_ETAT, COUR_CASSATION, TRIBUNAL_CONFLITS,
                                    COUR_JUSTICE_REPUBLIQUE, etc.

                - **TYPE_DECISION** : Type de décision
                  Valeurs possibles: ARRET, ORDONNANCE, AVIS, DECISION, JUGEMENT, etc.

                - **CHAMBRE** : Chambre de la juridiction
                  Valeurs possibles: Première chambre civile, Chambre criminelle,
                                    Chambre sociale, Chambre commerciale, etc.

                - **FORMATION** : Formation de jugement
                  Valeurs possibles: Plénière, Section, Assemblée, etc.

                **FACETTES SPÉCIFIQUES AU FONDS JORF (Journal Officiel):**

                - **MINISTERE** : Ministère émetteur
                  Valeurs possibles: Ministère de la Justice, Ministère de l'Intérieur,
                                    Ministère des Finances, Ministère de la Santé, etc.

                - **NUM_PARUTION** : Numéro de parution du JO

                **FACETTES SPÉCIFIQUES AU FONDS KALI (Conventions collectives):**

                - **IDCC** : Identifiant de Convention Collective
                  Valeurs possibles: Numéros IDCC (ex: "1880", "2120", etc.)

                - **MOTS_CLES** : Mots-clés thématiques
                  Valeurs possibles: ABATTOIRS, CHAUX HYDRAULIQUES, ENSEIGNEMENT,
                                    TRANSPORT, COMMERCE, etc.

                - **TYPE_TEXTE** : Type de texte conventionnel
                  Valeurs possibles: TEXTE_BASE, TEXTE_ATTACHE, TEXTE_ETENDU, etc.

                **FACETTES SPÉCIFIQUES AU FONDS CIRC (Circulaires):**

                - **MINISTERE_DEPOSANT** : Ministère déposant la circulaire

                - **ETAT_CIRCULAIRE** : État de la circulaire
                  Valeurs possibles: VIGUEUR (V), ABROGE (A), etc.

                **FACETTES SPÉCIFIQUES AU FONDS ACCO (Accords d'entreprise):**

                - **RAISON_SOCIALE** : Raison sociale de l'entreprise

                - **THEME** : Thème de l'accord
                  Valeurs possibles: Salaires, Temps de travail, Formation, etc.

                **FACETTES SPÉCIFIQUES AUX DÉBATS ET QUESTIONS PARLEMENTAIRES:**

                - **TYPE_PARLEMENT** : Type de parlement
                  Valeurs possibles: AN (Assemblée Nationale), SENAT (Sénat)

                - **LEGISLATURE** : Législature
                  Valeurs possibles: 14, 15, 16, etc.

                **AUTRES FACETTES:**

                - **ANNEE** (years) : Année de publication/signature

                - **CODE_NAME** : Nom du code (pour le fonds CODE)
                  Valeurs possibles: Code civil, Code pénal, Code du travail, etc.

            valeurs (List[str]): Liste des valeurs du filtre dans le cas d'un filtre textuel.
                Les valeurs exactes dépendent de la facette choisie.
                Utilisez les valeurs retournées par l'API dans les facettes de réponse.

        Returns:
            LegifranceQueryBuilder: Instance pour chaînage des méthodes

        Note:
            - Plusieurs filtres peuvent être ajoutés. Ils seront combinés avec un opérateur ET.
            - Les facettes disponibles varient selon le fonds recherché.
            - Consultez d'abord les résultats d'une recherche pour voir les facettes disponibles
              et leurs valeurs possibles dans le contexte de votre fonds.

        Examples:
            >>> search = LegifranceQueryBuilder()
            >>> # Filtrer par nature de texte (JORF, LODA)
            >>> search.add_filtre_valeurs("NATURE", ["LOI", "ORDONNANCE", "ARRETE"])
            >>>
            >>> # Filtrer par juridiction (CETAT, JURI)
            >>> search.add_filtre_valeurs("JURIDICTION_NATURE", ["TRIBUNAL_ADMINISTRATIF", "COURS_APPEL"])
            >>>
            >>> # Filtrer par état juridique
            >>> search.add_filtre_valeurs("ETAT_JURIDIQUE", ["VIGUEUR", "VIGUEUR_DIFF"])
            >>>
            >>> # Filtrer par IDCC pour conventions collectives (KALI)
            >>> search.add_filtre_valeurs("IDCC", ["1880", "2120"])
            >>>
            >>> # Filtrer par ministère (JORF)
            >>> search.add_filtre_valeurs("MINISTERE", ["Ministère de la Justice"])
        """
        filtre = {"facette": facette, "valeurs": valeurs}
        self.query["recherche"]["filtres"].append(filtre)
        return self

    def add_dates(self, start_date: str, end_date: str | None = None) -> "LegifranceQueryBuilder":
        """
        Ajoute un filtre par période de dates (objet FiltreDTO avec DatePeriod dans l'API Légifrance).

        Permet de filtrer les résultats sur une plage de dates définie.

        Attention : fond doit etre défini avant d'utiliser cette méthode.

        Args:

        # La date de recherche est spécifique au fond
        # Une facette principale est généralement admise pour les fonds qui supportent le filtrage
        # La liste est le résultat d'un scan exhaustif des fonds et facettes.
        # JORF : DATE_PUBLICATION
        # LODA_DATE : DATE_PUBLICATION
        # LODA_ETAT : DATE_PUBLICATION
        # JURI : DATE_DECISION
        # CETAT : DATE_DECISION
        # JUFI : DATE_DECISION
        # CONSTIT : DATE_DECISION
        # KALI : DATE_SIGNATURE
        # CIRC : DATE_SIGNATURE
        # ACCO : DATE_SIGNATURE

        ⚠️ Pour tous les autres fonds, le filtrage par date est ignoré.

            start_date (str): Date de début de la période.
                Format: "YYYY-MM-DD" (ex: "2015-01-01")
                Le format ISO 8601 est requis.

            end_date (str, optional): Date de fin de la période. optionnel
                Format: "YYYY-MM-DD" (ex: "2018-01-31")
                Le format ISO 8601 est requis.

        Returns:
            LegifranceQueryBuilder: Instance pour chaînage des méthodes

        """
        # La facette à utiliser est dérivée du fond via DATE_FILTER_FACETTES (SSOT).
        fond = self.query.get("fond", "")
        facette_principale = self.DATE_FILTER_FACETTES.get(fond)
        if facette_principale is None:
            # Fond sans support du filtrage par date
            return self

        # Apply date filter
        if end_date is not None:
            # Comportement normal avec start et end
            filtre = {
                "facette": facette_principale,
                "dates": {"start": start_date, "end": end_date},
            }
        else:
            # Seulement start (comportement par défaut pour ALL ou si end_date n'est pas fourni)
            filtre = {"facette": facette_principale, "dates": {"start": start_date}}

        self.query["recherche"]["filtres"].append(filtre)
        return self

    def set_pagination(
        self, page_number: int = 0, page_size: int = 10, type_pagination: str = "DEFAUT"
    ) -> "LegifranceQueryBuilder":
        """
        Configure la pagination des résultats (selon RechercheSpecifiqueDTO de l'API Légifrance).

        Args:
            page_number (int, optional): Numéro de la page à consulter.
                Défaut: 0(première page)


            page_size (int, optional): Nombre d'éléments par page.
                Défaut: 10
                Maximum: 50 (la valeur sera automatiquement limitée à 50 si dépassée)

            type_pagination (str, optional): Type de pagination.
                Défaut: "DEFAUT"

                Valeurs possibles:
                - "DEFAUT" : Pagination standard (DEFAULT dans l'API)
                - "ARTICLE" : Pagination spécifique pour les recherches dans les articles d'un texte

                Note: Dans la plupart des cas, utiliser "DEFAUT".
                Lors de la navigation dans plusieurs pages, il est nécessaire de passer
                la valeur reçue dans la réponse précédente.

        Returns:
            LegifranceQueryBuilder: Instance pour chaînage des méthodes

        Examples:
            >>> search = LegifranceQueryBuilder()
            >>> # Pagination standard : 50 résultats par page, page 1
            >>> search.set_pagination(page_number=1, page_size=50)
            >>> # Aller à la page 3 avec 25 résultats par page
            >>> search.set_pagination(page_number=3, page_size=25)
        """
        self.query["recherche"]["pageNumber"] = page_number
        self.query["recherche"]["pageSize"] = min(page_size, 50)  # Max 50
        self.query["recherche"]["typePagination"] = type_pagination
        return self

    def set_operator(self, operator: str) -> "LegifranceQueryBuilder":
        """
        Définit l'opérateur global entre les champs de recherche (selon RechercheSpecifiqueDTO de l'API).

        Cet opérateur détermine comment les différents champs de recherche sont combinés.

        Args:
            operateur (str): Opérateur entre les champs de recherche.

                Valeurs possibles:
                - "ET" : Tous les champs doivent correspondre (AND logique)
                         Exemple: Si vous recherchez "mariage" dans TITLE ET "divorce" dans ARTICLE,
                         seuls les documents contenant les deux seront retournés.

                - "OU" : Au moins un champ doit correspondre (OR logique)
                         Exemple: Si vous recherchez "mariage" dans TITLE OU "divorce" dans ARTICLE,
                         les documents contenant l'un ou l'autre (ou les deux) seront retournés.

        Returns:
            LegifranceQueryBuilder: Instance pour chaînage des méthodes

        Raises:
            ValueError: Si l'opérateur n'est pas "ET" ou "OU"

        Examples:
            >>> search = LegifranceQueryBuilder()
            >>> # Les documents doivent correspondre à TOUS les champs
            >>> search.set_operateur_global("ET")
            >>> # Les documents doivent correspondre à AU MOINS UN champ
            >>> search.set_operateur_global("OU")
        """
        if operator not in ["ET", "OU"]:
            raise ValueError("L'opérateur doit être 'ET' ou 'OU'")
        self.query["recherche"]["operateur"] = operator
        return self

    def set_sort(self, sort: str, second_sort: str | None = None) -> "LegifranceQueryBuilder":
        """
        Configure le tri des résultats (selon RechercheSpecifiqueDTO de l'API Légifrance).

        Les tris possibles dépendent du fonds recherché.

        Args:
            sort (str): Tri principal des éléments trouvés.

                Exemples de valeurs courantes (selon le fonds):
                - "PERTINENCE" : Tri par pertinence (défaut recommandé)
                - "SIGNATURE_DATE_DESC" : Date de signature décroissante (plus récent en premier)
                - "SIGNATURE_DATE_ASC" : Date de signature croissante
                - "DATE_PUBLI_DESC" : Date de publication décroissante
                - "DATE_PUBLI_ASC" : Date de publication croissante
                - "DATE_VERSION_DESC" : Date de version décroissante
                - "DATE_VERSION_ASC" : Date de version croissante
                - "ID_DESC" : Identifiant décroissant
                - "ID_ASC" : Identifiant croissant
                - "DATE_UPDATE" : Date de mise à jour

                Note: Les options de tri disponibles varient selon le fonds (JORF, LODA, CODE, etc.)

            second_sort (str, optional): Tri secondaire des éléments trouvés.
                Appliqué lorsque le tri principal donne des résultats identiques.
                Accepte les mêmes valeurs que le paramètre 'sort'.
                Défaut: None (pas de tri secondaire)

                Exemples:
                - "ID" : Par identifiant
                - "DATE_DESC" : Par date décroissante
                - "DATE_ASC" : Par date croissante

        Returns:
            LegifranceQueryBuilder: Instance pour chaînage des méthodes

        Examples:
            >>> search = LegifranceQueryBuilder()
            >>> # Tri par pertinence uniquement
            >>> search.set_sort("PERTINENCE")
            >>> # Tri par date de signature décroissante, puis par ID
            >>> search.set_sort("SIGNATURE_DATE_DESC", "ID")
            >>> # Tri par date de publication, puis par date de signature
            >>> search.set_sort("DATE_PUBLI_DESC", "SIGNATURE_DATE_DESC")
        """
        self.query["recherche"]["sort"] = sort
        if second_sort:
            self.query["recherche"]["secondSort"] = second_sort
        return self

    def set_advanced_search(self, advanced: bool = True) -> "LegifranceQueryBuilder":
        """
        Active ou désactive le mode de recherche avancée (selon RechercheSpecifiqueDTO de l'API).

        Ce paramètre permet d'indiquer s'il s'agit d'une recherche avancée ou simple.

        Args:
            advanced (bool, optional): Déterminer s'il s'agit d'une recherche avancée.
                Défaut: True

                Valeurs:
                - True : Mode recherche avancée activé
                - False : Mode recherche simple

        Returns:
            LegifranceQueryBuilder: Instance pour chaînage des méthodes

        Examples:
            >>> search = LegifranceQueryBuilder()
            >>> # Activer la recherche avancée
            >>> search.set_advanced_search(True)
            >>> # Désactiver la recherche avancée (recherche simple)
            >>> search.set_advanced_search(False)
        """
        self.query["recherche"]["fromAdvancedRecherche"] = advanced
        return self

    def build(self) -> Dict[str, Any]:
        """
        Construit et retourne la requête finale au format SearchRequestDTO de l'API Légifrance.

        Valide que tous les paramètres requis sont définis et retourne un dictionnaire
        représentant la requête complète prête à être envoyée à l'API.

        Returns:
            Dict: Dictionnaire représentant la requête de recherche complète,
                  conforme au format SearchRequestDTO de l'API Légifrance.

                  Structure retournée:
                  {
                      "fond": "LODA_DATE",  # Fonds de recherche
                      "recherche": {         # Objet RechercheSpecifiqueDTO
                          "champs": [...],   # Liste des champs de recherche (ChampDTO)
                          "filtres": [...],  # Liste des filtres (FiltreDTO)
                          "pageNumber": 1,   # Numéro de page
                          "pageSize": 50,    # Taille de page
                          "operateur": "ET", # Opérateur global
                          "sort": "PERTINENCE",  # Tri principal
                          "secondSort": "DATE_DESC",  # Tri secondaire (optionnel)
                          "typePagination": "DEFAUT",  # Type de pagination
                          "fromAdvancedRecherche": false  # Mode recherche avancée (optionnel)
                      }
                  }

        Raises:
            ValueError: Si le fonds n'a pas été défini avec set_fond()

        Examples:
            >>> search = LegifranceQueryBuilder()
            >>> search.set_fond("LODA_DATE")
            >>> critere = search.create_critere("mariage", "EXACTE")
            >>> search.add_champ("TITLE", [critere])
            >>> query = search.build()
            >>> print(query)
            {'fond': 'LODA_DATE', 'recherche': {...}}
        """
        if not self.query["fond"]:
            raise ValueError("Le fonds doit être défini")
        return self.query.copy()
