#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Client pour l'API JudiLibre via PISTE.
Documentation de l'API JudiLibre : https://piste.gouv.fr/api-judilibre/

Copyright (c) 2025 Jean-Michel Tanguy
Licensed under the MIT License (see LICENSE file)

Remarques :
   Certaines parties de ce code ont été développées avec l’aide de Vibe Coding
   et d’outils d’intelligence artificielle.
"""

import os
import requests
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

class JudilibreAPI:
    """
    Client OAuth pour l'API JudiLibre
    """

    def __init__(self, sandbox: bool = True):
        """
        Initialise le client OAuth

        Args:
            client_id: Identifiant client fourni par Légifrance
            client_secret: Secret client fourni par Légifrance
        """
        load_dotenv(verbose=False)
        if sandbox:
            self.client_id = os.getenv("PISTE_SANDBOX_CLIENT_ID")
            self.client_secret = os.getenv("PISTE_SANDBOX_CLIENT_SECRET")
            self.token_url = "https://sandbox-oauth.piste.gouv.fr/api/oauth/token"
            self.base_url = "https://sandbox-api.piste.gouv.fr"
        else:
            self.client_id = os.getenv("PISTE_CLIENT_ID")
            self.client_secret = os.getenv("PISTE_CLIENT_SECRET")
            self.token_url = "https://oauth.piste.gouv.fr/api/oauth/token"
            self.base_url = "https://api.piste.gouv.fr"

        self.api_url = f"{self.base_url}/cassation/judilibre/v1.0"

        # Stockage du token
        self.access_token: Optional[str] = None
        self.token_expires_at: Optional[datetime] = None

    def get_access_token(self) -> str:
        """
        Obtient un token d'accès via OAuth 2.0 Client Credentials

        Returns:
            Token d'accès
        """
        # Vérifier si le token existant est encore valide
        if self.access_token and self.token_expires_at:
            if datetime.now() < self.token_expires_at:
                return self.access_token

        data = {
            "Accept-Encoding": "gzip,deflate",
            "Content-Type": "application/x-www-form-urlencoded",
            "Host": self.token_url.replace("https://", "").split("/")[0],
            "Connection": "Keep-Alive",
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": "openid",
        }

        try:
            response = requests.post(self.token_url, data=data)
            response.raise_for_status()

            token_data = response.json()
            access_token: str = token_data["access_token"]
            self.access_token = access_token

            # Calculer l'expiration du token (avec marge de sécurité)
            expires_in = token_data.get("expires_in", 3600)
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)

            return access_token

        except requests.exceptions.RequestException as e:
            raise Exception(f"Erreur lors de l'obtention du token: {e}")

    def _get_api_headers(self) -> Dict[str, str]:
        """
        Génère les en-têtes pour les appels API
        """
        token = self.get_access_token()
        return {
            "Authorization": f"Bearer {token}",
        }

    def search(
        self,
        query: Optional[str] = None,
        field: Optional[List[str]] = None,
        operator: str = "and",
        type: Optional[List[str]] = None,
        theme: Optional[List[str]] = None,
        chamber: Optional[List[str]] = None,
        formation: Optional[List[str]] = None,
        jurisdiction: Optional[List[str]] = ["cc", "ca", "tj", "tcom"], # Par défaut toutes les juridictions
        location: Optional[List[str]] = None,
        publication: Optional[List[str]] = None,
        solution: Optional[List[str]] = None,
        date_start: Optional[str] = None,
        date_end: Optional[str] = None,
        sort: str = "scorepub",
        order: str = "desc",
        page_size: int = 50,
        page: int = 0,
        resolve_references: bool = True,
        withFileOfType: Optional[List[str]] = None,
        particularInterest: bool = False,
    ) -> Any:
        """
        Effectue une recherche dans la base de données ouverte des décisions de justice JudiLibre

        Args:
            query: Chaîne de caractères correspondant à la recherche. Une recherche avec un
                   paramètre query vide ou manquant est ignorée et retourne un résultat vide.
            field: Liste des champs, métadonnées ou zones de contenu ciblés par la recherche
                   (parmi les valeurs : expose, moyens, motivations, dispositif, annexes,
                   sommaire, titrage, etc. - les valeurs disponibles sont accessibles via
                   GET /taxonomy?id=field). Une recherche avec un paramètre field vide ou
                   manquant est appliquée à l'intégralité de la décision (introduction et
                   moyens annexés compris) mais va exclure les métadonnées (sommaire, titrage, etc.).
            operator: Opérateur logique reliant les multiples termes que le paramètre query
                     peut contenir (or , and par défaut ou exact – dans ce dernier cas le
                     moteur recherchera exactement le contenu du paramètre query).
            type: Filtre les résultats suivant la nature des décisions (parmi les valeurs :
                  arret, qpc, ordonnance, saisie, etc. - les valeurs disponibles sont
                  accessibles via GET /taxonomy?id=type). Une recherche avec un paramètre
                  type vide ou manquant retourne des décisions de toutes natures.
            theme: Filtre les résultats suivant la matière (nomenclature de la Cour de cassation)
                   relative aux décisions (les valeurs disponibles sont accessibles via
                   GET /taxonomy?id=theme). Une recherche avec un paramètre theme vide ou
                   manquant retourne des décisions relatives à toutes les matières.
            chamber: Filtre les résultats suivant la chambre relative aux décisions.
                    ⚠️ IMPORTANT: Utiliser les CLÉS (keys) du dictionnaire suivant, PAS les valeurs:

                    CLÉS DISPONIBLES POUR CHAMBER (Cour de cassation):
                    - "pl"     : Assemblée plénière
                    - "mi"     : Chambre mixte
                    - "civ1"   : Première chambre civile
                    - "civ2"   : Deuxième chambre civile
                    - "civ3"   : Troisième chambre civile
                    - "comm"   : Chambre commerciale financière et économique
                    - "soc"    : Chambre sociale
                    - "cr"     : Chambre criminelle
                    - "creun"  : Chambres réunies
                    - "ordo"   : Première présidence (Ordonnance)
                    - "allciv" : Toutes les chambres civiles
                    - "other"  : Autre

                    Exemple: chamber=["civ1", "comm"] pour filtrer sur la 1ère chambre civile
                            et la chambre commerciale.

                    Une recherche avec un paramètre chamber vide ou manquant retourne des
                    décisions relatives à toutes les chambres.

                    Note: Les valeurs disponibles peuvent aussi être récupérées dynamiquement via
                    GET /taxonomy?id=chamber ou api.get_taxonomy_values("chamber").
            formation: Filtre les résultats suivant la formation relative aux décisions (les
                      valeurs disponibles sont accessibles via GET /taxonomy?id=formation).
                      Une recherche avec un paramètre formation vide ou manquant retourne des
                      décisions relatives à toutes les formations.
            jurisdiction: Filtre les résultats suivant la juridiction relative aux décisions
                         (les valeurs disponibles sont accessibles via GET /taxonomy?id=jurisdiction).
                         Une recherche avec un paramètre jurisdiction vide ou manquant retourne
                         des décisions relatives à la Cour de cassation (cc).
            location: Filtre les résultats suivant le code du siège de juridiction ayant émis
                     les décisions (les valeurs disponibles sont accessibles via
                     GET /taxonomy?id=location&context_value=ca pour les cours d'appel et
                     GET /taxonomy?id=location&context_value=tj pour les tribunaux judiciaires).
                     Par exemple : GET /search?...&location=tj33063.
            publication: Filtre les résultats suivant le niveau de publication des décisions
                        (parmi les valeurs : b, r, l, c, etc. - les valeurs disponibles sont
                        accessibles via GET /taxonomy?id=publication). Une recherche avec un
                        paramètre publication vide ou manquant retourne des décisions de
                        n'importe quel niveau de publication.
            solution: Filtre les résultats suivant le type de solution des décisions (parmi
                     les valeurs : annulation, avis, cassation, decheance, designation,
                     irrecevabilite, nonlieu, qpc, rabat, etc. - les valeurs disponibles sont
                     accessibles via GET /taxonomy?id=solution). Une recherche avec un
                     paramètre solution vide retourne des décisions ayant n'importe quel type
                     de solution.
            date_start: Combiné avec le paramètre date_end, permet de restreindre les résultats
                       à un intervalle de dates, au format ISO-8601 (par exemple 2021-05-13,
                       2021-05-13T06:00:00Z).
            date_end: Combiné avec le paramètre date_start, permet de restreindre les résultats
                     à un intervalle de dates, au format ISO-8601 (par exemple 2021-05-13,
                     2021-05-13T06:00:00Z).
            sort: Permet de choisir la valeur suivant laquelle les résultats sont triés
                 (score pour un tri par pertinence, scorepub pour un tri par pertinence et
                 niveau de publication et date pour un tri par date, vaut scorepub par défaut).
            order: Permet de choisir l'ordre du tri (asc pour un tri ascendant ou desc pour
                  un tri descendant, vaut desc par défaut).
            page_size: Permet de déterminer le nombre de résultats retournés par page
                      (50 maximum, vaut 10 par défaut).
            page: Permet de déterminer le numéro de la page de résultats à retourner
                 (la première page valant 0).
            resolve_references: Lorsque ce paramètre vaut true, le résultat de la requête
                               contiendra, pour chaque information retournée par défaut sous
                               forme de clé, l'intitulé complet de celle-ci (vaut true par défaut).
            withFileOfType: Filtre les résultats suivant le type de documents associés aux
                           décisions, parmi les valeurs : prep_rapp (Rapport du rapporteur),
                           prep_avis (Avis de l'avocat général), prep_oral (Avis oral de
                           l'avocat général), comm_comm (Communiqué), comm_note (Note explicative),
                           comm_nora (Notice au rapport annuel), comm_lett (Lettre de chambre),
                           comm_trad (Arrêt traduit). Les valeurs disponibles sont accessibles
                           via GET /taxonomy?id=filetype.
            particularInterest: Lorsque ce paramètre vaut true, le résultat de la requête sera
                               restreint aux décisions qualifiées comme présentant un intérêt
                               particulier (vaut false par défaut).

        Returns:
            Résultats de la recherche paginés (type searchPage)

        Raises:
            ValueError: Si les paramètres sont invalides
            Exception: Erreurs de requête API
        """
       
        if page_size > 50:
            raise ValueError("page_size ne peut pas dépasser 50")

        if operator not in ["or", "and", "exact"]:
            raise ValueError("operator doit être 'or', 'and' ou 'exact'")

        if sort not in ["score", "scorepub", "date"]:
            raise ValueError("sort doit être 'score', 'scorepub' ou 'date'")

        if order not in ["asc", "desc"]:
            raise ValueError("order doit être 'asc' ou 'desc'")

        # Construction de l'URL et des paramètres
        endpoint = f"{self.api_url}/search"

        # Paramètres de requête
        params: Dict[str, Any] = {
            "operator": operator,
            "sort": sort,
            "order": order,
            "page_size": page_size,
            "page": page,
            "resolve_references": "true" if resolve_references else "false",
            "particularInterest": "true" if particularInterest else "false",
        }

        # Ajouter les paramètres optionnels s'ils sont fournis
        if query:
            params["query"] = query
        if field:
            params["field"] = field
        if type:
            params["type"] = type
        if theme:
            params["theme"] = theme
        if chamber:
            params["chamber"] = chamber
        if formation:
            params["formation"] = formation
        if jurisdiction:
            params["jurisdiction"] = jurisdiction
        if location:
            params["location"] = location
        if publication:
            params["publication"] = publication
        if solution:
            params["solution"] = solution
        if date_start:
            params["date_start"] = date_start
        if date_end:
            params["date_end"] = date_end
        if withFileOfType:
            params["withFileOfType"] = withFileOfType

        try:
            response = requests.get(endpoint, headers=self._get_api_headers(), params=params)
            response.raise_for_status()
            json = response.json()
            return self.clean(json)

        except requests.exceptions.RequestException as e:
            raise Exception(f"Erreur lors de la recherche JudiLibre")
        except Exception as e:
            raise Exception(f"Erreur inattendue lors de la recherche")

    def consult(
        self,
        decision_id: str,
        resolve_references: bool = False,
        query: Optional[str] = None,
        operator: str = "and",
    ) -> Any:
        """
        Permet de récupérer le contenu intégral d'une décision.

        Connaissant l'identifiant unique d'une décision, ce point d'entrée permet d'en récupérer
        le contenu intégral (structuré, mais sans mise en forme), à savoir :

        📋 MÉTADONNÉES DE LA DÉCISION :
        - L'identifiant de sa juridiction
        - L'identifiant de sa chambre
        - Sa formation
        - Son numéro de pourvoi
        - Son ECLI (« European Case Law Identifier » : identifiant européen de la jurisprudence)
        - Son code NAC
        - Son niveau de publication
        - Son numéro de publication au bulletin
        - Sa solution
        - Sa date

        📄 CONTENU TEXTUEL :
        - Son texte intégral
        - Les délimitations des principales zones d'intérêt de son texte intégral :
          * Introduction
          * Exposé du litige
          * Moyens
          * Motivations
          * Dispositif
          * Moyens annexés

        🏷️ ÉLÉMENTS ANNEXES :
        - Ses éléments de titrage
        - Son sommaire
        - Ses documents associés (communiqué, note explicative, traduction, rapport,
          avis de l'avocat général, etc.)
        - Les textes appliqués
        - Les rapprochements de jurisprudence

        Certaines des informations ne sont retournées que sous forme de clé ou d'identifiant
        numérique (juridiction, chambre, niveau de publication, etc.). Il convient dès lors
        d'utiliser le point d'entrée GET /taxonomy pour en récupérer l'intitulé complet, ou
        d'effectuer la requête en utilisant le paramètre resolve_references=true.

        Args:
            decision_id: Identifiant de la décision à récupérer (obligatoire).
            resolve_references: Lorsque ce paramètre vaut true, le résultat de la requête
                               contiendra, pour chaque information retournée par défaut sous
                               forme de clé, l'intitulé complet de celle-ci (vaut false par défaut).
            query: Chaîne de caractères correspondant à la recherche. Ce paramètre est utilisé
                   pour surligner en retour, dans le texte intégral de la décision, les termes
                   correspondant avec la recherche initiale (ces termes étant délimitées par
                   des balises <em>).
            operator: Opérateur logique reliant les multiples termes que le paramètre query
                     peut contenir (or par défaut, and ou exact – dans ce dernier cas le
                     moteur recherchera exactement le contenu du paramètre query).

        Returns:
            Dict contenant la décision complète (type decisionFull)

        Raises:
            ValueError: Si decision_id est vide ou manquant, ou si operator est invalide
            Exception: Erreurs de requête API

        Examples:
            # Récupération basique avec identifiants numériques
            decision = api.decision("decision_12345")

            # Récupération avec intitulés complets
            decision = api.decision("decision_12345", resolve_references=True)

            # Récupération avec surlignage des termes de recherche
            decision = api.decision("decision_12345", query="responsabilité")

            # Récupération avec recherche exacte et références résolues
            decision = api.decision(
                "decision_12345",
                resolve_references=True,
                query="responsabilité médicale",
                operator="exact"
            )
        """
        if not decision_id or not decision_id.strip():
            raise ValueError(
                "L'identifiant de la décision est obligatoire et ne peut pas être vide"
            )

        if operator not in ["or", "and", "exact"]:
            raise ValueError("operator doit être 'or', 'and' ou 'exact'")

        endpoint = f"{self.api_url}/decision"
        params = {
            "id": decision_id,
            "resolve_references": "true" if resolve_references else "false",
        }

        # Ajouter les paramètres optionnels de recherche
        if query:
            params["query"] = query
            params["operator"] = operator

        try:
            response = requests.get(endpoint, headers=self._get_api_headers(), params=params)
            response.raise_for_status()
            json = response.json()
            return self.clean(json)

        except requests.exceptions.RequestException as e:
            raise Exception(f"Erreur lors de la récupération de la décision '{decision_id}'")
        except Exception as e:
            raise Exception(f"Erreur inattendue lors de la récupération de la décision")


    def taxonomy(
        self,
        taxonomy_id: Optional[str] = None,
        key: Optional[str] = None,
        value: Optional[str] = None,
        context_value: Optional[str] = None,
    ) -> Any:
        """
        Récupère les listes des termes employés par le processus de recherche

        Cette méthode permet de récupérer les taxonomies (couples clé/valeur) constituant
        les différents critères et filtres pris en compte par la recherche, notamment :

        📋 TAXONOMIES DISPONIBLES :
        - type : Types de décision (arret, qpc, ordonnance, saisie, etc.)
        - jurisdiction : Juridictions (cc, ca, tj, ta, caa, ce, tc, crc, etc.)
        - chamber : Chambres de la Cour de cassation
                   ⚠️ Clés à utiliser: pl, mi, civ1, civ2, civ3, comm, soc, cr,
                                      creun, ordo, allciv, other
                   Exemples: "civ1" (Première chambre civile), "soc" (Chambre sociale)
        - formation : Formations des juridictions
        - publication : Niveaux de publication (b, r, l, c, etc.)
        - theme : Matières (nomenclature Cour de cassation)
        - solution : Solutions (annulation, cassation, rejet, etc.)
        - field : Champs et zones. de contenu (expose, moyens, motivations, dispositif, etc.)
        - zones : Zones de contenu des décisions
        - location : Codes des sièges de juridiction (avec context_value)
        - filetype : Types de documents associés

        🎯 MODES D'UTILISATION :

        1. **Liste complète d'une taxonomie** :
           `taxonomy("jurisdiction")` → Toutes les juridictions disponibles

        2. **Récupération d'un intitulé par clé** :
           `taxonomy("jurisdiction", key="cc")` → "Cour de cassation"

        3. **Récupération d'une clé par intitulé** :
           `taxonomy("jurisdiction", value="cour de cassation")` → "cc"

        4. **Liste contextuelle** :
           `taxonomy("chamber", context_value="cc")` → Chambres de la Cour de cassation

        Args:
            taxonomy_id: Identifiant de la taxonomie à interroger. Si omis, retourne
                        la liste de toutes les taxonomies disponibles.
                        Valeurs: type, jurisdiction, chamber, formation, publication,
                        theme, solution, field, zones, location, filetype
            key: Clé du terme dont on veut récupérer l'intitulé complet
                 (nécessite taxonomy_id)
            value: Intitulé complet dont on veut récupérer la clé
                   (nécessite taxonomy_id)
            context_value: Valeur de contexte pour certaines taxonomies.
                          - Pour chamber: 'cc' (Cour de cassation) ou 'ca' (Cours d'appel)
                          - Pour location: 'ca' (cours d'appel) ou 'tj' (tribunaux judiciaires)
                          - Défaut: 'cc' si omis

        Returns:
            Données de taxonomie (le format varie selon les paramètres) :
            - Si aucun paramètre : List[Dict[str, str]] avec format enrichi
              [{"key": "type", "description": "Types de décision ..."}, ...]
            - Si taxonomy_id seul : liste complète des termes de cette taxonomie
              (format original de l'API)
            - Si key fourni : Dict avec {"key": "cc", "value": "Cour de cassation"}
            - Si value fourni : Dict avec {"key": "cc", "value": "Cour de cassation"}

        Raises:
            ValueError: Si les paramètres sont incompatibles
            Exception: Erreurs de requête API

        Examples:
            # Lister toutes les taxonomies disponibles (FORMAT ENRICHI)
            all_taxonomies = api.taxonomy()
            # → [
            #     {"key": "type", "description": "Types de décision (arrêt, ordonnance, QPC, etc.)"},
            #     {"key": "jurisdiction", "description": "Juridictions (Cour de cassation, ...)"},
            #     {"key": "chamber", "description": "Chambres de la Cour de cassation ..."},
            #     ...
            # ]

            # Obtenir toutes les juridictions
            jurisdictions = api.taxonomy("jurisdiction")
            # → [{"key": "cc", "value": "Cour de cassation"}, ...]

            # Obtenir l'intitulé d'une juridiction par sa clé
            cc_name = api.taxonomy("jurisdiction", key="cc")
            # → {"key": "cc", "value": "Cour de cassation"}

            # Obtenir la clé d'une juridiction par son intitulé
            cc_key = api.taxonomy("jurisdiction", value="cour de cassation")
            # → {"key": "cc", "value": "Cour de cassation"}

            # Obtenir les chambres de la Cour de cassation
            cc_chambers = api.taxonomy("chamber", context_value="cc")
            # → [{"key": "civile", "value": "Chambre civile"}, ...]

            # Obtenir les codes des tribunaux judiciaires
            tj_locations = api.taxonomy("location", context_value="tj")
            # → [{"key": "tj06088", "value": "Tribunal judiciaire de Nice"}, ...]

            # Obtenir tous les types de décisions
            decision_types = api.taxonomy("type")
            # → [{"key": "arret", "value": "Arrêt"}, ...]

        Note:
            Cette méthode est essentielle pour automatiser la constitution des formulaires
            de recherche et pour enrichir les résultats retournés avec les intitulés complets.
        """
        endpoint = f"{self.api_url}/taxonomy"
        params = {}

        # Validation des paramètres
        if key and value:
            raise ValueError("Les paramètres 'key' et 'value' sont mutuellement exclusifs")

        if (key or value) and not taxonomy_id:
            raise ValueError("Le paramètre 'taxonomy_id' est requis avec 'key' ou 'value'")

        # Construction des paramètres
        if taxonomy_id:
            params["id"] = taxonomy_id

        if key:
            params["key"] = key

        if value:
            params["value"] = value

        if context_value:
            params["context_value"] = context_value

        if not params:
            # Aucun paramètre fourni : laisser l'appel API retourner la liste complète des taxonomies
            TAXONOMY_DESCRIPTIONS = {
                "type": "Types de décision (arrêt, ordonnance, QPC, etc.)",
                "jurisdiction": "Juridictions (Cour de cassation, cours d'appel, tribunaux, etc.)",
                "chamber": "Chambres de la Cour de cassation (civile, sociale, criminelle, etc.)",
                "formation": "Formations des juridictions",
                "publication": "Niveaux de publication (bulletin, rapport, lettre, etc.)",
                "theme": "Matières juridiques (nomenclature Cour de cassation)",
                "solution": "Types de solution (cassation, rejet, annulation, etc.)",
                "field": "Champs et zones de contenu (exposé, moyens, motivations, dispositif, etc.)",
                "zones": "Zones de contenu des décisions",
                "location": "Codes des sièges de juridiction (cours d'appel, tribunaux)",
                "filetype": "Types de documents associés (rapports, avis, communiqués, etc.)",
            }
            return TAXONOMY_DESCRIPTIONS

        try:
            response = requests.get(endpoint, headers=self._get_api_headers(), params=params)
            response.raise_for_status()
            json = response.json()
            # Un tableau est retourné si plusieurs décisions sont demandées, à défaut le réponse complète
            result = json.get("result", json)
            return result

        except requests.exceptions.RequestException as e:
            if taxonomy_id:
                raise Exception(
                    f"Erreur lors de la récupération de la taxonomie '{taxonomy_id}': {e}"
                )
            else:
                raise Exception(f"Erreur lors de la récupération des taxonomies: {e}")


    def clean(self, x, depth=0, max_depth=5):
            """
            Nettoie un dictionnaire ou une liste en ne conservant que les clés autorisées et en supprimant les valeurs None ou vides.

            Args:
                x (dict or list): Dictionnaire ou liste à nettoyer.

            Returns:
                dict or list: Structure nettoyée avec uniquement les clés autorisées.
            """
            # Liste des clés à conserver
            allowed_keys = {
                "text" , "id", "jurisdiction", "chamber", "formation", "type", "theme",
                "publication","decision_date","solution","jurisdiction","score"
            }

            # Arrêter la descente si on a atteint la profondeur maximale
            if depth >= max_depth:
                return None

            if isinstance(x, dict):
                cleaned = {}
                for k, v in x.items():
                    if v:  # Ignorer les valeurs vides
                        if k in allowed_keys and not isinstance(v, (dict, list)):
                            # Clé autorisée : conserver la valeur
                            cleaned[k] = v
                        elif isinstance(v, (dict, list)):
                            # Valeur est dict/list : descendre dans la hiérarchie
                            cleaned_value = self.clean(v, depth + 1, max_depth)
                            if cleaned_value:  # Ne garder que si le résultat n'est pas vide
                                cleaned[k] = cleaned_value
                return cleaned if cleaned else None

            if isinstance(x, list):
                # Si la liste contient uniquement des chaînes de caractères, la garder intacte
                if x and all(isinstance(item, str) for item in x):
                    return x
                # Sinon, traiter récursivement
                l = [cleaned_v for v in x if v and (cleaned_v := self.clean(v, depth + 1, max_depth)) is not None]
                return l if l else None

            return x
        
