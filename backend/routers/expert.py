from fastapi import APIRouter
from pydantic import BaseModel

from agents import expert_agent
from services import supabase_service

router = APIRouter(prefix="/api/v1/expert", tags=["expert"])


class ContributionRequest(BaseModel):
    contributor_name: str
    contributor_role: str
    years_experience: int
    text: str


@router.post("/contribute")
async def contribute(request: ContributionRequest):
    result = expert_agent.run(
        request.contributor_name,
        request.contributor_role,
        request.years_experience,
        request.text,
    )
    record = {
        "contributor_name": request.contributor_name,
        "contributor_role": request.contributor_role,
        "years_experience": request.years_experience,
        "text": request.text,
        "entities_found": result["entities_found"],
    }
    saved = supabase_service.insert_expert_contribution(record) or record
    return {"contribution": saved, "entities_found": result["entities_found"]}


@router.get("/contributions")
async def list_contributions():
    return supabase_service.get_expert_contributions()
