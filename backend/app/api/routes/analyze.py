from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.analysis import AnalyzeRequest, AnalyzeResponse
from app.services.analysis_service import AnalysisService

router = APIRouter(prefix="/analyze", tags=["Analysis"])
analysis_service = AnalysisService()


@router.post("", response_model=AnalyzeResponse, summary="Analyze Python source code statically")
def analyze_code(
    payload: AnalyzeRequest,
    db: Session = Depends(get_db)
):
    if not payload.code.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Source code cannot be empty."
        )

    try:
        result = analysis_service.analyze_code(payload, db=db)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected internal error occurred during static analysis: {str(e)}"
        )
