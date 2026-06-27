# Artisans BF — Annuaire géolocalisé des artisans et petits commerces

Plateforme web responsive permettant aux citoyens de trouver rapidement des artisans et petits commerces proches d’eux, et permettant aux artisans de publier leurs fiches, d’être contactés et d’être évalués automatiquement à partir des commentaires.

## 1. Liens importants

- Dépôt GitHub : `https://github.com/sanoncarlos2006-a11y/artisans-bf`
- Backend API : `http://127.0.0.1:8000` en local ou URL de déploiement backend
- Documentation technique PDF : `docs/documentation-technique.pdf`

## 2. Technologies retenues

- Backend : Python 3.11.9, FastAPI
- Base de données : SQLite en développement, PostgreSQL possible en production
- Frontend : HTML, CSS, JavaScript
- Carte : Leaflet.js + OpenStreetMap
- Versioning et collaboration : GitHub, branches, Pull Requests, GitHub Actions

## 3. Structure du projet

```text
artisans-bf/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── routes/
│   │   └── services/
│   ├── uploads/
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── index.html
│   ├── pages/
│   └── assets/
│       ├── css/style.css
│       └── js/
├── docs/
├── .github/workflows/
├── .gitignore
├── docker-compose.yml
└── README.md
```

## 4. Branches officielles

| Branche | Rôle |
|---|---|
| `main` | Version stable finale uniquement, utilisée pour la livraison. |
| `develop` | Version d’intégration testée régulièrement. |
| `feature/frontend-ui` | Interfaces, formulaires, carte, affichage recherche et fiche détail. |
| `feature/backend-api` | Authentification, commerces, publication/retrait, photos. |
| `feature/ai-search` | Recherche, géolocalisation, commentaires, notation IA. |
| `feature/devops-docs` | GitHub, CI/CD, documentation, ZIP final, tests de livraison. |

## 5. Installation locale rapide

### 5.1 Cloner le projet

```bash
git clone https://github.com/sanoncarlos2006-a11y/artisans-bf.git
cd artisans-bf
```

### 5.2 Lancer le backend

```bash
cd backend
python -m venv venv

venv\Scripts\activate


pip install -r requirements.txt

copy .env.example .env  


uvicorn app.main:app --reload
```

Backend disponible sur : `http://127.0.0.1:8000`

Documentation Swagger FastAPI : `http://127.0.0.1:8000/docs`

### 5.3 Lancer le frontend

Dans un deuxième terminal :

```bash
cd frontend
python -m http.server 5500
```

Frontend disponible sur : `http://127.0.0.1:5500`

