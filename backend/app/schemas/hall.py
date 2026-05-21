"""Hall schemas — request/response models for hall/classroom management."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator


class HallBase(BaseModel):
    """Base hall fields."""
    hall_number: str = Field(..., min_length=1, max_length=20)
    floor_number: int = Field(..., ge=0, le=20)
    capacity: int = Field(..., gt=0, le=500)
    num_benches: int = Field(..., gt=0, le=500)
    num_rows: int = Field(..., gt=0, le=50)
    num_columns: int = Field(..., gt=0, le=50)

    @field_validator("capacity")
    @classmethod
    def validate_capacity(cls, v, info):
        """Validate that capacity matches row × column layout."""
        if "num_rows" in info.data and "num_columns" in info.data:
            max_capacity = info.data["num_rows"] * info.data["num_columns"]
            if v > max_capacity:
                raise ValueError(
                    f"Capacity ({v}) cannot exceed rows × columns ({max_capacity})"
                )
        return v


class HallCreate(HallBase):
    """Schema for creating a new hall."""
    pass


class HallUpdate(BaseModel):
    """Schema for updating a hall."""
    hall_number: Optional[str] = Field(None, min_length=1, max_length=20)
    floor_number: Optional[int] = Field(None, ge=0, le=20)
    capacity: Optional[int] = Field(None, gt=0, le=500)
    num_benches: Optional[int] = Field(None, gt=0, le=500)
    num_rows: Optional[int] = Field(None, gt=0, le=50)
    num_columns: Optional[int] = Field(None, gt=0, le=50)
    is_enabled: Optional[bool] = None


class HallResponse(HallBase):
    """Schema for hall data in API responses."""
    id: int
    is_enabled: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class HallListResponse(BaseModel):
    """List of halls."""
    halls: List[HallResponse]
    total: int


class HallToggleRequest(BaseModel):
    """Request to enable/disable a hall."""
    is_enabled: bool
