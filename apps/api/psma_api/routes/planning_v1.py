from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends

from psma_api.deps import get_planner_engine
from psma_api.models.planning import PlanRequestV1, PlanResponseV1
from psma_api.ports.planner_engine import PlannerEngine


router = APIRouter(prefix="/plan/v1", tags=["planning"])


@router.post(
    "/generate",
    response_model=PlanResponseV1,
    response_model_exclude_none=True,
)
async def generate_plan(
    request: PlanRequestV1,
    engine: PlannerEngine = Depends(get_planner_engine),
) -> Any:
    return await engine.generate_plan_v1(request)
