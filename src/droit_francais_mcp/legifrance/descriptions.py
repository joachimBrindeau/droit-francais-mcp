"""Descriptions détaillées (référence) des fonds Légifrance et des types de champs.

Ces dictionnaires ne sont pas utilisés par le builder de requêtes ; ils sont
exposés pour les consommateurs externes (scripts, documentation générée)
qui veulent énumérer les valeurs valides avec leur explication détaillée.
"""

from __future__ import annotations

from typing import Any, Dict

# Source du contenu : champs des types de recherche supportés.
TYPE_CHAMP_DESCRIPTIONS: Dict[str, Dict[str, Any]] = {
    "ALL": {
        "nom": "Tous les champs",
        "description": "Recherche dans l'ensemble des champs disponibles du document",
        "usage": "Recherche générale quand on ne sait pas dans quel champ chercher",
        "exemple": 'Rechercher "mariage" dans tout le document',
    },
    "TITLE": {
        "nom": "Titre",
        "description": "Titre officiel du texte juridique",
        "usage": "Rechercher des textes par leur intitulé exact ou partiel",
        "exemple": 'Rechercher "Code civil" ou "loi sur le mariage"',
    },
    "TABLE": {
        "nom": "Table des matières",
        "description": "Structure et organisation du texte (parties, livres, titres, chapitres)",
        "usage": "Naviguer dans l'organisation du texte, chercher des sections",
        "exemple": 'Rechercher "Livre premier" ou "Titre II"',
    },
    "NOR": {
        "nom": "Numéro NOR",
        "description": "Numéro d'ordre réglementaire unique attribué aux textes",
        "usage": "Recherche précise d'un texte par son identifiant officiel",
        "exemple": "JUSC1732516D pour un décret spécifique",
    },
    "NUM": {
        "nom": "Numéro du texte",
        "description": "Numéro officiel du texte (loi n°, décret n°, etc.)",
        "usage": "Rechercher un texte par son numéro de publication",
        "exemple": "Loi n°2018-287 ou Décret n°2019-123",
    },
    "ADVANCED_TEXTE_ID": {
        "nom": "Identifiant technique",
        "description": "Identifiant technique interne du système Légifrance",
        "usage": "Recherche technique par ID système (usage avancé)",
        "exemple": "LEGITEXT000006070721",
    },
    "NUM_DELIB": {
        "nom": "Numéro de délibération",
        "description": "Numéro de délibération pour les textes délibératifs",
        "usage": "Rechercher des délibérations spécifiques (CNIL, collectivités)",
        "exemple": "Délibération n°2019-001",
    },
    "NUM_DEC": {
        "nom": "Numéro de décision",
        "description": "Numéro de décision pour la jurisprudence",
        "usage": "Rechercher des décisions de justice par leur numéro",
        "exemple": "Arrêt n°19-12345",
    },
    "NUM_ARTICLE": {
        "nom": "Numéro d'article",
        "description": "Numéro ou référence d'un article spécifique",
        "usage": "Rechercher des articles précis dans les codes ou lois",
        "exemple": "Article 1134 ou Article L123-1",
    },
    "ARTICLE": {
        "nom": "Contenu des articles",
        "description": "Texte intégral du contenu des articles",
        "usage": "Rechercher dans le contenu même des articles",
        "exemple": 'Rechercher "responsabilité" dans les articles',
    },
    "MINISTERE": {
        "nom": "Ministère",
        "description": "Ministère ou autorité émettrice du texte",
        "usage": "Filtrer les textes par ministère d'origine",
        "exemple": "Ministère de la Justice, Ministère de l'Intérieur",
    },
    "VISA": {
        "nom": "Visas",
        "description": "Références aux textes sur lesquels s'appuie la décision",
        "usage": "Rechercher les fondements juridiques cités",
        "exemple": "Vu le Code civil, vu la loi du...",
    },
    "NOTICE": {
        "nom": "Notice",
        "description": "Notice explicative ou informative du texte",
        "usage": "Rechercher des explications ou contexte du texte",
        "exemple": "Informations sur l'application du texte",
    },
    "VISA_NOTICE": {
        "nom": "Visas et notice",
        "description": "Recherche combinée dans les visas et la notice",
        "usage": "Rechercher à la fois dans les références et explications",
        "exemple": "Contexte juridique complet du texte",
    },
    "TRAVAUX_PREP": {
        "nom": "Travaux préparatoires",
        "description": "Documents préparatoires (rapports, débats parlementaires)",
        "usage": "Comprendre l'intention du législateur",
        "exemple": "Rapport de la commission, exposé des motifs",
    },
    "SIGNATURE": {
        "nom": "Signataires",
        "description": "Autorités ayant signé ou approuvé le texte",
        "usage": "Rechercher par autorité signataire",
        "exemple": "Ministre, Président de la République",
    },
    "NOTA": {
        "nom": "Nota",
        "description": "Notes explicatives ou d'application du texte",
        "usage": "Trouver des précisions sur l'application",
        "exemple": "Conditions d'entrée en vigueur, exceptions",
    },
    "NUM_AFFAIRE": {
        "nom": "Numéro d'affaire",
        "description": "Numéro d'affaire judiciaire ou administrative",
        "usage": "Rechercher une affaire judiciaire précise",
        "exemple": "19-12.345 pour une affaire en cours d'appel",
    },
    "ABSTRATS": {
        "nom": "Abstracts",
        "description": "Résumés courts du contenu principal",
        "usage": "Recherche dans les résumés pour avoir un aperçu",
        "exemple": "Mots-clés du résumé exécutif",
    },
    "RESUMES": {
        "nom": "Résumés",
        "description": "Résumés détaillés du texte",
        "usage": "Rechercher dans les synthèses du contenu",
        "exemple": "Points principaux du texte",
    },
    "TEXTE": {
        "nom": "Texte intégral",
        "description": "Contenu textuel complet du document",
        "usage": "Recherche exhaustive dans tout le contenu",
        "exemple": "Rechercher n'importe quel terme dans le texte",
    },
    "ECLI": {
        "nom": "Identifiant ECLI",
        "description": "European Case Law Identifier - Identifiant européen de jurisprudence",
        "usage": "Recherche de jurisprudence avec référence européenne",
        "exemple": "ECLI:FR:CCASS:2019:C100123",
    },
    "NUM_LOI_DEF": {
        "nom": "Numéro de loi déférée",
        "description": "Numéro de la loi contestée devant le Conseil constitutionnel",
        "usage": "Rechercher les décisions constitutionnelles par loi contestée",
        "exemple": "Loi n°2018-123 déférée au Conseil constitutionnel",
    },
    "TYPE_DECISION": {
        "nom": "Type de décision",
        "description": "Catégorie de la décision de justice",
        "usage": "Filtrer par type de décision judiciaire",
        "exemple": "Arrêt, ordonnance, jugement",
    },
    "NUMERO_INTERNE": {
        "nom": "Numéro interne",
        "description": "Numéro de référence interne à l'administration",
        "usage": "Recherche par référence administrative interne",
        "exemple": "Numéro de dossier administratif",
    },
    "REF_PUBLI": {
        "nom": "Référence de publication",
        "description": "Référence de publication dans les bulletins officiels",
        "usage": "Rechercher par référence de publication officielle",
        "exemple": "JORF n°123 du 15/06/2019",
    },
    "RESUME_CIRC": {
        "nom": "Résumé de circulaire",
        "description": "Résumé spécifique aux circulaires ministérielles",
        "usage": "Rechercher dans les résumés de circulaires",
        "exemple": "Objectifs et portée de la circulaire",
    },
    "TEXTE_REF": {
        "nom": "Texte de référence",
        "description": "Références aux textes cités ou modifiés",
        "usage": "Trouver les textes qui citent ou modifient d'autres textes",
        "exemple": "Références aux codes modifiés",
    },
    "TITRE_LOI_DEF": {
        "nom": "Titre de loi déférée",
        "description": "Titre de la loi contestée devant le Conseil constitutionnel",
        "usage": "Rechercher les décisions constitutionnelles par titre de loi",
        "exemple": "Loi de finances pour 2019",
    },
    "RAISON_SOCIALE": {
        "nom": "Raison sociale",
        "description": "Nom de l'entreprise pour les accords d'entreprise",
        "usage": "Rechercher les accords par nom d'entreprise",
        "exemple": "SNCF, Renault, Total",
    },
    "MOTS_CLES": {
        "nom": "Mots-clés",
        "description": "Mots-clés thématiques associés au texte",
        "usage": "Rechercher par thématique ou domaine juridique",
        "exemple": "Droit du travail, fiscalité, urbanisme",
    },
    "IDCC": {
        "nom": "IDCC",
        "description": "Identifiant de Convention Collective",
        "usage": "Rechercher une convention collective par son numéro IDCC",
        "exemple": "IDCC 1596 pour la métallurgie",
    },
}

