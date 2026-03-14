"""
Collation endpoints.

All endpoints in this router are protected with JWT (HTTP Bearer) via
`get_current_user`.
"""

import traceback
import csv
import io

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import Response, StreamingResponse
from sqlalchemy.orm import Session

from pydurma_app.enums.output_type import OutputType
from pydurma_app.schemas.schema import CollateCreateResponse, CollationDetailResponse, CollationHistoryItem, CollateRequest
from pydurma_app.services.collation_service import collate_texts, CollationProcessingError
from pydurma_app.models.Collation import Collation
from pydurma_app.dependencies.auth_dependencies import get_current_user, TokenUser
from pydurma_app.db.database import get_db, SessionLocal
from pydurma_app.core.limiter import limiter

router = APIRouter(
    prefix="/collate",
    tags=["Collation"]
)


@router.get("/history", response_model=list[CollationHistoryItem])
@limiter.limit("10/minute")
def get_collation_history(
    request: Request,
    user: TokenUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return a summary list of the current user's collations."""
    collations = (
        db.query(Collation)
        .filter(Collation.user_id == user.id)
        .order_by(Collation.created_at.desc())
        .all()
    )

    return [
        {
            "id": c.id,
            "status": c.status,
            "created_at": c.created_at,
            "output_type": c.output_type
        }
        for c in collations
    ]


@router.get("/{collation_id}", response_model=CollationDetailResponse)
@limiter.limit("20/minute")
def get_collation_by_id(
    request: Request,
    collation_id: int,
    user: TokenUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return a single collation owned by the current user."""
    collation = (
        db.query(Collation)
        .filter(Collation.id == collation_id, Collation.user_id == user.id)
        .first()
    )

    if not collation:
        # Hide existence of other users' collations
        raise HTTPException(status_code=404, detail="Collation not found")

    return {
        "id": collation.id,
        "status": collation.status,
        "input_texts": collation.input_texts,
        "output_type": collation.output_type,
        "result": collation.result,
        "weighted_matrix": collation.weighted_matrix,
        "error_message": collation.error_message,
        "error_trace": collation.error_trace,
        "created_at": collation.created_at,
    }


@router.post("/", response_model=CollateCreateResponse)
@limiter.limit("6/minute")
def create_collate(
    request: Request,
    payload: CollateRequest,
    output_type: OutputType,
    user: TokenUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Collate multiple diplomatic versions and persist the result.

    On success, returns the new collation id and result.
    On failure (pydurma internal error), persists a failure record and returns an error.
    """

    try:
        texts = payload.texts
        result, weighted_matrix = collate_texts(texts, output_type)

        collation = Collation(
            user_id=user.id,
            status="success",
            input_texts=texts,
            output_type=output_type,
            result=result,
            weighted_matrix=weighted_matrix,
            error_message=None,
            error_trace=None,
        )

        db.add(collation)
        db.commit()
        db.refresh(collation)

        return {
            "id": collation.id,
            "status": collation.status,
            "result": result
        }
    except CollationProcessingError as e:
        trace = traceback.format_exc()

        collation = Collation(
            user_id=user.id,
            status="failure",
            input_texts=texts,
            output_type=output_type,
            result=e.result,
            weighted_matrix=e.weighted_matrix,
            error_message=str(e),
            error_trace=trace,
        )

        db.add(collation)
        db.commit()
        db.refresh(collation)

        raise HTTPException(
            status_code=400,
            detail={"collation_id": collation.id, "error": str(e)},
        )
    except Exception as e:
        trace = traceback.format_exc()

        collation = Collation(
            user_id=user.id,
            status="failure",
            input_texts=texts,
            output_type=output_type,
            result=None,
            weighted_matrix=None,
            error_message=str(e),
            error_trace=trace,
        )

        db.add(collation)
        db.commit()
        db.refresh(collation)

        raise HTTPException(
            status_code=500,
            detail={"collation_id": collation.id, "error": "Internal error during collation"},
        )
    

@router.get(
    "/{collation_id}/download",
    response_class=StreamingResponse,
    responses={
        200: {
            "content": {
                "application/octet-stream": {"schema": {"type": "string", "format": "binary"}},
                "text/csv": {"schema": {"type": "string", "format": "binary"}},
            }
        }
    },
)
@limiter.limit("20/minute")
def download(
    request: Request,
    collation_id: int,
    user: TokenUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return a single collation owned by the current user."""
    collation = (
        db.query(Collation)
        .filter(Collation.id == collation_id, Collation.user_id == user.id)
        .first()
    )

    if not collation:
        # Hide existence of other users' collations
        raise HTTPException(status_code=404, detail="Collation not found")


    if collation.output_type == OutputType.TEXT:
        return StreamingResponse(
            iter([collation.result]),
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": f"attachment; filename=collation{collation_id}.txt"
            },
        )
    
    if collation.output_type == OutputType.CSV:

        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerows(collation.result)

        return StreamingResponse(
            iter([buffer.getvalue()]),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=collation{collation_id}.csv"
            },
        )
