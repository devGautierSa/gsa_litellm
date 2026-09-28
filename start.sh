#!/usr/bin/env bash
# Vérifie l'environnement (venv, dépendances, variables) puis démarre le serveur.
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")"

PYTHON_BIN="${PYTHON_BIN:-python3}"
VENV_DIR=".venv"
ENV_FILE=".env"
ENV_EXAMPLE=".env.example"

echo "==> Vérification de Python"
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "Erreur: $PYTHON_BIN introuvable. Installez Python 3.11+ avant de continuer." >&2
  exit 1
fi

echo "==> Vérification de l'environnement virtuel ($VENV_DIR)"
if [ ! -d "$VENV_DIR" ]; then
  echo "    Création de l'environnement virtuel..."
  "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

echo "==> Vérification/installation des dépendances (requirements.txt)"
pip install -q --upgrade pip
pip install -q -r requirements.txt

echo "==> Vérification du fichier .env"
if [ ! -f "$ENV_FILE" ]; then
  if [ -f "$ENV_EXAMPLE" ]; then
    echo "    Aucun .env trouvé, copie de $ENV_EXAMPLE vers $ENV_FILE"
    cp "$ENV_EXAMPLE" "$ENV_FILE"
  fi
  echo "Erreur: merci de renseigner les valeurs dans $ENV_FILE avant de relancer ce script." >&2
  exit 1
fi

echo "==> Vérification des variables d'environnement"
python - <<'PYEOF'
import sys

from app.config import get_settings

try:
    settings = get_settings()
except Exception as exc:
    print(f"Erreur de configuration: {exc}", file=sys.stderr)
    sys.exit(1)

errors = []
if not settings.litellm_master_key or settings.litellm_master_key == "sk-changeme":
    errors.append("LITELLM_MASTER_KEY n'est pas renseignée (valeur placeholder détectée).")
if not settings.litellm_base_url:
    errors.append("LITELLM_BASE_URL est vide.")

if not settings.app_api_key or settings.app_api_key == "change-me-please":
    print(
        "Attention: APP_API_KEY absente ou laissée à sa valeur d'exemple. "
        "Le serveur sera accessible sans authentification.",
        file=sys.stderr,
    )

if errors:
    for message in errors:
        print(f"Erreur: {message}", file=sys.stderr)
    sys.exit(1)

print(f"    LITELLM_BASE_URL   = {settings.litellm_base_url}")
print(f"    APP_API_KEY définie = {bool(settings.app_api_key)}")
PYEOF

HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"
RELOAD_FLAG=""
if [ "${RELOAD:-0}" = "1" ]; then
  RELOAD_FLAG="--reload"
fi

echo "==> Démarrage du serveur sur ${HOST}:${PORT}"
exec uvicorn app.main:app --host "$HOST" --port "$PORT" $RELOAD_FLAG "$@"
