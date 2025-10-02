#src/app/schemas/
from typing import Optional, Literal, List, Dict, Any
from pydantic import BaseModel, Field

TimeOrder = Literal["asc", "desc"]

class Page(BaseModel):
    limit: int = Field(50, ge=1, le=200)
    offset: int = Field(0, ge=0)

class ApiError(BaseModel):
    error_code: str
    message: str
    details: Optional[Dict[str, Any]] = None