"""
Collation endpoints.

All endpoints in this router are protected with JWT (HTTP Bearer) via
`get_current_user`.
"""

import traceback

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from pydurma_app.schemas.schema import CollateCreateResponse, CollationDetailResponse, CollationHistoryItem, CollateRequest
from pydurma_app.services.collation_service import collate_texts, CollationProcessingError
from pydurma_app.models.User import User
from pydurma_app.models.Collation import Collation
from pydurma_app.dependencies.auth_dependencies import get_current_user
from pydurma_app.db.database import get_db, SessionLocal

router = APIRouter(
    prefix="/collate",
    tags=["Collation"]
)


@router.get("/history", response_model=list[CollationHistoryItem])
def get_collation_history(
    user: User = Depends(get_current_user),
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
        }
        for c in collations
    ]


@router.get("/{collation_id}", response_model=CollationDetailResponse)
def get_collation_by_id(
    collation_id: int,
    user: User = Depends(get_current_user),
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
        "input_raw": collation.input_raw,
        "result_text": collation.result_text,
        "weighted_matrix": collation.weighted_matrix,
        "error_message": collation.error_message,
        "error_trace": collation.error_trace,
        "created_at": collation.created_at,
    }


@router.post("/", response_model=CollateCreateResponse)
def create_collate(
    payload: CollateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Collate multiple diplomatic versions and persist the result.

    On success, returns the new collation id and result text.
    On failure (pydurma internal error), persists a failure record and returns an error.
    """

    try:
        texts = payload.texts
        result_text, weighted_matrix = collate_texts(texts)

        collation = Collation(
            user_id=user.id,
            status="success",
            input_texts=texts,
            input_raw=None,
            result_text=result_text,
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
            "result": result_text,
        }
    except CollationProcessingError as e:
        trace = traceback.format_exc()

        collation = Collation(
            user_id=user.id,
            status="failure",
            input_texts=texts,
            input_raw=None,
            result_text=e.result_text,
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
            input_raw=None,
            result_text=None,
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