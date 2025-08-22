from fastapi import APIRouter

from app.api.v1.endpoints import chat, lectures, slides, tools

api_router = APIRouter()

# Include các endpoint routers
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(lectures.router, prefix="/lectures", tags=["lectures"])
api_router.include_router(slides.router, prefix="/slides", tags=["slides"])
api_router.include_router(tools.router, prefix="/tools", tags=["tools"])
