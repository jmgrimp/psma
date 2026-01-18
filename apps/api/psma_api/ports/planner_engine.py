from __future__ import annotations

from typing import Protocol

from psma_api.models.planning import PlanRequestV1, PlanResponseV1


class PlannerEngine(Protocol):
    async def generate_plan_v1(self, request: PlanRequestV1) -> PlanResponseV1: ...
