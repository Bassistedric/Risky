# RISKY V1 — Cahier des charges fonctionnel

## 1. Objet du projet
RISKY est un environnement de pilotage QHSE centré sur le SIPP et le processus 4 — Sécurité. L’objectif est de remplacer progressivement une organisation fondée sur de nombreux fichiers Excel, Google Sheets, exports Phronesys et documents indépendants par un système structuré dans lequel la donnée métier est enregistrée une seule fois, les modules utilisent les mêmes données, les documents sont générés à partir de la base, les données peuvent être importées depuis les outils existants et les documents officiels sont publiés dans SharePoint.

RISKY ne remplace pas le futur outil SMI. RISKY produit les données du processus 4 et sa contribution à la revue de direction ; le futur outil SMI agrégera les données de tous les processus.

## 2. Principes d’architecture non négociables
- Séparer RISKY Core, la configuration d’environnement et les données d’entreprise.
- Ne coder aucune donnée propre à une entreprise en dur.
- La base RISKY contient la vérité métier ; les PDF/Word/Excel sont des sorties générées.
- Archiver plutôt que supprimer physiquement.
- Conserver la provenance de toute donnée importée.
- Garder les connecteurs remplaçables.
- Permettre l’export des données dans des formats ouverts.

## 3. Structure organisationnelle
Structure hiérarchique et extensible, par exemple : VMA → VMA Sud → HVAC / REF / ELEC, avec possibilité d’ajouter VMA Nord, BE Maintenance, etc. Chaque entité possède un identifiant, un nom, un code, un type, un parent et un statut actif/inactif.

## 4. Personnel
Champs principaux : ID interne, matricule, nom, prénom, e-mail, fonction, catégorie, entité, responsable éventuel, statut actif/inactif/archivé. Les champs peuvent être facultatifs.

Catégories :
- CAT1 — Ligne hiérarchique / management opérationnel ;
- CAT2 — Employés ;
- CAT3 — Chefs d’équipe ;
- CAT4 — Ouvriers.

La catégorie décrit la population. Les obligations ILT/TBM sont configurées séparément par catégorie, fonction, individu et période.

## 5. Compétences, formations et habilitations
RISKY contient un catalogue de compétences, des exigences par fonction/catégorie/métier, des sessions de formation, des participants, des résultats et des attestations. Une formation validée peut alimenter automatiquement une compétence individuelle.

L’habilitation est construite à partir des compétences validées. Elle peut contenir tâches autorisées/interdites, rôle formateur, périmètre, limitations, validité et signataire. Pour BA4/BA5 : niveau, domaine de tension, installations, travaux, limitations, conditions particulières et compléments réglementaires.

## 6. Accidents / incidents
Chaque fait est encodé dans un dossier unique : situation dangereuse, incident, premier soin, accident sans arrêt, accident avec travail adapté, accident avec arrêt, accident grave, accident grave sans arrêt, chemin du travail, matériel, environnement, etc.

Le dossier intègre codification, HEEPO, analyse approfondie, photos, causes, mesures, actions et, si nécessaire, rapport circonstancié. Niveaux d’escalade : 0 simple enregistrement ; 1 HEEPO ; 2 analyse approfondie ; 3 rapport circonstancié.

Trois sorties documentaires : rapport événement, rapport d’analyse d’accident, rapport circonstancié.

## 7. Actions et plans
Une action n’existe qu’une seule fois dans la base. Workflow : À réaliser → En cours → Réalisée → À valider → Clôturée. Origines possibles : accident, analyse, ILT, STOP, CPPT, PAA, environnement, KPI, sécurité équipement, autre.

Le plan global de prévention est pluriannuel et alimente le plan annuel SIPP, lequel peut aussi contenir des actions annuelles ajoutées. Le plan CPPT utilise la même structure d’action et pourra alimenter le futur SMI sans duplication.

## 8. Analyses de risques
RISKY contient un registre central des analyses : référence, type, titre, métier, version, date, auteur, statut, date de révision, lien document, système externe éventuel.

