from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class CommonModelAttributes(SQLModel):
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    is_active: bool = Field(default=True)
    is_deleted: bool = Field(default=False)
    deleted_at: Optional[datetime] = Field(default_factory=None, nullable=True)
