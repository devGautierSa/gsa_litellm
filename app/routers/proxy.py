from typing import Any

from fastapi import APIRouter, Depends, Request

from ..litellm_client import LiteLLMClient, get_litellm_client
from ..security import require_app_api_key

router = APIRouter(prefix="/api/proxy", tags=["proxy"], dependencies=[Depends(require_app_api_key)])

_BODY_METHODS = {"POST", "PUT", "PATCH"}


@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def passthrough(path: str, request: Request, client: LiteLLMClient = Depends(get_litellm_client)) -> Any:
    """Passerelle générique vers n'importe quel endpoint LiteLLM non couvert par les routes typées."""
    body = None
    if request.method in _BODY_METHODS:
        raw_body = await request.body()
        body = await request.json() if raw_body else None
    response = await client.request(request.method, f"/{path}", params=dict(request.query_params), json=body)
    return response.json()
