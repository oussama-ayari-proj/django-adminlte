# 🏥 Documentation API - Système de Gestion Hospitalière

<style>
table {
  border-collapse: collapse;
  width: 100%;
  margin: 20px 0;
}

table, th, td {
  border: 1px solid black;
}

th, td {
  padding: 12px 15px;
  text-align: left;
}

th {
  background-color: #f2f2f2;
  font-weight: bold;
}

tr:nth-child(even) {
  background-color: #f9f9f9;
}

tr:hover {
  background-color: #f5f5f5;
}
</style>

## 📋 Vue d'ensemble

Ce document présente l'ensemble des APIs du système de gestion hospitalière Django AdminLTE. Le système est organisé en modules spécialisés pour différents aspects de la gestion hospitalière.

---

## 🗂️ Architecture des Modules

### Structure des URLs principales :
- **`/`** - Module Hospitalisation (module principal)
- **`/predictions-lits/`** - Module Prédictions
- **`/fileupload/`** - Module Téléchargement de fichiers
- **`/hebergement-hors-uf/`** - Module Hébergement hors UF
- **`/statistiques/`** - Module Statistiques globales
- **`/correlation-absences-lits/`** - Module Corrélation absences-lits
- **`/admin/`** - Interface d'administration Django

---

## 🏥 Module Hospitalisation (Principal)
**Base URL : `/`**

### Pages Principales
| Endpoint | Vue | Description |
|----------|-----|-------------|
| `''` | `views.index` | **Tableau de bord principal** - Vue d'ensemble des indicateurs hospitaliers |
| `lits-fermes/` | `views.index_lits_fermes` | **Analyse des lits fermés** - Impact des absences sur la fermeture des lits |
| `analyse-sejours/` | `views.analyse_sejours` | **Analyse des séjours** - Durées et patterns de prise en charge |

### APIs de Données
| Endpoint | Vue | Description |
|----------|-----|-------------|
| `api/stats/` | `views.get_hospitalisation_stats` | **Statistiques globales d'hospitalisation** - Indicateurs de performance et occupation |
| `api/stats/lits-fermes/` | `views.get_lits_fermes_stats` | **Données lits fermés** - Stats par semaine/UF avec corrélations absences |
| `api/sejours-analysis/` | `views.get_sejours_analysis` | **Analyse des séjours** - Durée moyenne, taux de rotation, flux patients |
| `api/date-ranges/` | `views.get_date_ranges` | **Plages de dates** - Périodes disponibles pour filtrage temporel |

---

## 🔮 Module Prédictions
**Base URL : `/predictions-lits/`**

### Page Principale
| Endpoint | Vue | Description |
|----------|-----|-------------|
| `''` | `views.index` | **Tableau de bord prédictions** - Prévisions d'occupation des lits |

### APIs de Prédiction
| Endpoint | Vue | Description |
|----------|-----|-------------|
| `api/stats/` | `views.get_predictions_stats` | **Statistiques prédictives** - Métriques de précision des modèles |
| `api/predictions/` | `views.get_predictions` | **Données prédictives** - Prévisions d'occupation futures |
| `api/filter-ufs-mae/` | `views.filter_ufs_with_mae_above_zero` | **Filtrage par précision** - UF avec erreur moyenne > 0 |

---


## 📈 Module Statistiques Globales
**Base URL : `/statistiques/`**

### Page Principale
| Endpoint | Vue | Description |
|----------|-----|-------------|
| `''` | `views.statistiques_globales` | **Dashboard statistiques** - Vue consolidée de tous les indicateurs |

### APIs Statistiques
| Endpoint | Vue | Description |
|----------|-----|-------------|
| `api/global/` | `views.api_global_stats` | **Stats globales** - Indicateurs transversaux de l'établissement |
| `api/em/` | `views.api_em_stats` | **Stats emplois-métiers** - Analyse RH et répartition des compétences |
| `api/charge-em/` | `views.get_charge_em` | **Charge de travail** - Indicateurs de surcharge par métier |
| `api/ems-by-year/` | `views.api_ems_by_year` | **Évolution annuelle** - Tendances RH sur plusieurs années |

---

## 🏠 Module Hébergement Hors UF
**Base URL : `/hebergement-hors-uf/`**

### Page Principale
| Endpoint | Vue | Description |
|----------|-----|-------------|
| `''` | `views.index` | **Gestion hébergement** - Lits temporaires hors unités standards |

