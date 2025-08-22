import httpx
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class BackendTools:
    """Tools để gọi vào backend API"""
    
    def __init__(self, backend_url: str):
        self.backend_url = backend_url
    
    async def save_chat_message(self, session_id: str, content: str, sender: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """Lưu tin nhắn chat"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.backend_url}/tools/save-chat-message",
                    json={
                        "session_id": session_id,
                        "content": content,
                        "sender": sender,
                        "metadata": metadata or {}
                    }
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error saving chat message: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_chat_history(self, session_id: str, limit: int = 10) -> Dict[str, Any]:
        """Lấy lịch sử chat"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.backend_url}/tools/get-chat-history",
                    json={
                        "session_id": session_id,
                        "limit": limit
                    }
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error getting chat history: {e}")
            return {"success": False, "error": str(e)}
    
    async def search_lectures(self, query: str, user_id: Optional[str] = None, limit: int = 5) -> Dict[str, Any]:
        """Tìm kiếm bài giảng"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.backend_url}/tools/search-lectures",
                    json={
                        "query": query,
                        "user_id": user_id,
                        "limit": limit
                    }
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error searching lectures: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_lecture_content(self, lecture_id: str) -> Dict[str, Any]:
        """Lấy nội dung bài giảng"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.backend_url}/tools/get-lecture-content",
                    json={"lecture_id": lecture_id}
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error getting lecture content: {e}")
            return {"success": False, "error": str(e)}
    
    async def search_slides(self, query: str, user_id: Optional[str] = None, limit: int = 5) -> Dict[str, Any]:
        """Tìm kiếm slides"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.backend_url}/tools/search-slides",
                    json={
                        "query": query,
                        "user_id": user_id,
                        "limit": limit
                    }
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error searching slides: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_slide_content(self, slide_id: str) -> Dict[str, Any]:
        """Lấy nội dung slides"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.backend_url}/tools/get-slide-content",
                    json={"slide_id": slide_id}
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error getting slide content: {e}")
            return {"success": False, "error": str(e)}
    
    async def create_lecture_draft(self, 
                                  title: str, 
                                  subject: str, 
                                  requirements: str,
                                  user_id: Optional[str] = None,
                                  grade: Optional[str] = None,
                                  description: Optional[str] = None) -> Dict[str, Any]:
        """Tạo draft bài giảng"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.backend_url}/tools/create-lecture-draft",
                    json={
                        "title": title,
                        "subject": subject,
                        "requirements": requirements,
                        "user_id": user_id,
                        "grade": grade,
                        "description": description
                    }
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error creating lecture draft: {e}")
            return {"success": False, "error": str(e)}
    
    async def create_slide_draft(self,
                               title: str,
                               subject: str,
                               requirements: str,
                               user_id: Optional[str] = None,
                               presentation_type: Optional[str] = None,
                               duration: Optional[int] = None,
                               description: Optional[str] = None) -> Dict[str, Any]:
        """Tạo draft slide"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.backend_url}/tools/create-slide-draft",
                    json={
                        "title": title,
                        "subject": subject,
                        "requirements": requirements,
                        "user_id": user_id,
                        "presentation_type": presentation_type,
                        "duration": duration,
                        "description": description
                    }
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error creating slide draft: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_recent_content(self, user_id: str, content_type: str, limit: int = 5) -> Dict[str, Any]:
        """Lấy nội dung gần đây của user"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.backend_url}/tools/get-recent-content",
                    json={
                        "user_id": user_id,
                        "content_type": content_type,
                        "limit": limit
                    }
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error getting recent content: {e}")
            return {"success": False, "error": str(e)}
