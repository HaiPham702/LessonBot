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

class ChatMessage(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    session_id: str
    content: str
    sender: str  # "user" or "bot"
    message_type: Optional[str] = "text"  # text, image, file, etc.
    metadata: Optional[dict] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class ChatSession(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    user_id: Optional[str] = None
    title: Optional[str] = "New Chat"
    status: str = "active"  # active, archived, deleted
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[dict] = {}
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

# Request/Response models
class ChatMessageRequest(BaseModel):
    message: str
    sessionId: Optional[str] = None
    user_id: Optional[str] = None

class ChatMessageResponse(BaseModel):
    reply: str
    session_id: str
    message_id: str
    metadata: Optional[dict] = {}

class ChatSessionResponse(BaseModel):
    session_id: str
    title: str
    created_at: datetime
    message_count: int = 0

class ChatHistoryResponse(BaseModel):
    session_id: str
    messages: List[dict]
    total_count: int
