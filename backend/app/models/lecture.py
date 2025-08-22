from typing import Optional, List, Any
from pydantic import BaseModel, Field
from datetime import datetime
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        from pydantic_core import core_schema
        return core_schema.no_info_after_validator_function(
            cls.validate,
            core_schema.union_schema([
                core_schema.is_instance_schema(ObjectId),
                core_schema.str_schema()
            ]),
            serialization=core_schema.to_string_ser_schema()
        )

    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return v
        if isinstance(v, str):
            if ObjectId.is_valid(v):
                return ObjectId(v)
        raise ValueError("Invalid objectid")

class Lecture(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    user_id: Optional[str] = None
    title: str
    subject: str
    grade: Optional[str] = None  # elementary, middle, high, university
    description: Optional[str] = None
    requirements: str
    content: Optional[Any] = None  # Can be string or dict for structured content
    status: str = "draft"  # draft, completed, published
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[dict] = {}
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

# Request/Response models
class LectureCreateRequest(BaseModel):
    title: str
    subject: str
    grade: Optional[str] = None
    description: Optional[str] = None
    requirements: str
    user_id: Optional[str] = None

class LectureUpdateRequest(BaseModel):
    title: Optional[str] = None
    subject: Optional[str] = None
    grade: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    content: Optional[Any] = None  # Can be string or dict for structured content
    status: Optional[str] = None

class LectureResponse(BaseModel):
    id: str
    title: str
    subject: str
    grade: Optional[str] = None
    description: Optional[str] = None
    requirements: str
    content: Optional[Any] = None  # Can be string or dict for structured content
    status: str
    created_at: datetime
    updated_at: datetime

class LectureListResponse(BaseModel):
    lectures: List[LectureResponse]
    total_count: int
    page: int = 1
    per_page: int = 20

class LectureGenerationRequest(BaseModel):
    title: str
    subject: str
    grade: Optional[str] = None
    requirements: str
    user_preferences: Optional[dict] = {}
