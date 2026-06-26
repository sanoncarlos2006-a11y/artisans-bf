# Artisans BF — Annuaire géolocalisé des artisans et petits commerces

Plateforme web responsive permettant aux citoyens de trouver rapidement des artisans et petits commerces proches d’eux, et permettant aux artisans de publier leurs fiches, d’être contactés et d’être évalués automatiquement à partir des commentaires.

## 1. Liens importants

- Dépôt GitHub : `https://github.com/<organisation-ou-equipe>/artisans-bf`
- Frontend public GitHub Pages : `https://<organisation-ou-equipe>.github.io/artisans-bf/`
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

Règle stricte : personne ne code directement sur `main`. Les ajouts passent par une Pull Request vers `develop`, puis `develop` est fusionnée dans `main` seulement pour la version finale.

## 5. Installation locale rapide

### 5.1 Cloner le projet

```bash
git clone https://github.com/<organisation-ou-equipe>/artisans-bf.git
cd artisans-bf
```

### 5.2 Lancer le backend

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
copy .env.example .env  # Windows
# cp .env.example .env  # Linux/Mac

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

## 6. Variables d’environnement attendues

Créer `backend/.env` à partir de `backend/.env.example`.

```env
APP_NAME=Artisans BF
APP_ENV=development
SECRET_KEY=change-me-in-production
DATABASE_URL=sqlite:///./artisans_bf.db
ACCESS_TOKEN_EXPIRE_MINUTES=1440
CORS_ORIGINS=http://127.0.0.1:5500,http://localhost:5500
UPLOAD_DIR=uploads
```

Ne jamais envoyer le fichier `.env` sur GitHub.

## 7. Commandes Git importantes

### Créer les branches au départ

```bash
git checkout -b develop
git push -u origin develop

git checkout -b feature/frontend-ui
git push -u origin feature/frontend-ui

git checkout develop
git checkout -b feature/backend-api
git push -u origin feature/backend-api

git checkout develop
git checkout -b feature/ai-search
git push -u origin feature/ai-search

git checkout develop
git checkout -b feature/devops-docs
git push -u origin feature/devops-docs
```

### Travailler chaque jour

```bash
git checkout feature/devops-docs
git pull origin develop
git status
git add .
git commit -m "docs: ajouter procedure github et deploiement"
git push origin feature/devops-docs
```

Ensuite, ouvrir une Pull Request de `feature/devops-docs` vers `develop`.

## 8. Convention de commits

- `feat:` nouvelle fonctionnalité
- `fix:` correction de bug
- `docs:` documentation
- `style:` correction visuelle sans changement logique
- `refactor:` amélioration interne
- `test:` ajout ou correction de tests
- `chore:` configuration, nettoyage, maintenance

Exemples :

```bash
git commit -m "feat: ajouter formulaire de creation de commerce"
git commit -m "fix: corriger le filtre par categorie"
git commit -m "docs: completer la procedure de deploiement"
```

## 9. Tests rapides avant Pull Request

Avant chaque PR, vérifier :

```bash
cd backend
python -m compileall app
uvicorn app.main:app --reload
```

Puis tester dans le navigateur :

- création de compte ;
- connexion ;
- ajout de commerce ;
- publication/retrait ;
- recherche ;
- carte ;
- commentaire avec note IA ;
- partage WhatsApp.

## 10. Déploiement frontend sur GitHub Pages

Le workflow `.github/workflows/frontend-deploy.yml` publie le dossier `frontend/` sur GitHub Pages à chaque push sur `main`.

À faire dans GitHub :

1. Aller dans `Settings` > `Pages`.
2. Dans `Build and deployment`, choisir `GitHub Actions`.
3. Faire une Pull Request finale de `develop` vers `main`.
4. Vérifier l’action `Deploy frontend to GitHub Pages`.
5. Tester l’URL publique.

## 11. Livrables finaux

- Application fonctionnelle.
- Dépôt GitHub propre et accessible au jury.
- Documentation technique PDF dans `docs/`.
- ZIP final inférieur à 100 Mo.
- Données de démonstration.
- Scénario de présentation testé.

## 12. Comptes et données de démonstration

À compléter avant livraison :

| Type | Identifiant | Mot de passe | Rôle |
|---|---|---|---|
| Artisan démo | `demo@artisansbf.local` | `Demo@12345` | propriétaire de commerces |
| Citoyen démo | `client@artisansbf.local` | `Client@12345` | recherche et commentaires |

Ne pas utiliser ces mots de passe en production réelle.
