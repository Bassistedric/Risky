# RISKY — CONTEXTE PROJET / PASSATION

Dernière mise à jour : 2026-09-10

Ce fichier sert de référence pour reprendre le projet RISKY dans une nouvelle conversation sans devoir réexpliquer l’historique.

## 1. Objectif du projet
RISKY est une application QHSE interne pensée d’abord pour VMA Sud, avec possibilité d’extension ultérieure à d’autres entités.

Architecture visée :
- VMA
  - VMA Sud
    - HVAC
    - REF
    - ELEC
  - extension possible : VMA Nord / BE Maintenance

Objectifs :
- centraliser les outils QHSE ;
- multi-utilisateurs ;
- rôles + périmètres organisationnels ;
- transférable à d’autres entités ;
- interface professionnelle et cohérente.

## 2. Environnement local
Dossier projet :
`C:\Users\Cedric\Documents\RISKY-DEV`

Frontend :
`C:\Users\Cedric\Documents\RISKY-DEV\frontend`

Backend :
`C:\Users\Cedric\Documents\RISKY-DEV\backend`

Stack :
- FastAPI + SQLAlchemy + SQLite
- React + TypeScript + Vite
- DB : `sqlite:///./database/risky.db`

Backend :
```powershell
cd C:\Users\Cedric\Documents\RISKY-DEV
python -m uvicorn backend.main:app --reload
```

Frontend :
```powershell
cd C:\Users\Cedric\Documents\RISKY-DEV\frontend
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
npm run dev
```

Adresses :
- frontend : `http://localhost:5173`
- backend : `http://127.0.0.1:8000`
- Swagger : `http://127.0.0.1:8000/docs`

## 3. Règles de travail
Toujours :
- préciser le chemin exact du fichier à modifier ;
- conserver les commentaires séparateurs de sections dans les gros fichiers ;
- modifications progressives ;
- ne pas réécrire ce qui existe déjà sans vérifier ;
- éviter les tests inutiles ;
- penser à Ctrl+S en cas de comportement incohérent.

Séparateurs :
```ts
/* ========================================================
   NOM DE SECTION
   ======================================================== */
```

```py
# ============================================================
# NOM DE SECTION
# ============================================================
```

## 4. Frontend principal
Fichier :
`frontend/src/App.tsx`

Type principal :
```ts
type MainView =
  | 'home'
  | 'risk-analysis'
  | 'accidents'
  | 'action-plans'
  | 'personnel'
  | 'competencies'
  | 'equipment'
  | 'field'
  | 'quality'
```

État initial :
```ts
const [mainView, setMainView] =
  useState<MainView>('home')
```

Après authentification : affichage de `HomePage`.

Pages importantes :
- `frontend/src/pages/LoginPage.tsx`
- `frontend/src/pages/LoginPage.css`
- `frontend/src/pages/HomePage.tsx`
- `frontend/src/pages/HomePage.css`
- `frontend/src/pages/AccidentRegisterPage.tsx`
- `frontend/src/pages/AccidentCreatePage.tsx`
- `frontend/src/pages/AccidentDossierPage.tsx`
- `frontend/src/pages/CauseTreePage.tsx`

## 5. Authentification et sessions
Modèles ajoutés dans `backend/models.py` :
- `AccessRole`
- `UserAccessGrant`
- `UserSession`

Rôles :
- ADMIN
- SIPP
- QHSE
- MANAGER
- VIEWER

Utilisateur de démonstration courant :
- Person id 1
- initiales `Cco`
- nom base `Jean DEMO`
- rôle ADMIN
- scope global

Service :
`backend/services/session.py`

Durée session : 30 jours.

Header :
`X-Session-Token`

Token frontend :
`risky_session_token` dans `sessionStorage`.

Routes :
- `POST /session/login`
- `GET /session/me`
- `POST /session/logout`

CORS dans `backend/main.py` doit autoriser au minimum :
- `http://localhost:5173`
- `http://127.0.0.1:5173`

## 6. Login — validé
Fichiers :
- `frontend/src/pages/LoginPage.tsx`
- `frontend/src/pages/LoginPage.css`

Design :
- fond bleu nuit ;
- carte centrale sombre ;
- logo RISKY ;
- champ Initiales ;
- bouton bleu ;
- bas gauche : Gestion QHSE | Version 1.0 ;
- bas droite : petit logo By Cco.

Logo :
`/images/winston_bycco_logo.png`

Placeholder :
`Ex : Jean Démo → JED`

## 7. HomePage
Après login :
`mainView = 'home'`

Cartes :
- Analyse de risques
- Accidents & incidents
- Plans d'action
- Personnel
- Compétences & habilitations
- Sécurité équipements
- Terrain
- Qualité & SMI

## 8. Sidebar — DESIGN FIGÉ
Fichiers :
- `frontend/src/App.tsx`
- `frontend/src/App.css`

Ne plus modifier l’esthétique générale sans demande explicite.

