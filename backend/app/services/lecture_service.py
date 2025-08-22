from typing import Optional, List, Tuple
from datetime import datetime
from bson import ObjectId
import httpx
import logging

from app.db.database import get_database
from app.models.lecture import Lecture, LectureCreateRequest, LectureUpdateRequest, LectureGenerationRequest
from app.core.config import settings

logger = logging.getLogger(__name__)

class LectureService:
    def __init__(self):
        self.agent_url = settings.AGENT_MAIN_URL
    
    async def create_lecture(self, request: LectureCreateRequest) -> str:
        """Tạo bài giảng mới và gọi agent để sinh nội dung"""
        db = await get_database()
        
        # Tạo lecture record
        lecture = Lecture(
            user_id=request.user_id,
            title=request.title,
            subject=request.subject,
            grade=request.grade,
            description=request.description,
            requirements=request.requirements,
            status="generating"  # Đang tạo nội dung
        )
        
        result = await db.lectures.insert_one(lecture.model_dump(by_alias=True))
        lecture_id = str(result.inserted_id)
        
        try:
            # Gọi agent để sinh nội dung bài giảng
            content = await self._generate_lecture_content(request)
            
            # Cập nhật nội dung và status
            await db.lectures.update_one(
                {"_id": ObjectId(lecture_id)},
                {
                    "$set": {
                        "content": content,
                        "status": "completed",
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
        except Exception as e:
            logger.error(f"Error generating lecture content: {e}")
            # Cập nhật status thành error
            await db.lectures.update_one(
                {"_id": ObjectId(lecture_id)},
                {
                    "$set": {
                        "status": "error",
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            raise
        
        return lecture_id
    
    async def get_lecture(self, lecture_id: str) -> Optional[Lecture]:
        """Lấy chi tiết bài giảng"""
        db = await get_database()
        
        try:
            lecture_data = await db.lectures.find_one({"_id": ObjectId(lecture_id)})
            if lecture_data:
                return Lecture(**lecture_data)
            return None
        except Exception as e:
            logger.error(f"Error getting lecture {lecture_id}: {e}")
            return None
    
    async def get_lectures(self, user_id: Optional[str] = None, page: int = 1, per_page: int = 20) -> Tuple[List[Lecture], int]:
        """Lấy danh sách bài giảng với phân trang"""
        db = await get_database()
        
        try:
            # Tạo filter
            filter_query = {}
            if user_id:
                filter_query["user_id"] = user_id
            
            # Đếm tổng số
            total_count = await db.lectures.count_documents(filter_query)
            
            # Lấy dữ liệu với phân trang
            skip = (page - 1) * per_page
            cursor = db.lectures.find(filter_query).sort("created_at", -1).skip(skip).limit(per_page)
            
            lectures = []
            async for lecture_data in cursor:
                lectures.append(Lecture(**lecture_data))
            
            return lectures, total_count
            
        except Exception as e:
            logger.error(f"Error getting lectures: {e}")
            return [], 0
    
    async def update_lecture(self, lecture_id: str, request: LectureUpdateRequest) -> bool:
        """Cập nhật bài giảng"""
        db = await get_database()
        
        try:
            # Tạo update data
            update_data = {}
            if request.title is not None:
                update_data["title"] = request.title
            if request.subject is not None:
                update_data["subject"] = request.subject
            if request.grade is not None:
                update_data["grade"] = request.grade
            if request.description is not None:
                update_data["description"] = request.description
            if request.requirements is not None:
                update_data["requirements"] = request.requirements
            if request.content is not None:
                update_data["content"] = request.content
            if request.status is not None:
                update_data["status"] = request.status
            
            update_data["updated_at"] = datetime.utcnow()
            
            result = await db.lectures.update_one(
                {"_id": ObjectId(lecture_id)},
                {"$set": update_data}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error updating lecture {lecture_id}: {e}")
            return False
    
    async def delete_lecture(self, lecture_id: str) -> bool:
        """Xóa bài giảng"""
        db = await get_database()
        
        try:
            result = await db.lectures.delete_one({"_id": ObjectId(lecture_id)})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting lecture {lecture_id}: {e}")
            return False
    
    async def search_lectures(self, query: str, user_id: Optional[str] = None) -> List[Lecture]:
        """Tìm kiếm bài giảng"""
        db = await get_database()
        
        try:
            # Tạo filter
            filter_query = {
                "$or": [
                    {"title": {"$regex": query, "$options": "i"}},
                    {"subject": {"$regex": query, "$options": "i"}},
                    {"description": {"$regex": query, "$options": "i"}}
                ]
            }
            
            if user_id:
                filter_query["user_id"] = user_id
            
            cursor = db.lectures.find(filter_query).sort("created_at", -1).limit(20)
            
            lectures = []
            async for lecture_data in cursor:
                lectures.append(Lecture(**lecture_data))
            
            return lectures
            
        except Exception as e:
            logger.error(f"Error searching lectures: {e}")
            return []
    
    async def _generate_lecture_content(self, request: LectureCreateRequest) -> str:
        """Gọi agent để sinh nội dung bài giảng"""
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                payload = LectureGenerationRequest(
                    title=request.title,
                    subject=request.subject,
                    grade=request.grade,
                    requirements=request.requirements
                ).model_dump()
                
                response = await client.post(
                    f"{self.agent_url}/generate/lecture",
                    json=payload
                )
                response.raise_for_status()
                
                result = response.json()
                return result.get("content", "")
                
        except httpx.RequestError as e:
            logger.error(f"Error calling agent for lecture generation: {e}")
            raise Exception("Không thể kết nối tới dịch vụ sinh nội dung")
        except Exception as e:
            logger.error(f"Unexpected error generating lecture: {e}")
            raise Exception("Đã xảy ra lỗi khi sinh nội dung bài giảng")

# Singleton instance
lecture_service = LectureService()
