from typing import Optional, List, Tuple
from datetime import datetime
from bson import ObjectId
import httpx
import logging

from app.db.database import get_database
from app.models.slide import Slide, SlideCreateRequest, SlideUpdateRequest, SlideFromLectureRequest, SlideGenerationRequest
from app.models.lecture import Lecture
from app.core.config import settings

logger = logging.getLogger(__name__)

class SlideService:
    def __init__(self):
        self.agent_url = settings.AGENT_MAIN_URL
    
    async def create_slide(self, request: SlideCreateRequest) -> str:
        """Tạo slide mới và gọi agent để sinh nội dung"""
        db = await get_database()
        
        # Tạo slide record
        slide = Slide(
            user_id=request.user_id,
            title=request.title,
            subject=request.subject,
            presentation_type=request.presentation_type,
            duration=request.duration,
            description=request.description,
            requirements=request.requirements,
            status="generating"  # Đang tạo nội dung
        )
        
        result = await db.slides.insert_one(slide.model_dump(by_alias=True))
        slide_id = str(result.inserted_id)
        
        try:
            # Gọi agent để sinh nội dung slide
            slides_content = await self._generate_slide_content(request)
            
            # Cập nhật nội dung và status
            await db.slides.update_one(
                {"_id": ObjectId(slide_id)},
                {
                    "$set": {
                        "slides": slides_content,
                        "slide_count": len(slides_content),
                        "status": "completed",
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
        except Exception as e:
            logger.error(f"Error generating slide content: {e}")
            # Cập nhật status thành error
            await db.slides.update_one(
                {"_id": ObjectId(slide_id)},
                {
                    "$set": {
                        "status": "error",
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            raise
        
        return slide_id
    
    async def create_slide_from_lecture(self, request: SlideFromLectureRequest) -> str:
        """Tạo slide từ bài giảng có sẵn"""
        db = await get_database()
        
        # Lấy thông tin bài giảng
        lecture_data = await db.lectures.find_one({"_id": ObjectId(request.lecture_id)})
        if not lecture_data:
            raise Exception("Không tìm thấy bài giảng")
        
        lecture = Lecture(**lecture_data)
        
        # Tạo slide record
        slide = Slide(
            user_id=request.user_id,
            title=f"Slide: {lecture.title}",
            subject=lecture.subject,
            presentation_type="lecture",
            description=f"Slide được tạo từ bài giảng: {lecture.title}",
            requirements=f"Tạo slide từ nội dung bài giảng với các tùy chọn: {request.model_dump()}",
            source_lecture_id=request.lecture_id,
            status="generating"
        )
        
        result = await db.slides.insert_one(slide.model_dump(by_alias=True))
        slide_id = str(result.inserted_id)
        
        try:
            # Gọi agent để sinh slide từ lecture
            slides_content = await self._generate_slide_from_lecture(lecture, request)
            
            # Cập nhật nội dung và status
            await db.slides.update_one(
                {"_id": ObjectId(slide_id)},
                {
                    "$set": {
                        "slides": slides_content,
                        "slide_count": len(slides_content),
                        "status": "completed",
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
        except Exception as e:
            logger.error(f"Error generating slide from lecture: {e}")
            # Cập nhật status thành error
            await db.slides.update_one(
                {"_id": ObjectId(slide_id)},
                {
                    "$set": {
                        "status": "error",
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            raise
        
        return slide_id
    
    async def get_slide(self, slide_id: str) -> Optional[Slide]:
        """Lấy chi tiết slide"""
        db = await get_database()
        
        try:
            slide_data = await db.slides.find_one({"_id": ObjectId(slide_id)})
            if slide_data:
                return Slide(**slide_data)
            return None
        except Exception as e:
            logger.error(f"Error getting slide {slide_id}: {e}")
            return None
    
    async def get_slides(self, user_id: Optional[str] = None, page: int = 1, per_page: int = 20) -> Tuple[List[Slide], int]:
        """Lấy danh sách slides với phân trang"""
        db = await get_database()
        
        try:
            # Tạo filter
            filter_query = {}
            if user_id:
                filter_query["user_id"] = user_id
            
            # Đếm tổng số
            total_count = await db.slides.count_documents(filter_query)
            
            # Lấy dữ liệu với phân trang
            skip = (page - 1) * per_page
            cursor = db.slides.find(filter_query).sort("created_at", -1).skip(skip).limit(per_page)
            
            slides = []
            async for slide_data in cursor:
                slides.append(Slide(**slide_data))
            
            return slides, total_count
            
        except Exception as e:
            logger.error(f"Error getting slides: {e}")
            return [], 0
    
    async def update_slide(self, slide_id: str, request: SlideUpdateRequest) -> bool:
        """Cập nhật slide"""
        db = await get_database()
        
        try:
            # Tạo update data
            update_data = {}
            if request.title is not None:
                update_data["title"] = request.title
            if request.subject is not None:
                update_data["subject"] = request.subject
            if request.presentation_type is not None:
                update_data["presentation_type"] = request.presentation_type
            if request.duration is not None:
                update_data["duration"] = request.duration
            if request.description is not None:
                update_data["description"] = request.description
            if request.requirements is not None:
                update_data["requirements"] = request.requirements
            if request.slides is not None:
                update_data["slides"] = [slide.model_dump() for slide in request.slides]
                update_data["slide_count"] = len(request.slides)
            if request.status is not None:
                update_data["status"] = request.status
            
            update_data["updated_at"] = datetime.utcnow()
            
            result = await db.slides.update_one(
                {"_id": ObjectId(slide_id)},
                {"$set": update_data}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error updating slide {slide_id}: {e}")
            return False
    
    async def delete_slide(self, slide_id: str) -> bool:
        """Xóa slide"""
        db = await get_database()
        
        try:
            result = await db.slides.delete_one({"_id": ObjectId(slide_id)})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting slide {slide_id}: {e}")
            return False
    
    async def search_slides(self, query: str, user_id: Optional[str] = None) -> List[Slide]:
        """Tìm kiếm slides"""
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
            
            cursor = db.slides.find(filter_query).sort("created_at", -1).limit(20)
            
            slides = []
            async for slide_data in cursor:
                slides.append(Slide(**slide_data))
            
            return slides
            
        except Exception as e:
            logger.error(f"Error searching slides: {e}")
            return []
    
    async def _generate_slide_content(self, request: SlideCreateRequest) -> List[dict]:
        """Gọi agent để sinh nội dung slide"""
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                payload = SlideGenerationRequest(
                    title=request.title,
                    subject=request.subject,
                    presentation_type=request.presentation_type,
                    duration=request.duration,
                    requirements=request.requirements
                ).model_dump()
                
                response = await client.post(
                    f"{self.agent_url}/generate/slide",
                    json=payload
                )
                response.raise_for_status()
                
                result = response.json()
                return result.get("slides", [])
                
        except httpx.RequestError as e:
            logger.error(f"Error calling agent for slide generation: {e}")
            raise Exception("Không thể kết nối tới dịch vụ sinh nội dung")
        except Exception as e:
            logger.error(f"Unexpected error generating slide: {e}")
            raise Exception("Đã xảy ra lỗi khi sinh nội dung slide")
    
    async def _generate_slide_from_lecture(self, lecture: Lecture, request: SlideFromLectureRequest) -> List[dict]:
        """Gọi agent để sinh slide từ bài giảng"""
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                payload = {
                    "lecture_content": lecture.content,
                    "lecture_title": lecture.title,
                    "lecture_subject": lecture.subject,
                    "include_intro": request.include_intro,
                    "include_conclusion": request.include_conclusion,
                    "include_questions": request.include_questions,
                    "slide_style": request.slide_style
                }
                
                response = await client.post(
                    f"{self.agent_url}/generate/slide-from-lecture",
                    json=payload
                )
                response.raise_for_status()
                
                result = response.json()
                return result.get("slides", [])
                
        except httpx.RequestError as e:
            logger.error(f"Error calling agent for slide from lecture generation: {e}")
            raise Exception("Không thể kết nối tới dịch vụ sinh nội dung")
        except Exception as e:
            logger.error(f"Unexpected error generating slide from lecture: {e}")
            raise Exception("Đã xảy ra lỗi khi sinh slide từ bài giảng")

# Singleton instance
slide_service = SlideService()
