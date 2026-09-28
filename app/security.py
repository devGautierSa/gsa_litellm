from fastapi import Header, HTTPException, status

from .config import get_settings


async def require_app_api_key(x_app_api_key: str | None = Header(default=None)) -> None:
    """Protège les routes /api/* avec la clé définie dans APP_API_KEY (si configurée)."""
    settings = get_settings()
    if settings.app_api_key and x_app_api_key != settings.app_api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Clé API invalide ou manquante")
