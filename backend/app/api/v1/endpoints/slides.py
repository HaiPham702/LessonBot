from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
import logging

from app.models.slide import (
    SlideCreateRequest,
    SlideUpdateRequest,
    SlideFromLectureRequest,
    SlideResponse,
    SlideListResponse
)
from app.services.slide_service import slide_service

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/create", response_model=dict)
async def create_slide(request: SlideCreateRequest):
    """
    Tạo slide thuyết trình mới
    """
    try:
        slide_id = await slide_service.create_slide(request)
        return {
            "slide_id": slide_id,
            "message": "Slide đang được tạo. Vui lòng chờ trong giây lát.",
            "status": "generating"
        }
    except Exception as e:
        logger.error(f"Error creating slide: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/from-lecture/{lecture_id}", response_model=dict)
async def create_slide_from_lecture(lecture_id: str, options: dict = {}):
    """
    Tạo slide từ bài giảng có sẵn
    """
    try:
        request = SlideFromLectureRequest(
            lecture_id=lecture_id,
            include_intro=options.get("include_intro", True),
            include_conclusion=options.get("include_conclusion", True),
            include_questions=options.get("include_questions", False),
            slide_style=options.get("slide_style", "professional"),
            user_id=options.get("user_id")
        )
        
        slide_id = await slide_service.create_slide_from_lecture(request)
        return {
            "slide_id": slide_id,
            "message": "Slide từ bài giảng đang được tạo. Vui lòng chờ trong giây lát.",
            "status": "generating"
        }
    except Exception as e:
        logger.error(f"Error creating slide from lecture: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{slide_id}", response_model=SlideResponse)