# Valeurs valides pour le fonds (descriptions: voir FONDS_DESCRIPTIONS)


# Source du contenu : descriptions des fonds Légifrance.
FONDS_DESCRIPTIONS: Dict[str, Dict[str, Any]] = {
    "ALL": {
        "nom": "Tous les fonds",
        "description": "Recherche transversale dans tous les fonds disponibles",
        "contenu": "Ensemble de la base juridique Légifrance",
    },
    "JORF": {
        "nom": "Journal Officiel de la République Française",
        "description": "Textes publiés au Journal Officiel : lois, décrets, arrêtés, avis, annonces...",
        "contenu": "Publications officielles, textes réglementaires, nominations, marchés publics",
    },
    "CNIL": {
        "nom": "Commission Nationale de l'Informatique et des Libertés",
        "description": "Décisions, délibérations et avis de la CNIL en matière de protection des données",
        "contenu": "Autorisations, sanctions, recommandations, délibérations",
    },
    "CETAT": {
        "nom": "Conseil d'État",
        "description": "Jurisprudence administrative du Conseil d'État et des juridictions administratives",
        "contenu": "Arrêts, ordonnances, avis du Conseil d'État et des cours administratives d'appel",
    },
    "JURI": {
        "nom": "Jurisprudence judiciaire",
        "description": "Décisions des juridictions de l'ordre judiciaire",
        "contenu": "Arrêts de la Cour de cassation, cours d'appel, tribunaux",
    },
    "JUFI": {
        "nom": "Jurisprudence financière",
        "description": "Décisions des juridictions financières (Cour des comptes, CRC)",
        "contenu": "Arrêts de la Cour des comptes et des chambres régionales des comptes",
    },
    "CONSTIT": {
        "nom": "Conseil Constitutionnel",
        "description": "Décisions du Conseil constitutionnel",
        "contenu": "Décisions sur la constitutionnalité des lois, QPC, contrôle des élections",
    },
    "KALI": {
        "nom": "Conventions collectives",
        "description": "Conventions et accords collectifs de travail étendus",
        "contenu": "Conventions collectives nationales, accords de branche, avenants",
    },
    "CODE_DATE": {
        "nom": "Codes consolidés (par date)",
        "description": "Codes en vigueur recherchés par date de version",
        "contenu": "Tous les codes français consolidés avec historique des versions",
    },
    "CODE_ETAT": {
        "nom": "Codes consolidés (par état juridique)",
        "description": "Codes en vigueur recherchés par état juridique",
        "contenu": "Codes français avec statut juridique (en vigueur, abrogé, etc.)",
    },
    "LODA_DATE": {
        "nom": "LODA (par date)",
        "description": "Lois, Ordonnances, Décrets, Arrêtés recherchés par date de version",
        "contenu": "Textes législatifs et réglementaires consolidés avec historique",
    },
    "LODA_ETAT": {
        "nom": "LODA (par état juridique)",
        "description": "Lois, Ordonnances, Décrets, Arrêtés recherchés par état juridique",
        "contenu": "Textes législatifs et réglementaires avec statut juridique",
    },
    "CIRC": {
        "nom": "Circulaires et instructions",
        "description": "Circulaires et instructions ministérielles",
        "contenu": "Textes d'application, instructions, notes de service",
    },
    "ACCO": {
        "nom": "Accords d'entreprise",
        "description": "Accords collectifs d'entreprise déposés",
        "contenu": "Accords d'entreprise, protocoles d'accord, avenants d'entreprise",
    },
}
