import uuid
from typing import Optional
from pydantic import BaseModel, Field

class User(BaseModel):
    user_id: str = Field(default_factory=uuid.uuid4, alias="_id")
    has_labels: bool = False
    activities: Optional[list] = None

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "has_labels": False,
                "activities": []
            }
        }