Décisions validées :
- fond bleu nuit sombre ;
- tout aligné à gauche ;
- titres de sections `VUE GÉNÉRALE / SÉCURITÉ / GESTION / SYSTÈME` en bleu-gris ;
- texte des items en vert ;
- icônes en vert ;
- item actif : fond bleu foncé discret + trait bleu à gauche ;
- flèche de réduction orange, à cheval sur la limite droite ;
- scrollbar verticale visible et discrète ;
- logo By Cco petit, à droite du branding Risky.

Couleurs actuelles :
- titres sidebar : `#7f98ae`
- items/icônes : `#43d98e`
- hover : `#55e99c`
- fond actif : `#173653`
- trait actif : `#478bc9`
- flèche : `#e47c18`
- fond sidebar : `#081f37`
- scrollbar : `#55748f`

Flèche :
```css
top: 74px;
right: -15px;
width: 30px;
height: 38px;
```

## 9. Topbar — DESIGN FIGÉ
- fond blanc ;
- titre sombre ;
- texte secondaire gris ;
- filtres organisation/métier à droite ;
- `VUE GÉNÉRALE` dans la topbar reste BLEU.

Couleur topbar eyebrow :
`#3479c8`

## 10. Module Accident
État :
```ts
const [accidentView, setAccidentView] =
  useState<
    | 'register'
    | 'create'
    | 'dossier'
    | 'cause-tree'
  >('register')
```

Flux :
`register → create / dossier → cause-tree`

Ne pas supprimer ou recréer Dossier / Arbre des causes : ils existent.

## 11. Event backend
Champs ajoutés :
- `person_category`
- `victim_last_name`
- `victim_first_name`
- `project_manager`
- `site_supervisor`
- `material_damage`
- `material_damage_details`
- `material_damage_cost`
- `environmental_damage`
- `environmental_damage_type`
- `environmental_damage_details`
- `environmental_quantity`
- `environmental_unit`

Types :
- ACCIDENT
- INCIDENT
- NEAR_MISS
- MATERIAL
- ENVIRONMENT

Migration manuelle :
`migrate_events.py`

Pas encore Alembic.

## 12. Bug historique important
Dans `backend/models.py`, du code de `backend/services/session.py` avait été collé accidentellement dans `class Event`, causant :
`Mapper[Event(events)] has no property 'classification'`

Bug corrigé. Ne pas réintroduire cette structure.

## 13. Rôles et périmètres
Séparer :
1. identité ;
2. rôle ;
3. périmètre organisationnel.

Exemples :
- ADMIN global → toutes les entités ;
- SIPP VMA Sud → VMA Sud + enfants ;
- futur VMA Nord → VMA Nord uniquement.

`Organization` possède :
- id
- code
- name
- entity_type
- parent_id
- active

## 14. Profil utilisateur — prochaine étape logique
La sidebar contient encore temporairement un profil codé en dur.

Cible :
```text
Cco
ADMIN · Toutes les entités
```

À prévoir :
- vraies données `/session/me` ;
- menu profil ;
- changer de périmètre ;
- logout frontend.

## 15. UI générale
Palette fonctionnelle :
- gris = retour / secondaire ;
- bleu = action principale ;
- vert = positif / navigation ;
- rouge = danger.

Sections :
- fond général clair ;
- cartes blanches ;
- zones légèrement teintées type `#f8fafc`.

## 16. Modules futurs
Analyse de risques :
- Kinney
- RePSS
- MOADR
- méthodes standard
- méthodes ergonomiques

Terrain :
- FMRA
- STOP
- Toolbox
- ILT

Accident :
- registre
- dossier
- arbre des causes
- Heepo
- rapport circonstancié
- TF/TG/TGG
- rapports

Plans d’actions :
- Global
- Annuel
- CPPT
- 9001
- SIPP annuel

Personnel :
- identité
- catégories
- fiche 360

Compétences :
- BA4/BA5
- formations
- attestations

Équipements :
- trois feux verts
- fiches machines
- contrôles

Qualité/SMI :
- indicateurs
- revue de direction
- audits
- NC
- SWOT
- futur ISO 14001

## 17. Intégrations prévues
Google Sheets :
- LMRA_data_base
- premier_soin
- stop
- tbm
- TBM_UNIQUE
- TBM_PARTICIPANTS
- equipes-tbm

Phronesys :
- Ex_phro
- Ex_phro_NOK
- suivi ILT LLN/JUM

Documents :
- cible SharePoint avec classement ISO.

## 18. Règle de reprise pour une nouvelle conversation
Quand ce fichier est fourni :
1. le lire comme contexte de référence ;
2. ne pas redemander l’historique décrit ici ;
3. conserver les décisions UI validées ;
4. demander seulement les fichiers actuels nécessaires ;
5. ne pas supposer que le code local n’a pas évolué ;
6. toujours préciser le chemin exact ;
7. préférer les modifications ciblées ;
8. conserver les séparateurs de sections.

## 19. État de référence — 10/09/2026
Fonctionnel :
- backend FastAPI ;
- frontend Vite ;
- login ;
- session persistante ;
- rôles/grants ;
- CORS ;
- HomePage ;
- navigation principale ;
- module accidents ;
- sidebar restaurée et design validé ;
- login validé.

Prochaine étape :
- profil utilisateur réel ;
- rôle/scope réel ;
- logout frontend ;
- changement de périmètre ;
- poursuite des modules métier.
