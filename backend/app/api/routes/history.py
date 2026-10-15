from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.db.database import get_db
from app.models.models import AnalysisResult, CodeSubmission
from app.schemas.project import HistoryItemResponse, HistoryDetailResponse

router = APIRouter(prefix="/history", tags=["History"])


@router.get("", response_model=List[HistoryItemResponse], summary="Retrieve analysis history")
def get_history(limit: int = 20, db: Session = Depends(get_db)):
    results = (
        db.query(AnalysisResult)
        .join(CodeSubmission, AnalysisResult.submission_id == CodeSubmission.id)
        .order_by(desc(AnalysisResult.created_at))
        .limit(limit)
        .all()
    )

    items = []
    for r in results:
        sub = r.submission
        snippet = (sub.code[:120] + "...") if sub and len(sub.code) > 120 else (sub.code if sub else "")
        items.append(
            HistoryItemResponse(
                id=r.id,
                submission_id=r.submission_id,
                title=sub.title if sub else "Untitled",
                code_snippet=snippet,
                time_complexity=r.time_complexity,
                space_complexity=r.space_complexity,
                confidence=r.confidence,
                created_at=r.created_at,
            )
        )
    return items


@router.get("/{submission_id}", response_model=HistoryDetailResponse, summary="Retrieve detailed past analysis")
def get_history_detail(submission_id: str, db: Session = Depends(get_db)):
    result = (
        db.query(AnalysisResult)
        .filter(AnalysisResult.submission_id == submission_id)
        .first()
    )
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis result not found."
        )

    sub = result.submission
    return HistoryDetailResponse(
        id=result.id,
        submission_id=result.submission_id,
        title=sub.title if sub else "Untitled",
        code=sub.code if sub else "",
        time_complexity=result.time_complexity,
        space_complexity=result.space_complexity,
        confidence=result.confidence,
        complexity_reasoning=result.complexity_reasoning,
        statistics=result.statistics,
        structure=result.structure,
        graph_data=result.graph_data,
        detected_patterns=result.detected_patterns,
        optimization_suggestions=result.optimization_suggestions,
        created_at=result.created_at,
    )


@router.delete("/{submission_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete an analysis record")
def delete_history_item(submission_id: str, db: Session = Depends(get_db)):
    submission = (
        db.query(CodeSubmission)
        .filter(CodeSubmission.id == submission_id)
        .first()
    )
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found."
        )
    db.delete(submission)
    db.commit()
    return None
