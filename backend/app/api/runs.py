from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import current_user
from app.db.models import Run, User
from app.db.session import get_db
from app.queue import get_queue

router = APIRouter(prefix="/api/runs", tags=["runs"])

TERMINAL = {"completed", "failed", "cancelled"}


class RunCreate(BaseModel):
    question: str = Field(min_length=10, max_length=4000)
    budget_usd: float = Field(default=1.0, gt=0, le=100)
    run_experiments: bool = True


class RunOut(BaseModel):
    id: str
    question: str
    status: str
    phase: str
    budget_usd: float
    cost_usd: float
    report_md: str | None
    error: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


async def _get_owned_run(run_id: str, user: User, db: AsyncSession) -> Run:
    run = await db.get(Run, run_id)
    if run is None or run.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Run not found")
    return run


@router.post("", response_model=RunOut, status_code=201)
async def create_run(
    body: RunCreate,
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_db),
    queue=Depends(get_queue),
) -> Run:
    if body.budget_usd > user.budget_usd:
        raise HTTPException(status.HTTP_402_PAYMENT_REQUIRED, f"Budget exceeds your remaining ${user.budget_usd:.2f}")
    run = Run(
        user_id=user.id,
        question=body.question,
        budget_usd=body.budget_usd,
        config={"run_experiments": body.run_experiments},
    )
    db.add(run)
    await db.commit()
    await db.refresh(run)
    await queue.enqueue_job("execute_run", run.id, _job_id=f"run:{run.id}")
    return run


@router.get("", response_model=list[RunOut])
async def list_runs(user: User = Depends(current_user), db: AsyncSession = Depends(get_db)) -> list[Run]:
    result = await db.scalars(select(Run).where(Run.user_id == user.id).order_by(Run.created_at.desc()).limit(100))
    return list(result)


@router.get("/{run_id}", response_model=RunOut)
async def get_run(run_id: str, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)) -> Run:
    return await _get_owned_run(run_id, user, db)


@router.post("/{run_id}/cancel", response_model=RunOut)
async def cancel_run(run_id: str, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)) -> Run:
    run = await _get_owned_run(run_id, user, db)
    if run.status not in TERMINAL:
        run.status = "cancelled"
        await db.commit()
        await db.refresh(run)
    return run
