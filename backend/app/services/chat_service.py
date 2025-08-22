from typing import Optional, List
from datetime import datetime
from bson import ObjectId
import httpx
import logging

from app.db.database import get_database
from app.models.chat import ChatMessage, ChatSession, ChatMessageRequest, ChatMessageResponse
from app.core.config import settings

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self):
        self.agent_url = settings.AGENT_MAIN_URL
    
    async def create_session(self, user_id: Optional[str] = None) -> str:
        """Tạo session chat mới"""
        db = await get_database()
        
        session = ChatSession(
            user_id=user_id,
            title="New Chat",
            status="active"
        )
        
        result = await db.chat_sessions.insert_one(session.model_dump(by_alias=True))
        return str(result.inserted_id)
    
    async def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Lấy thông tin session"""
        db = await get_database()
        
        try:
            session_data = await db.chat_sessions.find_one({"_id": ObjectId(session_id)})
            if session_data:
                return ChatSession(**session_data)
            return None
        except Exception as e:
            logger.error(f"Error getting session {session_id}: {e}")
            return None
    
    async def save_message(self, session_id: str, content: str, sender: str, metadata: dict = None, message_type: str = "text") -> str:
        """Lưu tin nhắn vào database"""
        db = await get_database()
        
        # Determine message type from metadata if not provided
        if metadata and metadata.get("type") == "lecture":
            message_type = "lecture"
        
        message = ChatMessage(
            session_id=session_id,
            content=content,
            sender=sender,
            message_type=message_type,
            metadata=metadata or {}
        )
        
        result = await db.chat_messages.insert_one(message.model_dump(by_alias=True))
        
        # Cập nhật session updated_at
        await db.chat_sessions.update_one(
            {"_id": ObjectId(session_id)},
            {"$set": {"updated_at": datetime.utcnow()}}
        )
        
        return str(result.inserted_id)
    
    async def get_chat_history(self, session_id: str, limit: int = 50) -> List[dict]:
        """Lấy lịch sử chat của session"""
        db = await get_database()
        
        try:
            cursor = db.chat_messages.find(
                {"session_id": session_id}
            ).sort("created_at", 1).limit(limit)
            
            messages = []
            async for message in cursor:
                # Convert ObjectId to string
                message["id"] = str(message["_id"])
                del message["_id"]
                
                # Convert datetime to ISO string to make it JSON serializable
                if "created_at" in message and message["created_at"]:
                    message["created_at"] = message["created_at"].isoformat()
                
                # Ensure all fields are JSON serializable
                clean_message = {
                    "id": message["id"],
                    "session_id": message.get("session_id", ""),
                    "content": message.get("content", ""),
                    "sender": message.get("sender", ""),
                    "message_type": message.get("message_type", "text"),
                    "metadata": message.get("metadata", {}),
                    "created_at": message.get("created_at", "")
                }
                messages.append(clean_message)
            
            return messages
        except Exception as e:
            logger.error(f"Error getting chat history for session {session_id}: {e}")
            return []
    
    async def get_user_sessions(self, user_id: str, limit: int = 20) -> List[dict]:
        """Lấy danh sách sessions của user"""
        db = await get_database()
        
        try:
            cursor = db.chat_sessions.find(
                {"user_id": user_id, "status": "active"}
            ).sort("updated_at", -1).limit(limit)
            
            sessions = []
            async for session in cursor:
                # Đếm số tin nhắn
                message_count = await db.chat_messages.count_documents(
                    {"session_id": str(session["_id"])}
                )
                
                session_data = {
                    "session_id": str(session["_id"]),
                    "title": session.get("title", "New Chat"),
                    "created_at": session["created_at"],
                    "updated_at": session["updated_at"],
                    "message_count": message_count
                }
                sessions.append(session_data)
            
            return sessions
        except Exception as e:
            logger.error(f"Error getting user sessions for {user_id}: {e}")
            return []
    
    async def process_message(self, request: ChatMessageRequest) -> ChatMessageResponse:
        """Xử lý tin nhắn từ user và gọi agent"""
        try:
            # Tạo session mới nếu chưa có
            session_id = request.sessionId
            if not session_id:
                session_id = await self.create_session(request.user_id)
            
            # Lưu tin nhắn user
            user_message_id = await self.save_message(
                session_id=session_id,
                content=request.message,
                sender="user"
            )
            
            # Lấy lịch sử chat để context
            chat_history = await self.get_chat_history(session_id)
            
            # Gọi agent để xử lý
            agent_response = await self._call_agent(request.message, chat_history)
            
            # Lưu phản hồi của bot
            bot_message_id = await self.save_message(
                session_id=session_id,
                content=agent_response["reply"],
                sender="bot",
                metadata=agent_response.get("metadata", {})
            )
            
            # Cập nhật title session nếu là tin nhắn đầu tiên
            if len(chat_history) == 0:
                await self._update_session_title(session_id, request.message)
            
            return ChatMessageResponse(
                reply=agent_response["reply"],
                session_id=session_id,
                message_id=bot_message_id,
                metadata=agent_response.get("metadata", {})
            )
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            # Lưu thông báo lỗi
            if session_id:
                await self.save_message(
                    session_id=session_id,
                    content="Xin lỗi, có lỗi xảy ra khi xử lý tin nhắn của bạn.",
                    sender="bot",
                    metadata={"error": True}
                )
            
            raise
    
    async def _call_agent(self, message: str, chat_history: List[dict]) -> dict:
        """Gọi agent để xử lý tin nhắn"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                payload = {
                    "message": message,
                    "chat_history": chat_history[-10:]  # Lấy 10 tin nhắn gần nhất
                }
                
                response = await client.post(
                    f"{self.agent_url}/process",
                    json=payload
                )
                response.raise_for_status()
                
                return response.json()
                
        except httpx.RequestError as e:
            logger.error(f"Error calling agent: {e.message}")
            return {
                "reply": "Xin lỗi, tôi đang gặp sự cố kỹ thuật. Vui lòng thử lại sau.",
                "metadata": {"error": True, "error_type": "agent_unavailable"}
            }
        except Exception as e:
            logger.error(f"Unexpected error calling agent: {e}")
            return {
                "reply": "Đã xảy ra lỗi không mong muốn. Vui lòng thử lại.",
                "metadata": {"error": True, "error_type": "unexpected"}
            }
    
    async def _update_session_title(self, session_id: str, first_message: str):
        """Cập nhật title session dựa trên tin nhắn đầu tiên"""
        db = await get_database()
        
        # Tạo title ngắn gọn từ tin nhắn đầu tiên
        title = first_message[:50] + "..." if len(first_message) > 50 else first_message
        
        await db.chat_sessions.update_one(
            {"_id": ObjectId(session_id)},
            {"$set": {"title": title}}
        )

    async def get_user_sessions(self, user_id: str, limit: int = 20) -> List[dict]:
        """Lấy danh sách sessions của user"""
        try:
            db = await get_database()
            
            # Aggregation pipeline để lấy sessions cùng với message count
            pipeline = [
                {
                    "$match": {
                        "user_id": user_id,
                        "status": {"$ne": "deleted"}  # Không lấy sessions đã xóa
                    }
                },
                {
                    "$lookup": {
                        "from": "chat_messages",
                        "localField": "_id",
                        "foreignField": "session_id",
                        "as": "messages"
                    }
                },
                {
                    "$addFields": {
                        "message_count": {"$size": "$messages"},
                        "session_id": {"$toString": "$_id"}
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
                {
                    "$sort": {"updated_at": -1}
                },
                {
                    "$limit": limit
                }
            ]
            
            sessions = []
            async for session in db.chat_sessions.aggregate(pipeline):
                sessions.append(session)
            
            return sessions
            
        except Exception as e:
            logger.error(f"Error getting user sessions: {e}")
            raise

    async def get_session(self, session_id: str) -> Optional[dict]:
        """Lấy thông tin session"""
        try:
            db = await get_database()
            session = await db.chat_sessions.find_one({"_id": ObjectId(session_id)})
            
            if session:
                session["_id"] = str(session["_id"])
                return session
            return None
            
        except Exception as e:
            logger.error(f"Error getting session: {e}")
            raise

    async def delete_session(self, session_id: str) -> bool:
        """Xóa session (chuyển status thành deleted)"""
        try:
            db = await get_database()
            from datetime import datetime
            
            result = await db.chat_sessions.update_one(
                {"_id": ObjectId(session_id)},
                {"$set": {"status": "deleted", "updated_at": datetime.utcnow()}}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error deleting session: {e}")
            raise

# Singleton instance
chat_service = ChatService()