### APIs Hébergement
| Endpoint | Vue | Description |
|----------|-----|-------------|
| `api/stats/` | `views.get_hebergement_stats` | **Stats hébergement** - Utilisation des lits temporaires |
| `api/ems-by-year/` | `views.get_ems_by_year` | **Personnel par année** - Évolution des équipes hébergement |
| `api/get_lits_fermes_filtres/` | `views.get_lits_fermes_filtres` | **Lits fermés filtrés** - Impact sur capacité hébergement |

---

## 🔗 Module Corrélation Absences-Lits
**Base URL : `/correlation-absences-lits/`**

### Page Principale
| Endpoint | Vue | Description |
|----------|-----|-------------|
| `''` | `views.index` | **Analyse corrélation** - Impact des absences sur fermeture de lits |

### APIs de Corrélation
| Endpoint | Vue | Description |
|----------|-----|-------------|
| `get_ufs/` | `views.get_ufs` | **Liste UF** - Unités Fonctionnelles disponibles pour analyse corrélation |
| `get_metiers/` | `views.get_metiers` | **Liste métiers** - Professions médicales pour analyse d'impact absences |
| `get_data_metiers/` | `views.get_data_metiers` | **Données métiers** - Corrélations absences/fermetures avec scores R² |
| `get_metier_graph/` | `views.get_metier_graph` | **Graphiques métiers** - Visualisations impact par profession avec régression |

---

## 📁 Module Téléchargement de Fichiers
**Base URL : `/fileupload/`**

### APIs de Gestion de Fichiers
| Endpoint | Vue | Description |
|----------|-----|-------------|
| `upload/` | `views.upload_file` | **Téléchargement** - Import masse de données Excel/CSV avec validation |
| `success-multiple/<session_key>/` | `views.upload_success_multiple` | **Confirmation multi-fichiers** - Validation import en lot avec rapport erreurs |

---


## 🔧 Logique Métier Globale

### 🎯 Objectifs du Système
1. **Optimisation des ressources** - Maximiser l'utilisation des lits et du personnel
2. **Prédiction proactive** - Anticiper les besoins en capacité hospitalière
3. **Analyse d'impact** - Comprendre l'effet des absences sur les services
4. **Reporting consolidé** - Tableaux de bord pour la prise de décision

### 🔄 Flux de Données
1. **Import** → Téléchargement de données via module fileupload
2. **Traitement** → Analyse et corrélation via modules spécialisés
3. **Prédiction** → Modèles d'IA pour prévisions futures
4. **Visualisation** → Dashboards et graphiques interactifs

### 📊 Indicateurs Clés
- **Taux d'occupation des lits** - Performance opérationnelle
- **Impact des absences** - Corrélation RH/capacité
- **Précision prédictive** - Fiabilité des modèles d'IA
- **Efficiency des planifications** - Optimisation des ressources

---

## 🚀 Utilisation des APIs


### Authentification
- Toutes les APIs nécessitent une authentification Django
- Sessions utilisateur maintenues via cookies
- Accès basé sur les permissions utilisateur

### Gestion d'Erreurs
- Codes HTTP standards (200, 400, 401, 404, 500)
- Messages d'erreur descriptifs en français
- Logs détaillés pour le debugging

---

## 📝 Notes Techniques

### Technologies Utilisées
- **Backend** : Django 4.1+ avec Python 3.11+
- **Frontend** : AdminLTE avec Chart.js, Select2, jQuery
- **Base de données** : MySQL 8.0+ pour production, SQLite pour développement
- **IA/ML** : MLflow + Scikit-learn pour prédictions et analyses de corrélation

### Performance
- Pagination automatique pour grandes datasets
- Requêtes AJAX pour UX fluide sans rechargement
- Optimisation des requêtes SQL avec indexation MySQL
- Compression des réponses JSON pour APIs

### Infrastructure
- **Serveur Web** : Gunicorn + Nginx pour production
- **Base de données** : MySQL 8.0 avec support UTF8MB4
- **Stockage** : Fichiers statiques et media séparés
- **Monitoring** : Logs Django structurés

### Sécurité
- Protection CSRF sur toutes les APIs
- Validation des données d'entrée avec Django Forms
- Permissions granulaires par module et utilisateur
- Audit trail des actions utilisateur
- Authentification par session Django
- Chiffrement des mots de passe avec PBKDF2

### Base de Données
- **MySQL 8.0+** en production avec encodage UTF8MB4
- **SQLite** pour développement et tests
- **Migrations Django** pour évolution du schéma
- **Index optimisés** pour requêtes fréquentes
- **Contraintes d'intégrité** au niveau base de données

---

*Documentation générée le 28 juillet 2025*
*Version du système : Django AdminLTE Optisoin v1.0*
