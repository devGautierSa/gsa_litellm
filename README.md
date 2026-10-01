# GSA LiteLLM Manager

Serveur FastAPI + dashboard web pour administrer le proxy LiteLLM à
`https://ai.proxy.gautiersa.fr` : modèles, chat, clés API, utilisateurs, équipes,
dépenses et un registre de prompts local (avec exécution via le proxy).

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Renseignez dans `.env` :
- `LITELLM_MASTER_KEY` : la master key (ou clé admin) du proxy LiteLLM.
- `APP_API_KEY` : clé pour protéger l'accès à ce serveur (fortement recommandé).

Pour générer une clé aléatoire de 64 caractères (hexadécimal) pour `APP_API_KEY` :

```bash
openssl rand -hex 32
```

## Démarrage

```bash
./start.sh
```

Ce script crée/active le venv, installe les dépendances, vérifie que `.env` existe et que
`LITELLM_MASTER_KEY`/`LITELLM_BASE_URL` sont bien renseignées (échec explicite sinon), puis lance uvicorn.

Variables d'environnement optionnelles pour le script : `HOST` (défaut `0.0.0.0`), `PORT` (défaut `8000`),
`RELOAD=1` (active `--reload`).

- Dashboard : http://localhost:8000/
- Documentation API interactive : http://localhost:8000/docs

## Architecture

- `app/litellm_client.py` : client HTTP vers le proxy LiteLLM (porte la master key, jamais exposée au frontend).
- `app/routers/` : routes typées (`models`, `chat`, `keys`, `users`, `teams`, `spend`, `prompts`) + `proxy.py` en passerelle générique vers tout endpoint LiteLLM non couvert (`/api/proxy/{path}`).
- `app/db.py` + `app/routers/prompts.py` : registre de prompts stocké en SQLite local (`data/prompts.db`), avec substitution de variables `{{var}}` et exécution via `/chat/completions`.
- `static/` : dashboard HTML/CSS/JS statique (aucun build requis).

Toutes les routes `/api/*` sont protégées par le header `X-App-Api-Key` si `APP_API_KEY` est défini.
