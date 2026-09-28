from typing import Any

from fastapi import APIRouter, Depends, Request

from ..litellm_client import LiteLLMClient, get_litellm_client
from ..security import require_app_api_key

router = APIRouter(prefix="/api/spend", tags=["spend"], dependencies=[Depends(require_app_api_key)])


@router.get("/logs")
async def spend_logs(request: Request, client: LiteLLMClient = Depends(get_litellm_client)) -> Any:
    """Accepte les mêmes filtres que LiteLLM (api_key, user_id, start_date, end_date, ...)."""
    response = await client.request("GET", "/spend/logs", params=dict(request.query_params))
    return response.json()


@router.get("/global")
async def global_spend(client: LiteLLMClient = Depends(get_litellm_client)) -> Any:
    response = await client.request("GET", "/global/spend")
    return response.json()


@router.get("/global/report")
async def global_spend_report(request: Request, client: LiteLLMClient = Depends(get_litellm_client)) -> Any:
    response = await client.request("GET", "/global/spend/report", params=dict(request.query_params))
    return response.json()


@router.post("/calculate")
async def calculate_spend(payload: dict, client: LiteLLMClient = Depends(get_litellm_client)) -> Any:
    response = await client.request("POST", "/spend/calculate", json=payload)
    return response.json()


@router.post("/budgets")
async def create_budget(payload: dict, client: LiteLLMClient = Depends(get_litellm_client)) -> Any:
    response = await client.request("POST", "/budget/new", json=payload)
    return response.json()


@router.get("/budgets/info")
async def budget_info(budget_id: str, client: LiteLLMClient = Depends(get_litellm_client)) -> Any:
    response = await client.request("GET", "/budget/info", params={"budget_id": budget_id})
    return response.json()
