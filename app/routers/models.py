from typing import Any

from fastapi import APIRouter, Depends

from ..litellm_client import LiteLLMClient, get_litellm_client
from ..security import require_app_api_key

router = APIRouter(prefix="/api/models", tags=["models"], dependencies=[Depends(require_app_api_key)])


@router.get("")
async def list_models(client: LiteLLMClient = Depends(get_litellm_client)) -> Any:
    """Liste des modèles exposés (format compatible OpenAI)."""
    response = await client.request("GET", "/v1/models")
    return response.json()


@router.get("/info")
async def model_info(client: LiteLLMClient = Depends(get_litellm_client)) -> Any:
    """Détail complet des modèles configurés côté proxy (routing, params, etc.)."""
    response = await client.request("GET", "/model/info")
    return response.json()


@router.post("")
async def add_model(payload: dict, client: LiteLLMClient = Depends(get_litellm_client)) -> Any:
    response = await client.request("POST", "/model/new", json=payload)
    return response.json()


@router.post("/update")
async def update_model(payload: dict, client: LiteLLMClient = Depends(get_litellm_client)) -> Any:
    response = await client.request("POST", "/model/update", json=payload)
    return response.json()


@router.delete("/{model_id}")
async def delete_model(model_id: str, client: LiteLLMClient = Depends(get_litellm_client)) -> Any:
    response = await client.request("POST", "/model/delete", json={"id": model_id})
    return response.json()
