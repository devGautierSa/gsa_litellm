from typing import Any

from fastapi import APIRouter, Depends

from ..litellm_client import LiteLLMClient, get_litellm_client
from ..security import require_app_api_key

router = APIRouter(prefix="/api/teams", tags=["teams"], dependencies=[Depends(require_app_api_key)])


@router.get("")
async def list_teams(client: LiteLLMClient = Depends(get_litellm_client)) -> Any:
    response = await client.request("GET", "/team/list")
    return response.json()


@router.post("")
async def create_team(payload: dict, client: LiteLLMClient = Depends(get_litellm_client)) -> Any:
    response = await client.request("POST", "/team/new", json=payload)
    return response.json()


@router.post("/update")
async def update_team(payload: dict, client: LiteLLMClient = Depends(get_litellm_client)) -> Any:
    response = await client.request("POST", "/team/update", json=payload)
    return response.json()


@router.post("/delete")
async def delete_team(payload: dict, client: LiteLLMClient = Depends(get_litellm_client)) -> Any:
    response = await client.request("POST", "/team/delete", json=payload)
    return response.json()


@router.get("/info")
async def team_info(team_id: str, client: LiteLLMClient = Depends(get_litellm_client)) -> Any:
    response = await client.request("GET", "/team/info", params={"team_id": team_id})
    return response.json()
