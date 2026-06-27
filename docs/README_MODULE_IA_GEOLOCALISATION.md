# Module Membre 3 — Backend uniquement

Ce dossier contient uniquement la partie du **Membre 3** :

- recherche géolocalisée ;
- calcul de distance ;
- état `ouvert / fermé / fermé temporairement` ;
- génération de liens d'itinéraire vers Google Maps/OpenStreetMap ;
- commentaires ;
- notation IA automatique sur 5 étoiles avec Ollama `qwen3:8b` ;
- fallback par mots-clés si Ollama est indisponible.

Aucun frontend n'est inclus dans cette version, afin de respecter la répartition de l'équipe.

## Point important sur les utilisateurs

Ce module ne crée pas de compte utilisateur et ne crée pas d'« utilisateur mécanicien ».

La création de compte appartient au module Auth/Backend principal. Quand un utilisateur connecté crée un commerce, le backend principal doit enregistrer son identifiant dans `owner_id` et son domaine d'activité dans `category`.

Exemple :

```json
{
  "owner_id": 12,
  "name": "Garage Wend-Panga",
  "category": "mecanicien",
  "latitude": 12.3856,
  "longitude": -1.4853,
  "opening_days": "0,1,2,3,4,5",
  "open_time": "08:00",
  "close_time": "18:00"
}
```

## Disponibilité / horaires

L'artisan renseigne lui-même ses horaires dans la fiche commerce :

- `opening_days` : jours d'ouverture, avec `0=lundi` et `6=dimanche` ;
- `open_time` : heure d'ouverture, exemple `08:00` ;
- `close_time` : heure de fermeture, exemple `18:00` ;
- `is_temporarily_closed` : permet de forcer l'état `fermé temporairement`.

Le backend calcule automatiquement :

- `open_status` : `ouvert`, `fermé` ou `fermé temporairement` ;
- `opening_days_labels` : liste des jours lisibles ;
- `hours_label` : exemple `lundi à samedi, 08:00 - 18:00`.

## Itinéraire type Google Maps

Le backend ne recrée pas Google Maps. Il fournit des liens prêts à ouvrir :

- `google_maps_url` : ouvrir la position du commerce ;
- `google_navigation_url` : ouvrir l'itinéraire vers le commerce ;
- `openstreetmap_url` : ouvrir la position dans OpenStreetMap.

Pour une vraie navigation guidée, le frontend ouvre `google_navigation_url`. Pour suivre la position de l'utilisateur dans l'application, le frontend devra utiliser `navigator.geolocation.watchPosition()`.

## Installation backend

Depuis VS Code :

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Sur Windows PowerShell :

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

## Configuration Ollama

Le fichier `backend/.env.example` est configuré pour :

```env
OLLAMA_ENABLED=true
OLLAMA_HOST=http://127.0.0.1:11434
OLLAMA_MODEL=qwen3:8b
```

Vérifier que le modèle existe :

```bash
ollama list
```

Si `ollama serve` retourne `address already in use`, cela veut dire qu'Ollama tourne déjà.

## Lancement backend

```bash
cd backend
source .venv/bin/activate
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Ou :

```bash
cd backend
./start_backend.sh
```

## Tests rapides

Backend actif :

```txt
http://127.0.0.1:8000/health
```

Statut Ollama :

```txt
http://127.0.0.1:8000/ai/status
```

Recherche géolocalisée :

```txt
http://127.0.0.1:8000/search?category=mecanicien&lat=12.3714&lng=-1.5197&radius_km=10
```

Itinéraire vers un commerce :

```txt
http://127.0.0.1:8000/businesses/1/navigation?lat=12.3714&lng=-1.5197&mode=walking
```

Sans données réelles venant du module commerce, la recherche peut retourner `[]`. C'est normal.

## Données de démonstration optionnelles

Le script ci-dessous est seulement pour tester le module seul. Il ne crée pas de comptes utilisateurs.

```bash
cd backend
source .venv/bin/activate
python scripts/seed_demo_optional.py
```

## Routes livrées

```txt
GET  /health
GET  /ai/status
POST /ai/rate-comment
GET  /search
GET  /businesses/{business_id}
GET  /businesses/{business_id}/navigation
POST /businesses/{business_id}/comments
GET  /businesses/{business_id}/comments
```

## Route IA

`POST /ai/rate-comment`

Body :

```json
{
  "comment": "Service rapide, artisan sérieux, prix abordable et travail propre."
}
```

Réponse attendue si Ollama fonctionne :

```json
{
  "rating": 5,
  "confidence": 0.9,
  "explanation": "...",
  "model": "ollama-qwen3:8b"
}
```

Si Ollama est indisponible, le backend retourne une note avec :

```json
"model": "fallback-keywords-v1"
```

## Route recherche

`GET /search`

Paramètres :

- `q` : recherche libre, par exemple `mécanicien` ;
- `category` : catégorie normalisée, par exemple `mecanicien` ;
- `min_rating` : note minimale ;
- `lat`, `lng` : position utilisateur ;
- `radius_km` : rayon de recherche.

La réponse contient :

- `distance_km` ;
- `open_status` ;
- `hours_label` ;
- `average_rating` ;
- `google_maps_url` ;
- `google_navigation_url` ;
- `openstreetmap_url` ;
- `latitude` / `longitude`.
