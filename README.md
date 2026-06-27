# Artisans BF

Annuaire web géolocalisé pour trouver des artisans et petits commerces au Burkina Faso.  
Le projet contient un backend FastAPI avec SQLite et un frontend HTML/CSS/JavaScript servi en statique.

## Fonctionnalités

- inscription et connexion artisan ;
- création de fiches commerces ;
- publication et retrait de fiches ;
- recherche par métier, nom, quartier, note minimale et proximité ;
- carte Leaflet/OpenStreetMap ;
- ouverture directe d'un commerce ou d'un itinéraire dans Google Maps ;
- ajout de photos ;
- commentaires avec note automatique par IA locale ou fallback mots-clés ;
- données de démonstration.

## Prérequis

- Python 3.11 recommandé ;
- Node.js 20+ recommandé pour le check frontend ;
- un navigateur récent ;
- accès internet au premier lancement pour installer les dépendances et charger Leaflet/OpenStreetMap.

Sur ce poste, un Python portable local peut aussi être utilisé avec :

```powershell
.\.python311\python.exe --version
```

Si `.python311` n’existe pas, utilisez simplement `python` après avoir installé Python 3.11.

## Installation Backend

Depuis la racine du projet :

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

Si vous utilisez le Python portable local déjà présent :

```powershell
cd backend
..\.python311\python.exe .tmp\pip.pyz install -r requirements.txt
```

## Configuration

Le fichier `backend/.env` doit contenir au minimum :

```env
APP_NAME="Annuaire Artisans BF API"
APP_ENV=local
DEMO_MODE=true
SECRET_KEY=change-me-local-demo-secret-32-bytes-minimum
ACCESS_TOKEN_EXPIRE_MINUTES=60
DATABASE_URL=sqlite:///./annuaire_artisans.db
UPLOAD_DIR=uploads
MAX_PHOTOS_PER_BUSINESS=3
MAX_UPLOAD_SIZE_MB=5
OLLAMA_HOST=http://127.0.0.1:11434
OLLAMA_MODEL=llama3.1:8b
```

Ollama est optionnel. Si Ollama n’est pas disponible, l’application utilise automatiquement une notation par mots-clés.

## Initialiser Les Données Démo

Depuis `backend/` :

```powershell
python scripts\seed_demo.py
```

Avec le Python portable local :

```powershell
..\.python311\python.exe scripts\seed_demo.py
```

Compte démo :

| Identifiant | Mot de passe |
|---|---|
| `+22670000000` | `demo1234` |

## Lancer Le Backend

Depuis `backend/` :

```powershell
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Avec le Python portable local :

```powershell
..\.python311\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

API :

- health : http://127.0.0.1:8000/health
- routes API : http://127.0.0.1:8000/docs
- recherche JSON : http://127.0.0.1:8000/search

## Lancer Le Frontend

Ouvrir un deuxième terminal, puis depuis `frontend/` :

```powershell
python -m http.server 5500 --bind 127.0.0.1
```

Avec le Python portable local :

```powershell
..\.python311\python.exe -m http.server 5500 --bind 127.0.0.1
```

Site :

- accueil : http://127.0.0.1:5500/
- recherche : http://127.0.0.1:5500/search.html
- connexion : http://127.0.0.1:5500/login.html
- dashboard : http://127.0.0.1:5500/dashboard.html

Important : ne pas ouvrir les fichiers `.html` directement avec `file://`. Il faut passer par `http://127.0.0.1:5500`.

## Géolocalisation

La géolocalisation navigateur fonctionne seulement dans un contexte sécurisé :

- `https://...` ;
- `http://localhost:5500` ;
- `http://127.0.0.1:5500`.

Elle peut être bloquée si :

- le site est ouvert en `file://` ;
- le site est ouvert depuis une IP locale du type `http://192.168.x.x:5500` ;
- le navigateur refuse la permission GPS ;
- le téléphone ou le PC n’a pas encore fourni de position.

Le site prévoit maintenant un fallback : si le GPS est refusé ou indisponible, les champs latitude/longitude apparaissent dans la recherche. Exemple pour Ouagadougou :

```text
Latitude: 12.3714
Longitude: -1.5197
```

Dans le formulaire d’ajout de commerce, les champs latitude et longitude peuvent aussi être saisis manuellement.

Sur les fiches commerce et les résultats, le bouton Google Maps ouvre directement la position ou l'itinéraire vers le commerce. Si le navigateur donne la position actuelle, elle est utilisée comme point de départ ; sinon Google Maps choisit le départ côté application.

## Tests

Backend :

```powershell
cd backend
python -m compileall app
python -m pytest
```

Frontend :

```powershell
cd frontend
npm run check
```

Vérification rapide API :

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
Invoke-RestMethod http://127.0.0.1:8000/search
```

## Lancement Rapide Complet

Terminal 1 :

```powershell
cd backend
python scripts\seed_demo.py
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Terminal 2 :

```powershell
cd frontend
python -m http.server 5500 --bind 127.0.0.1
```

Puis ouvrir :

```text
http://127.0.0.1:5500/
```

## Structure

```text
artisans-bf/
├── backend/
│   ├── app/
│   ├── scripts/
│   ├── tests/
│   ├── uploads/
│   ├── .env.example
│   └── requirements.txt
├── frontend/
│   ├── assets/
│   ├── index.html
│   ├── search.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── business-form.html
│   └── business-detail.html
├── docs/
├── docker-compose.yml
└── README.md
```

## Notes De Livraison

- `backend/.env` ne doit pas être envoyé sur GitHub.
- Les bases SQLite locales (`*.db`) sont ignorées.
- Les uploads locaux sont ignorés sauf `backend/uploads/.gitkeep`.
- Les environnements Python locaux (`venv/`, `.venv/`, `.python*/`) sont ignorés.
