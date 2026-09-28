from typing import Any

import httpx
from fastapi import HTTPException

from .config import get_settings


def _safe_error_body(response: httpx.Response) -> Any:
    try:
        return response.json()
    except ValueError:
        return response.text


class LiteLLMClient:
    """Client HTTP vers le proxy LiteLLM. La master key n'est jamais transmise au frontend."""

    def __init__(self) -> None:
        settings = get_settings()
        self._base_url = settings.litellm_base_url.rstrip("/")
        self._master_key = settings.litellm_master_key
        self._timeout = settings.request_timeout_seconds

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any | None = None,
    ) -> httpx.Response:
        url = f"{self._base_url}/{path.lstrip('/')}"
        headers = {"Authorization": f"Bearer {self._master_key}"}
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            try:
                response = await client.request(method, url, params=params, json=json, headers=headers)
            except httpx.RequestError as exc:
                raise HTTPException(
                    status_code=502, detail=f"Impossible de contacter le proxy LiteLLM : {exc}"
                ) from exc

        if response.status_code >= 400:
            raise HTTPException(status_code=response.status_code, detail=_safe_error_body(response))
        return response


def get_litellm_client() -> LiteLLMClient:
    return LiteLLMClient()