Familles :
- Standard : Kinney, Ishikawa, HAZOP, 5 Why, AMDEC, etc. ;
- Ergonomie : KIM, NIOSH, RULA, REBA, etc. ;
- Métier / Spécifique : RePSS, MOADR, etc.

Les anciennes analyses peuvent rester sur SharePoint et être référencées par lien. RePSS reste un outil externe relié à Risky ; MOADR peut être externe ou généré dans Risky.

## 9. ILT / Phronesys
Phronesys reste l’outil terrain. RISKY importe les exports, suit les obligations nominatives, gère les exemptions, calcule les statistiques, liste les manquants, prépare les rappels et alimente le rapport SIPP.

## 10. TBM / FMRA / STOP / premiers soins
Le Google Sheet actuel reste une source transitoire. RISKY récupère les données TBM, FMRA, STOP et premiers soins, puis les rattache aux personnes, métiers, chantiers et périodes. Une entrée premiers soins peut être transformée en événement accident/incident.

## 11. Obligations périodiques et relances
Le même moteur gère ILT et TBM. Pour chaque personne et période : attendu, réalisé, exempté, manquant, statut. Le rapport annuel doit fournir par personne : attendu, réalisé, exempté, non réalisé, taux et éventuellement rappels.

## 12. Planning / affectations / app QHSE
Le planning Excel est une source d’import. RISKY importe, reconnaît personnes/équipes/chantiers, détecte les anomalies, génère les affectations et alimente le format attendu par l’app QHSE. À terme, Google Sheets devient un pont transitoire remplacé par API.

## 13. Sécurité équipement
Le module ne gère pas le parc. Il gère la documentation sécurité : trois feux verts, fiches machine, fiches de contrôle et documents associés. Un dossier équipement minimal contient désignation, type, marque, modèle, numéro de série et référence éventuelle.

## 14. Environnement
Module préparé pour une future ISO 14001 : aspects & impacts, exigences/conformité, indicateurs, événements environnementaux, objectifs. La méthode d’évaluation reste paramétrable.

## 15. Processus 4 / SMI
RISKY ne gère pas tout le SMI. Il gère uniquement le processus 4 — Sécurité : KPI, tableau des tâches du processus, objectifs, actions et génération de la contribution à la revue de direction. Le futur SMI récupérera cette contribution.

## 16. Reporting SIPP
Rapport exécutif d’une page, avec périodes semaine, mois, trimestre, YTD, année. Le rapport hebdomadaire contient accidents YTD, accidents avec arrêt, TF, TG, éventuellement TGG, événements récents, ILT, TBM, listes nominatives des manquants et points d’attention SIPP. Une annexe détaillée peut être générée en complément.

## 17. Documents et SharePoint
SharePoint est le stockage documentaire officiel. RISKY génère, référence et conserve les métadonnées ainsi que le lien SharePoint. RISKY ne recrée pas une GED complète.

## 18. Administration
Blocs : Organisation ; Référentiels ; Objectifs & règles ; Modèles documentaires ; Connexions & imports ; Système. Les personnes, accidents, actions et analyses restent dans leurs modules métier.

## 19. Suppression fonctionnelle
Le module générique “Formulaires” est supprimé. Chaque formulaire appartient à son module métier.

## 20. Architecture technique de développement
Développement local : Python, FastAPI, SQLAlchemy, SQLite, frontend web. Cible ultérieure : backend API, base PostgreSQL ou SQL Server selon environnement approuvé, authentification entreprise, SharePoint, multi-utilisateur.

## 21. Premier vertical slice
Premier flux complet : Personne → Compétence → Formation → Validation → Habilitation → Génération de document → Référence documentaire.

## 22. Étapes suivantes
1. Créer le modèle de données V1.
2. Générer les premières tables SQLAlchemy.
3. Créer la base SQLite.
4. Créer l’API FastAPI.
5. Développer le premier vertical slice.
