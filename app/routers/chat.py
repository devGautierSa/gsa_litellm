from typing import Any

from fastapi import APIRouter, Depends

from ..litellm_client import LiteLLMClient, get_litellm_client
from ..security import require_app_api_key

router = APIRouter(prefix="/api/chat", tags=["chat"], dependencies=[Depends(require_app_api_key)])


@router.post("/completions")
async def chat_completions(payload: dict, client: LiteLLMClient = Depends(get_litellm_client)) -> Any:
    """Proxy direct vers /chat/completions du serveur LiteLLM (playground de test)."""
    response = await client.request("POST", "/chat/completions", json=payload)
    return response.json()


@router.post("/embeddings")
async def embeddings(payload: dict, client: LiteLLMClient = Depends(get_litellm_client)) -> Any:
    response = await client.request("POST", "/embeddings", json=payload)
    return response.json()
