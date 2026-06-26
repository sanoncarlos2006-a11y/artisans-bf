## Objet de la Pull Request

Décrire clairement ce qui a été ajouté, corrigé ou supprimé.

## Module concerné

- [ ] Frontend UI/UX
- [ ] Backend API
- [ ] IA / recherche / géolocalisation
- [ ] GitHub / déploiement / documentation

## Comment tester

1. Lancer le backend : `cd backend && uvicorn app.main:app --reload`
2. Lancer le frontend : `cd frontend && python -m http.server 5500`
3. Tester les pages ou routes suivantes :
   - `...`

## Checklist avant fusion

- [ ] Le projet se lance localement.
- [ ] Les fichiers sensibles ne sont pas envoyés (`.env`, base locale, uploads réels).
- [ ] La branche est à jour avec `develop`.
- [ ] Les changements sont limités au module concerné.
- [ ] Le README ou la documentation a été mis à jour si nécessaire.