async def get_slide(slide_id: str):
    """
    Lấy chi tiết slide
    """
    try:
        slide = await slide_service.get_slide(slide_id)
        if not slide:
            raise HTTPException(status_code=404, detail="Không tìm thấy slide")
        
        return SlideResponse(
            id=str(slide.id),
            title=slide.title,
            subject=slide.subject,
            presentation_type=slide.presentation_type,
            duration=slide.duration,
            description=slide.description,
            requirements=slide.requirements,
            slides=slide.slides,
            slide_count=slide.slide_count,
            status=slide.status,
            created_at=slide.created_at,
            updated_at=slide.updated_at,
            source_lecture_id=slide.source_lecture_id
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting slide: {e}")
        raise HTTPException(status_code=500, detail="Không thể lấy thông tin slide")

@router.get("", response_model=SlideListResponse)
async def get_slides(
    user_id: Optional[str] = Query(None, description="ID của user"),
    page: int = Query(1, ge=1, description="Số trang"),
    per_page: int = Query(20, ge=1, le=50, description="Số slide mỗi trang"),
    search: Optional[str] = Query(None, description="Từ khóa tìm kiếm")
):
    """
    Lấy danh sách slides với phân trang và tìm kiếm
    """
    try:
        if search:
            # Tìm kiếm
            slides = await slide_service.search_slides(search, user_id)
            total_count = len(slides)
            # Áp dụng phân trang cho kết quả tìm kiếm
            start = (page - 1) * per_page
            end = start + per_page
            slides = slides[start:end]
        else:
            # Lấy danh sách thông thường
            slides, total_count = await slide_service.get_slides(user_id, page, per_page)
        
        slide_responses = [
            SlideResponse(
                id=str(slide.id),
                title=slide.title,
                subject=slide.subject,
                presentation_type=slide.presentation_type,
                duration=slide.duration,
                description=slide.description,
                requirements=slide.requirements,
                slides=slide.slides,
                slide_count=slide.slide_count,
                status=slide.status,
                created_at=slide.created_at,
                updated_at=slide.updated_at,
                source_lecture_id=slide.source_lecture_id
            )
            for slide in slides
        ]
        
        return SlideListResponse(
            slides=slide_responses,
            total_count=total_count,
            page=page,
            per_page=per_page
        )
    except Exception as e:
        logger.error(f"Error getting slides: {e}")
        raise HTTPException(status_code=500, detail="Không thể lấy danh sách slides")

@router.put("/{slide_id}", response_model=dict)
async def update_slide(slide_id: str, request: SlideUpdateRequest):
    """
    Cập nhật slide
    """
    try:
        # Kiểm tra slide tồn tại
        slide = await slide_service.get_slide(slide_id)
        if not slide:
            raise HTTPException(status_code=404, detail="Không tìm thấy slide")
        
        success = await slide_service.update_slide(slide_id, request)
        if not success:
            raise HTTPException(status_code=400, detail="Không thể cập nhật slide")
        
        return {"message": "Cập nhật slide thành công"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating slide: {e}")
        raise HTTPException(status_code=500, detail="Có lỗi xảy ra khi cập nhật slide")

@router.delete("/{slide_id}")
async def delete_slide(slide_id: str):
    """
    Xóa slide
    """
    try:
        # Kiểm tra slide tồn tại
        slide = await slide_service.get_slide(slide_id)
        if not slide:
            raise HTTPException(status_code=404, detail="Không tìm thấy slide")
        
        success = await slide_service.delete_slide(slide_id)
        if not success:
            raise HTTPException(status_code=400, detail="Không thể xóa slide")
        
        return {"message": "Xóa slide thành công"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting slide: {e}")
        raise HTTPException(status_code=500, detail="Có lỗi xảy ra khi xóa slide")

@router.get("/{slide_id}/export")
async def export_slide(
    slide_id: str,
    format: str = Query("pptx", description="Định dạng file: pptx, pdf")
):
    """
    Xuất slide ra file PowerPoint hoặc PDF
    """
    try:
        # Kiểm tra slide tồn tại
        slide = await slide_service.get_slide(slide_id)
        if not slide:
            raise HTTPException(status_code=404, detail="Không tìm thấy slide")
        
        # TODO: Implement file export logic
        # Hiện tại trả về thông báo placeholder
        return {
            "message": "Chức năng xuất file đang được phát triển",
            "slide_id": slide_id,
            "format": format,
            "download_url": f"/api/v1/slides/{slide_id}/download?format={format}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting slide: {e}")
        raise HTTPException(status_code=500, detail="Có lỗi xảy ra khi xuất file")

@router.get("/{slide_id}/preview")
async def preview_slide(slide_id: str, slide_number: int = Query(1, ge=1)):
    """
    Xem trước một slide cụ thể
    """
    try:
        slide = await slide_service.get_slide(slide_id)
        if not slide:
            raise HTTPException(status_code=404, detail="Không tìm thấy slide")
        
        if not slide.slides or slide_number > len(slide.slides):
            raise HTTPException(status_code=404, detail="Không tìm thấy slide số này")
        
        preview_slide = slide.slides[slide_number - 1]
        
        return {
            "slide_number": slide_number,
            "total_slides": len(slide.slides),
            "slide_content": preview_slide,
            "slide_title": slide.title
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error previewing slide: {e}")
        raise HTTPException(status_code=500, detail="Có lỗi xảy ra khi xem trước slide")

@router.get("/search/suggestions")
async def get_search_suggestions(
    query: str = Query(..., min_length=2, description="Từ khóa tìm kiếm"),
    user_id: Optional[str] = Query(None, description="ID của user"),
    limit: int = Query(5, ge=1, le=10, description="Số gợi ý")
):
    """
    Lấy gợi ý tìm kiếm cho slides
    """
    try:
        slides = await slide_service.search_slides(query, user_id)
        
        # Tạo gợi ý từ kết quả tìm kiếm
        suggestions = []
        for slide in slides[:limit]:
            suggestions.append({
                "id": str(slide.id),
                "title": slide.title,
                "subject": slide.subject,
                "type": "slide",
                "slide_count": slide.slide_count
            })
        
        return {"suggestions": suggestions}
        
    except Exception as e:
        logger.error(f"Error getting search suggestions: {e}")
        raise HTTPException(status_code=500, detail="Không thể lấy gợi ý tìm kiếm")
