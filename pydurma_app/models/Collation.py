from datetime import datetime, timezone

from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from pydurma_app.db.database import Base


class Collation(Base):
    __tablename__ = "collations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String, nullable=False, default="success")

    # Original input texts (diplomatic versions)
    input_texts = Column(JSONB, nullable=False)

    output_type = Column(Text, nullable=True)

    # Collated critical edition
    result = Column(JSONB, nullable=True)

    # Weighted matrix from Pydurma, stored as JSON (list-of-lists)
    weighted_matrix = Column(JSONB, nullable=True)

    # Error information (only for failures)
    error_message = Column(Text, nullable=True)
    error_trace = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
