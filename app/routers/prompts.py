import json
import re
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from ..db import get_connection
from ..litellm_client import LiteLLMClient, get_litellm_client
from ..security import require_app_api_key

router = APIRouter(prefix="/api/prompts", tags=["prompts"], dependencies=[Depends(require_app_api_key)])

_VARIABLE_PATTERN = re.compile(r"{{\s*(\w+)\s*}}")


class PromptCreate(BaseModel):
    name: str
    description: str | None = None
    template: str
    model: str | None = None
    variables: list[str] = Field(default_factory=list)


class PromptRunRequest(BaseModel):
    variables: dict[str, str] = Field(default_factory=dict)
    model: str | None = None
    extra_messages: list[dict] = Field(default_factory=list)


def _row_to_dict(row: Any) -> dict:
    return {
        "id": row["id"],
        "name": row["name"],
        "description": row["description"],
        "template": row["template"],
        "model": row["model"],
        "variables": json.loads(row["variables"] or "[]"),
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def _get_prompt_or_404(conn, prompt_id: int):
    row = conn.execute("SELECT * FROM prompts WHERE id = ?", (prompt_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Prompt introuvable")
    return row


@router.get("")
def list_prompts() -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM prompts ORDER BY id DESC").fetchall()
    return [_row_to_dict(row) for row in rows]


@router.post("")
def create_prompt(payload: PromptCreate) -> dict:
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO prompts (name, description, template, model, variables) VALUES (?, ?, ?, ?, ?)",
            (payload.name, payload.description, payload.template, payload.model, json.dumps(payload.variables)),
        )
        row = _get_prompt_or_404(conn, cursor.lastrowid)
    return _row_to_dict(row)


@router.get("/{prompt_id}")
def get_prompt(prompt_id: int) -> dict:
    with get_connection() as conn:
        row = _get_prompt_or_404(conn, prompt_id)
    return _row_to_dict(row)


@router.put("/{prompt_id}")
def update_prompt(prompt_id: int, payload: PromptCreate) -> dict:
    with get_connection() as conn:
        _get_prompt_or_404(conn, prompt_id)
        conn.execute(
            """
            UPDATE prompts
            SET name = ?, description = ?, template = ?, model = ?, variables = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (payload.name, payload.description, payload.template, payload.model, json.dumps(payload.variables), prompt_id),
        )
        row = _get_prompt_or_404(conn, prompt_id)
    return _row_to_dict(row)


@router.delete("/{prompt_id}")
def delete_prompt(prompt_id: int) -> dict:
    with get_connection() as conn:
        _get_prompt_or_404(conn, prompt_id)
        conn.execute("DELETE FROM prompts WHERE id = ?", (prompt_id,))
    return {"deleted": prompt_id}


@router.post("/{prompt_id}/run")
async def run_prompt(
    prompt_id: int,
    payload: PromptRunRequest,
    client: LiteLLMClient = Depends(get_litellm_client),
) -> Any:
    """Rend le template (variables {{var}}) puis l'envoie au proxy LiteLLM via /chat/completions."""
    with get_connection() as conn:
        row = _get_prompt_or_404(conn, prompt_id)
    prompt = _row_to_dict(row)

    missing = [name for name in prompt["variables"] if name not in payload.variables]
    if missing:
        raise HTTPException(status_code=400, detail=f"Variables manquantes : {', '.join(missing)}")

    rendered = _VARIABLE_PATTERN.sub(lambda m: payload.variables.get(m.group(1), m.group(0)), prompt["template"])
    model = payload.model or prompt["model"]
    if not model:
        raise HTTPException(status_code=400, detail="Aucun modèle spécifié pour ce prompt")

    messages = [{"role": "user", "content": rendered}, *payload.extra_messages]
    response = await client.request("POST", "/chat/completions", json={"model": model, "messages": messages})
    return response.json()
