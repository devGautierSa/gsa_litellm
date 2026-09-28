from typing import Any

from fastapi import APIRouter, Depends

from ..litellm_client import LiteLLMClient, get_litellm_client
from ..security import require_app_api_key

router = APIRouter(prefix="/api/keys", tags=["keys"], dependencies=[Depends(require_app_api_key)])


@router.get("")
async def list_keys(client: LiteLLMClient = Depends(get_litellm_client)) -> Any:
    response = await client.request("GET", "/key/list")
    return response.json()


@router.post("/generate")
async def generate_key(payload: dict, client: LiteLLMClient = Depends(get_litellm_client)) -> Any:
    response = await client.request("POST", "/key/generate", json=payload)
    return response.json()


@router.post("/update")
async def update_key(payload: dict, client: LiteLLMClient = Depends(get_litellm_client)) -> Any:
    response = await client.request("POST", "/key/update", json=payload)
    return response.json()


@router.post("/delete")
async def delete_key(payload: dict, client: LiteLLMClient = Depends(get_litellm_client)) -> Any:
    response = await client.request("POST", "/key/delete", json=payload)
    return response.json()


@router.get("/info")
async def key_info(key: str, client: LiteLLMClient = Depends(get_litellm_client)) -> Any:
    response = await client.request("GET", "/key/info", params={"key": key})
    return response.json()
