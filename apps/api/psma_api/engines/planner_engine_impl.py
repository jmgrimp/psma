from __future__ import annotations

from psma_api.engines.planner_v1 import generate_plan_v1
from psma_api.models.planning import PlanRequestV1, PlanResponseV1
from psma_api.ports.planner_engine import PlannerEngine


class DefaultPlannerEngine(PlannerEngine):
    async def generate_plan_v1(self, request: PlanRequestV1) -> PlanResponseV1:
        return await generate_plan_v1(request)
