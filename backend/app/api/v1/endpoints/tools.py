from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Body
import logging

from app.services.chat_service import chat_service
from app.services.lecture_service import lecture_service
from app.services.slide_service import slide_service

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/save-chat-message")
async def save_chat_message_tool(
    session_id: str = Body(...),
    content: str = Body(...),
    sender: str = Body(...),
    metadata: Optional[Dict[str, Any]] = Body(None)
):
    """
    Tool cho agent: Lưu tin nhắn chat
    """
    try:
        message_id = await chat_service.save_message(session_id, content, sender, metadata)
        return {
            "success": True,
            "message_id": message_id,
            "message": "Tin nhắn đã được lưu thành công"
        }
    except Exception as e:
        logger.error(f"Error in save_chat_message_tool: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get-chat-history")
async def get_chat_history_tool(
    session_id: str = Body(...),
    limit: int = Body(10)
):
    """
    Tool cho agent: Lấy lịch sử chat
    """
    try:
        messages = await chat_service.get_chat_history(session_id, limit)
        return {
            "success": True,
            "messages": messages,
            "count": len(messages)
        }
    except Exception as e:
        logger.error(f"Error in get_chat_history_tool: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search-lectures")
async def search_lectures_tool(
    query: str = Body(...),
    user_id: Optional[str] = Body(None),
    limit: int = Body(5)
):
    """
    Tool cho agent: Tìm kiếm bài giảng
    """
    try:
        lectures = await lecture_service.search_lectures(query, user_id)
        
        # Chuyển đổi sang format đơn giản cho agent
        lecture_data = []
        for lecture in lectures[:limit]:
            lecture_data.append({
                "id": str(lecture.id),
                "title": lecture.title,
                "subject": lecture.subject,
                "description": lecture.description,
                "status": lecture.status,
                "created_at": lecture.created_at.isoformat()
            })
        
        return {
            "success": True,
            "lectures": lecture_data,
            "count": len(lecture_data)
        }
    except Exception as e:
        logger.error(f"Error in search_lectures_tool: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get-lecture-content")
async def get_lecture_content_tool(lecture_id: str = Body(...)):
    """
    Tool cho agent: Lấy nội dung bài giảng
    """
    try:
        lecture = await lecture_service.get_lecture(lecture_id)
        if not lecture:
            return {
                "success": False,
                "error": "Không tìm thấy bài giảng"
            }
        
        return {
            "success": True,
            "lecture": {
                "id": str(lecture.id),
                "title": lecture.title,
                "subject": lecture.subject,
                "content": lecture.content,
                "requirements": lecture.requirements,
                "status": lecture.status
            }
        }
    except Exception as e:
        logger.error(f"Error in get_lecture_content_tool: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search-slides")
async def search_slides_tool(
    query: str = Body(...),
    user_id: Optional[str] = Body(None),
    limit: int = Body(5)
):
    """
    Tool cho agent: Tìm kiếm slides
    """
    try:
        slides = await slide_service.search_slides(query, user_id)
        
        # Chuyển đổi sang format đơn giản cho agent
        slide_data = []
        for slide in slides[:limit]:
            slide_data.append({
                "id": str(slide.id),
                "title": slide.title,
                "subject": slide.subject,
                "description": slide.description,
                "slide_count": slide.slide_count,
                "status": slide.status,
                "created_at": slide.created_at.isoformat()
            })
        
        return {
            "success": True,
            "slides": slide_data,
            "count": len(slide_data)
        }
    except Exception as e:
        logger.error(f"Error in search_slides_tool: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get-slide-content")
async def get_slide_content_tool(slide_id: str = Body(...)):
    """
    Tool cho agent: Lấy nội dung slides
    """
    try:
        slide = await slide_service.get_slide(slide_id)
        if not slide:
            return {
                "success": False,
                "error": "Không tìm thấy slide"
            }
        
        return {
            "success": True,
            "slide": {
                "id": str(slide.id),
                "title": slide.title,
                "subject": slide.subject,
                "slides": slide.slides,
                "slide_count": slide.slide_count,
                "requirements": slide.requirements,
                "status": slide.status
            }
        }
    except Exception as e:
        logger.error(f"Error in get_slide_content_tool: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create-lecture-draft")
async def create_lecture_draft_tool(
    title: str = Body(...),
    subject: str = Body(...),
    requirements: str = Body(...),
    user_id: Optional[str] = Body(None),
    grade: Optional[str] = Body(None),
    description: Optional[str] = Body(None)
):
    """
    Tool cho agent: Tạo draft bài giảng nhanh
    """
    try:
        from app.models.lecture import LectureCreateRequest
        
        request = LectureCreateRequest(
            title=title,
            subject=subject,
            requirements=requirements,
            user_id=user_id,
            grade=grade,
            description=description
        )
        
        lecture_id = await lecture_service.create_lecture(request)
        
        return {
            "success": True,
            "lecture_id": lecture_id,
            "message": "Draft bài giảng đã được tạo"
        }
    except Exception as e:
        logger.error(f"Error in create_lecture_draft_tool: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create-slide-draft")
async def create_slide_draft_tool(
    title: str = Body(...),
    subject: str = Body(...),
    requirements: str = Body(...),
    user_id: Optional[str] = Body(None),
    presentation_type: Optional[str] = Body(None),
    duration: Optional[int] = Body(None),
    description: Optional[str] = Body(None)
):
    """
    Tool cho agent: Tạo draft slide nhanh
    """
    try:
        from app.models.slide import SlideCreateRequest
        
        request = SlideCreateRequest(
            title=title,
            subject=subject,
            requirements=requirements,
            user_id=user_id,
            presentation_type=presentation_type,
            duration=duration,
            description=description
        )
        
        slide_id = await slide_service.create_slide(request)
        
        return {
            "success": True,
            "slide_id": slide_id,
            "message": "Draft slide đã được tạo"
        }
    except Exception as e:
        logger.error(f"Error in create_slide_draft_tool: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get-recent-content")
async def get_recent_content_tool(
    user_id: str = Body(...),
    content_type: str = Body(...),  # "lectures" or "slides"
    limit: int = Body(5)
):
    """
    Tool cho agent: Lấy nội dung gần đây của user
    """
    try:
        if content_type == "lectures":
            lectures, _ = await lecture_service.get_lectures(user_id, 1, limit)
            content_data = [
                {
                    "id": str(lecture.id),
                    "title": lecture.title,
                    "subject": lecture.subject,
                    "status": lecture.status,
                    "created_at": lecture.created_at.isoformat()
                }
                for lecture in lectures
            ]
        elif content_type == "slides":
            slides, _ = await slide_service.get_slides(user_id, 1, limit)
            content_data = [
                {
                    "id": str(slide.id),
                    "title": slide.title,
                    "subject": slide.subject,
                    "slide_count": slide.slide_count,
                    "status": slide.status,
                    "created_at": slide.created_at.isoformat()
                }
                for slide in slides
            ]
        else:
            raise HTTPException(status_code=400, detail="content_type phải là 'lectures' hoặc 'slides'")
        
        return {
            "success": True,
            "content_type": content_type,
            "content": content_data,
            "count": len(content_data)
        }
    except Exception as e:
        logger.error(f"Error in get_recent_content_tool: {e}")
        raise HTTPException(status_code=500, detail=str(e))
