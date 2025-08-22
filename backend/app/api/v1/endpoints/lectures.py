from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Response
import logging

from app.models.lecture import (
    LectureCreateRequest, 
    LectureUpdateRequest, 
    LectureResponse, 
    LectureListResponse
)
from app.services.lecture_service import lecture_service

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/create", response_model=dict)
async def create_lecture(request: LectureCreateRequest):
    """
    Tạo bài giảng mới
    """
    try:
        lecture_id = await lecture_service.create_lecture(request)
        return {
            "lecture_id": lecture_id,
            "message": "Bài giảng đang được tạo. Vui lòng chờ trong giây lát.",
            "status": "generating"
        }
    except Exception as e:
        logger.error(f"Error creating lecture: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{lecture_id}", response_model=LectureResponse)
async def get_lecture(lecture_id: str):
    """
    Lấy chi tiết bài giảng
    """
    try:
        lecture = await lecture_service.get_lecture(lecture_id)
        if not lecture:
            raise HTTPException(status_code=404, detail="Không tìm thấy bài giảng")
        
        return LectureResponse(
            id=str(lecture.id),
            title=lecture.title,
            subject=lecture.subject,
            grade=lecture.grade,
            description=lecture.description,
            requirements=lecture.requirements,
            content=lecture.content,
            status=lecture.status,
            created_at=lecture.created_at,
            updated_at=lecture.updated_at
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting lecture: {e}")
        raise HTTPException(status_code=500, detail="Không thể lấy thông tin bài giảng")

@router.get("", response_model=LectureListResponse)
async def get_lectures(
    user_id: Optional[str] = Query(None, description="ID của user"),
    page: int = Query(1, ge=1, description="Số trang"),
    per_page: int = Query(20, ge=1, le=50, description="Số bài giảng mỗi trang"),
    search: Optional[str] = Query(None, description="Từ khóa tìm kiếm")
):
    """
    Lấy danh sách bài giảng với phân trang và tìm kiếm
    """
    try:
        if search:
            # Tìm kiếm
            lectures = await lecture_service.search_lectures(search, user_id)
            total_count = len(lectures)
            # Áp dụng phân trang cho kết quả tìm kiếm
            start = (page - 1) * per_page
            end = start + per_page
            lectures = lectures[start:end]
        else:
            # Lấy danh sách thông thường
            lectures, total_count = await lecture_service.get_lectures(user_id, page, per_page)
        
        lecture_responses = [
            LectureResponse(
                id=str(lecture.id),
                title=lecture.title,
                subject=lecture.subject,
                grade=lecture.grade,
                description=lecture.description,
                requirements=lecture.requirements,
                content=lecture.content,
                status=lecture.status,
                created_at=lecture.created_at,
                updated_at=lecture.updated_at
            )
            for lecture in lectures
        ]
        
        return LectureListResponse(
            lectures=lecture_responses,
            total_count=total_count,
            page=page,
            per_page=per_page
        )
    except Exception as e:
        logger.error(f"Error getting lectures: {e}")
        raise HTTPException(status_code=500, detail="Không thể lấy danh sách bài giảng")

@router.put("/{lecture_id}", response_model=dict)
async def update_lecture(lecture_id: str, request: LectureUpdateRequest):
    """
    Cập nhật bài giảng
    """
    try:
        # Kiểm tra bài giảng tồn tại
        lecture = await lecture_service.get_lecture(lecture_id)
        if not lecture:
            raise HTTPException(status_code=404, detail="Không tìm thấy bài giảng")
        
        success = await lecture_service.update_lecture(lecture_id, request)
        if not success:
            raise HTTPException(status_code=400, detail="Không thể cập nhật bài giảng")
        
        return {"message": "Cập nhật bài giảng thành công"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating lecture: {e}")
        raise HTTPException(status_code=500, detail="Có lỗi xảy ra khi cập nhật bài giảng")

@router.delete("/{lecture_id}")
async def delete_lecture(lecture_id: str):
    """
    Xóa bài giảng
    """
    try:
        # Kiểm tra bài giảng tồn tại
        lecture = await lecture_service.get_lecture(lecture_id)
        if not lecture:
            raise HTTPException(status_code=404, detail="Không tìm thấy bài giảng")
        
        success = await lecture_service.delete_lecture(lecture_id)
        if not success:
            raise HTTPException(status_code=400, detail="Không thể xóa bài giảng")
        
        return {"message": "Xóa bài giảng thành công"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting lecture: {e}")
        raise HTTPException(status_code=500, detail="Có lỗi xảy ra khi xóa bài giảng")

@router.get("/{lecture_id}/export")
async def export_lecture(
    lecture_id: str,
    format: str = Query("pdf", description="Định dạng file: pdf, docx")
):
    """
    Xuất bài giảng ra file
    """
    try:
        # Kiểm tra bài giảng tồn tại
        lecture = await lecture_service.get_lecture(lecture_id)
        if not lecture:
            raise HTTPException(status_code=404, detail="Không tìm thấy bài giảng")
        
        # TODO: Implement file export logic
        # Hiện tại trả về thông báo placeholder
        return {
            "message": "Chức năng xuất file đang được phát triển",
            "lecture_id": lecture_id,
            "format": format,
            "download_url": f"/api/v1/lectures/{lecture_id}/download?format={format}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting lecture: {e}")
        raise HTTPException(status_code=500, detail="Có lỗi xảy ra khi xuất file")

@router.get("/search/suggestions")
async def get_search_suggestions(
    query: str = Query(..., min_length=2, description="Từ khóa tìm kiếm"),
    user_id: Optional[str] = Query(None, description="ID của user"),
    limit: int = Query(5, ge=1, le=10, description="Số gợi ý")
):
    """
    Lấy gợi ý tìm kiếm cho bài giảng
    """
    try:
        lectures = await lecture_service.search_lectures(query, user_id)
        
        # Tạo gợi ý từ kết quả tìm kiếm
        suggestions = []
        for lecture in lectures[:limit]:
            suggestions.append({
                "id": str(lecture.id),
                "title": lecture.title,
                "subject": lecture.subject,
                "type": "lecture"
            })
        
        return {"suggestions": suggestions}
        
    except Exception as e:
        logger.error(f"Error getting search suggestions: {e}")
        raise HTTPException(status_code=500, detail="Không thể lấy gợi ý tìm kiếm")
