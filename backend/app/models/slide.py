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
            core_schema.str_schema(),
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

class SlideContent(BaseModel):
    title: str
    content: str
    slide_type: str = "content"  # title, content, image, chart, conclusion
    notes: Optional[str] = None

class Slide(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    user_id: Optional[str] = None
    title: str
    subject: str
    presentation_type: Optional[str] = None  # lecture, workshop, seminar, conference
    duration: Optional[int] = None  # minutes
    description: Optional[str] = None
    requirements: str
    slides: Optional[List[SlideContent]] = []
    slide_count: int = 0
    status: str = "draft"  # draft, completed, published
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    source_lecture_id: Optional[str] = None  # If created from lecture
    metadata: Optional[dict] = {}
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

# Request/Response models
class SlideCreateRequest(BaseModel):
    title: str
    subject: str
    presentation_type: Optional[str] = None
    duration: Optional[int] = None
    description: Optional[str] = None
    requirements: str
    user_id: Optional[str] = None

class SlideUpdateRequest(BaseModel):
    title: Optional[str] = None
    subject: Optional[str] = None
    presentation_type: Optional[str] = None
    duration: Optional[int] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    slides: Optional[List[SlideContent]] = None
    status: Optional[str] = None

class SlideFromLectureRequest(BaseModel):
    lecture_id: str
    include_intro: bool = True
    include_conclusion: bool = True
    include_questions: bool = False
    slide_style: str = "professional"  # professional, creative, minimal
    user_id: Optional[str] = None

class SlideResponse(BaseModel):
    id: str
    title: str
    subject: str
    presentation_type: Optional[str] = None
    duration: Optional[int] = None
    description: Optional[str] = None
    requirements: str
    slides: Optional[List[SlideContent]] = []
    slide_count: int
    status: str
    created_at: datetime
    updated_at: datetime
    source_lecture_id: Optional[str] = None

class SlideListResponse(BaseModel):
    slides: List[SlideResponse]
    total_count: int
    page: int = 1
    per_page: int = 20

class SlideGenerationRequest(BaseModel):
    title: str
    subject: str
    presentation_type: Optional[str] = None
    duration: Optional[int] = None
    requirements: str
    user_preferences: Optional[dict] = {}

class SlideExportRequest(BaseModel):
    slide_id: str
    format: str = "pptx"  # pptx, pdf
    template: Optional[str] = "default"
