"""Settings database model."""
from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database.base import Base


class SettingModel(Base):
    """Settings key-value store model."""

    __tablename__ = "settings"
    __table_args__ = (
        CheckConstraint(
            "value_type IN ('string', 'integer', 'boolean', 'json')",
            name="valid_value_type",
        ),
    )

    # Override default id with key as primary
    key: Mapped[str] = mapped_column(String(100), primary_key=True)
    value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    value_type: Mapped[str] = mapped_column(String(20), default="string")
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    updated_by: Mapped[Optional[UUID]] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("admins.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Remove id from base class for this model
    id = None  # type: ignore

    def get_typed_value(self) -> Any:
        """Get value with proper type conversion."""
        if self.value is None:
            return None

        if self.value_type == "integer":
            return int(self.value)
        elif self.value_type == "boolean":
            return self.value.lower() in ("true", "1", "yes")
        elif self.value_type == "json":
            import json
            return json.loads(self.value)
        return self.value

    def __repr__(self) -> str:
        return f"<Setting {self.key}={self.value}>"
