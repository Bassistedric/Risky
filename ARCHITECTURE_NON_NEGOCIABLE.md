# RISKY — Exigences non négociables

## Portabilité / réversibilité — priorité absolue

RISKY doit pouvoir être repris et redéployé dans un autre environnement sans reconstruire l'application.

### Séparation obligatoire

**RISKY Core** : frontend, backend/API, logique métier, structure de base de données, moteur de formulaires, workflows, cotation des risques, documentation, scripts d'installation/migration et outils d'import/export.

**Configuration d'environnement** : nom/branding, entités ou métiers, listes de référence, compétences, méthodes de cotation, seuils, formulaires, workflows, KPI, processus et modules activés.

**Données d'entreprise** : personnes, accidents, actions, analyses réalisées, équipements, documents internes, historiques, KPI réels et données de suivi. Ces données restent strictement séparées du Core.

### Deux exports obligatoires

1. **Export complet d'instance** : destiné à l'entreprise exploitante, avec moteur, configuration, données, historique et documentation de reprise.
2. **Export environnement neutre** : destiné au redéploiement du moteur ailleurs, avec Core, schéma de données, configuration générique, modèles, formulaires, workflows, méthodes et documentation, en excluant explicitement toutes les données propres à l'entreprise précédente.

### Interdictions d'architecture

- Aucun nom d'entreprise codé en dur dans le moteur.
- Aucun site, métier, utilisateur ou logo codé en dur.
- Aucun identifiant d'entreprise nécessaire au fonctionnement du Core.
- Aucune dépendance au compte personnel du créateur.
- Aucune dépendance imposant de reconstruire RISKY lors d'un changement d'organisation.

### Administration fonctionnelle sans IT

L'administrateur fonctionnel RISKY doit pouvoir modifier : organisation, métiers/entités, utilisateurs et rôles, compétences, listes, formulaires, KPI, processus, matrices de risques, seuils, modules actifs et branding sans intervention IT.

## Structure de démonstration VMA Sud

Afin d'anticiper la centralisation future des implantations, la démo n'utilise plus Louvain-la-Neuve, Jumet et Alleur comme axes principaux. L'axe de filtre et de reporting devient :

- VMA Sud — global
- HVAC
- REF
- ELEC

Décision actée le 21/08/2026.