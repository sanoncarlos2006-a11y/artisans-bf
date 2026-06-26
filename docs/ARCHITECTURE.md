# Architecture du projet — Artisans BF

## 1. Vue globale

Le projet suit une architecture API/client séparés :

- `backend/` contient l’API FastAPI, la base de données, les modèles, les routes et les services métiers.
- `frontend/` contient les pages HTML, les styles CSS et les scripts JavaScript consommant l’API.
- `docs/` contient la documentation technique et les captures.
- `.github/` contient les workflows CI/CD et les modèles de Pull Request.

## 2. Backend

```text
backend/app/
├── main.py
├── config.py
├── database.py
├── models/
├── schemas/
├── routes/
└── services/
```

Rôles :

- `models/` : tables utilisateurs, commerces, photos, commentaires, réinitialisation.
- `schemas/` : validation des données entrantes et sortantes.
- `routes/` : endpoints API.
- `services/` : logique métier : authentification, distance, IA, moyenne des notes.

## 3. Frontend

```text
frontend/
├── index.html
├── pages/
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── add-business.html
│   ├── search.html
│   └── business-details.html
└── assets/
    ├── css/style.css
    └── js/
```

Rôles :

- `api.js` : configuration et appels API.
- `auth.js` : inscription, connexion, session.
- `business.js` : ajout, modification, publication, retrait, partage WhatsApp.
- `search.js` : filtres par nom, catégorie, proximité et note.
- `map.js` : carte Leaflet/OpenStreetMap.
- `comments.js` : commentaires et affichage note IA.

## 4. Routes API attendues

| Module | Méthode | Route | Rôle |
|---|---:|---|---|
| Auth | POST | `/api/auth/register` | Créer un compte |
| Auth | POST | `/api/auth/login` | Connexion |
| Auth | POST | `/api/auth/forgot-password` | Demander une réinitialisation |
| Auth | POST | `/api/auth/reset-password` | Changer le mot de passe |
| Auth | GET | `/api/auth/me` | Profil connecté |
| Commerce | POST | `/api/businesses` | Enregistrer un commerce |
| Commerce | GET | `/api/businesses` | Lister les commerces publiés |
| Commerce | GET | `/api/businesses/{id}` | Détail commerce |
| Commerce | PUT | `/api/businesses/{id}` | Modifier une fiche |
| Commerce | PATCH | `/api/businesses/{id}/publish` | Publier |
| Commerce | PATCH | `/api/businesses/{id}/unpublish` | Retirer temporairement |
| Commerce | POST | `/api/businesses/{id}/photos` | Ajouter des photos |
| Recherche | GET | `/api/search` | Filtrer et trier |
| Avis/IA | POST | `/api/businesses/{id}/comments` | Ajouter avis et note IA |
| Avis/IA | GET | `/api/businesses/{id}/comments` | Lister avis |
| Avis/IA | POST | `/api/ai/rate-comment` | Tester notation IA |

## 5. Modèle de données minimal

- `users` : comptes utilisateurs.
- `businesses` : fiches commerces.
- `business_photos` : photos associées aux commerces.
- `comments` : commentaires et notes IA.
- `password_resets` : tokens ou codes de réinitialisation.
