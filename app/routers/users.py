from typing import Any

from fastapi import APIRouter, Depends

from ..litellm_client import LiteLLMClient, get_litellm_client
from ..security import require_app_api_key

router = APIRouter(prefix="/api/users", tags=["users"], dependencies=[Depends(require_app_api_key)])


@router.get("")
async def list_users(client: LiteLLMClient = Depends(get_litellm_client)) -> Any:
    response = await client.request("GET", "/user/list")
    return response.json()


@router.post("")
async def create_user(payload: dict, client: LiteLLMClient = Depends(get_litellm_client)) -> Any:
    response = await client.request("POST", "/user/new", json=payload)
    return response.json()


@router.post("/update")
async def update_user(payload: dict, client: LiteLLMClient = Depends(get_litellm_client)) -> Any:
    response = await client.request("POST", "/user/update", json=payload)
    return response.json()


@router.post("/delete")
async def delete_user(payload: dict, client: LiteLLMClient = Depends(get_litellm_client)) -> Any:
    response = await client.request("POST", "/user/delete", json=payload)
    return response.json()


@router.get("/info")
async def user_info(user_id: str, client: LiteLLMClient = Depends(get_litellm_client)) -> Any:
    response = await client.request("GET", "/user/info", params={"user_id": user_id})
    return response.json()
