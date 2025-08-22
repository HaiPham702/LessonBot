from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
import logging

from app.models.chat import ChatMessageRequest, ChatMessageResponse, ChatHistoryResponse, ChatSessionResponse
from app.services.chat_service import chat_service

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/message", response_model=ChatMessageResponse)
async def send_message(request: ChatMessageRequest):
    """
    Gửi tin nhắn chat và nhận phản hồi từ AI
    """
    try:
        response = await chat_service.process_message(request)
        return response
    except Exception as e:
        logger.error(f"Error in send_message: {e}")
        raise HTTPException(status_code=500, detail="Có lỗi xảy ra khi xử lý tin nhắn")

@router.post("/session")
async def create_chat_session(user_id: Optional[str] = "anonymous"):
    """
    Tạo session chat mới
    """
    try:
        session_id = await chat_service.create_session(user_id)
        from datetime import datetime
        
        return {
            "id": session_id,
            "title": "Chat mới",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "message_count": 0,
            "message": "Session created successfully"
        }
    except Exception as e:
        logger.error(f"Error creating chat session: {e}")
        raise HTTPException(status_code=500, detail="Không thể tạo session chat")

@router.get("/history/{session_id}", response_model=ChatHistoryResponse)
async def get_chat_history(
    session_id: str,
    limit: int = Query(50, ge=1, le=100, description="Số lượng tin nhắn muốn lấy")
):
    """
    Lấy lịch sử chat của một session
    """
    try:
        # Kiểm tra session tồn tại
        session = await chat_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Không tìm thấy session")
        
        messages = await chat_service.get_chat_history(session_id, limit)
        
        return ChatHistoryResponse(
            session_id=session_id,
            messages=messages,
            total_count=len(messages)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting chat history: {e}")
        raise HTTPException(status_code=500, detail="Không thể lấy lịch sử chat")

@router.get("/sessions")
async def get_chat_sessions(
    limit: int = Query(20, ge=1, le=50, description="Số lượng session muốn lấy")
):
    """
    Tạm thời: Lấy tất cả sessions (không lọc theo user)
    """
    try:
        from app.db.database import get_database

        db = await get_database()
        pipeline = [
            {"$match": {"status": {"$ne": "deleted"}}},
            {"$addFields": {"session_id": {"$toString": "$_id"}}},
            {
                "$lookup": {
                    "from": "chat_messages",
                    "localField": "session_id",
                    "foreignField": "session_id",
                    "as": "messages"
                }
            },
            {
                "$addFields": {
                    "message_count": {"$size": "$messages"}
                }
            },
            {
                "$project": {
                    "session_id": 1,
                    "title": 1,
                    "created_at": 1,
                    "updated_at": 1,
                    "message_count": 1
                }
            },
            {"$sort": {"updated_at": -1}},
            {"$limit": limit}
        ]

        results = []
        async for s in db.chat_sessions.aggregate(pipeline):
            results.append(s)

        return {
            "sessions": [
                {
                    "id": s["session_id"],
                    "title": s.get("title") or "Chat không tiêu đề",
                    "created_at": s.get("created_at").isoformat() if s.get("created_at") else None,
                    "updated_at": s.get("updated_at").isoformat() if s.get("updated_at") else None,
                    "message_count": s.get("message_count", 0)
                }
                for s in results
            ]
        }
    except Exception as e:
        logger.error(f"Error getting chat sessions: {e}")
        raise HTTPException(status_code=500, detail="Không thể lấy danh sách sessions")

@router.delete("/session/{session_id}")
async def delete_chat_session(session_id: str):
    """
    Xóa một session chat (chuyển status thành deleted)
    """
    try:
        # Kiểm tra session tồn tại
        session = await chat_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Không tìm thấy session")
        
        # Xóa session
        success = await chat_service.delete_session(session_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Không thể xóa session")
        
        return {"message": "Session đã được xóa thành công"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting chat session: {e}")
        raise HTTPException(status_code=500, detail="Không thể xóa session")
