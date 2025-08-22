import os
import asyncio
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(title="EduBot External Agent", version="1.0.0")

# Initialize LLM
llm = ChatOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
    temperature=0.7
)

class WebSearchRequest(BaseModel):
    query: str
    num_results: int = 5

class WebSearchResponse(BaseModel):
    results: List[Dict[str, Any]]
    status: str

class ContentEnrichmentRequest(BaseModel):
    topic: str
    subject: str
    content_type: str = "educational"  # educational, reference, examples

class ContentEnrichmentResponse(BaseModel):
    enriched_content: str
    sources: List[str]
    status: str

class ExternalResourceRequest(BaseModel):
    subject: str
    grade_level: str
    topic: str
    resource_type: str = "all"  # videos, articles, exercises, images

class ExternalResourceResponse(BaseModel):
    resources: List[Dict[str, Any]]
    status: str

class ExternalAgent:
    def __init__(self):
        self.llm = llm
    
    async def search_educational_content(self, query: str, subject: str = None) -> Dict[str, Any]:
        """Tìm kiếm nội dung giáo dục từ các nguồn bên ngoài"""
        try:
            # Simulate external API calls (in real implementation, call actual APIs)
            
            # 1. Wikipedia search for basic information
            wikipedia_content = await self._search_wikipedia(query)
            
            # 2. Educational resource search
            educational_resources = await self._search_educational_resources(query, subject)
            
            # 3. Academic paper search (simplified)
            academic_resources = await self._search_academic_content(query)
            
            return {
                "wikipedia": wikipedia_content,
                "educational_resources": educational_resources,
                "academic_resources": academic_resources,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Error searching educational content: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _search_wikipedia(self, query: str) -> Dict[str, Any]:
        """Tìm kiếm thông tin từ Wikipedia (mock implementation)"""
        try:
            # Mock Wikipedia API call
            # In real implementation, use wikipedia-api or direct API calls
            
            system_prompt = f"""
            Hãy tìm kiếm thông tin cơ bản về "{query}" như thể bạn đang tra cứu từ Wikipedia.
            Trả về thông tin chính xác, khách quan và có cấu trúc rõ ràng.
            
            Format trả về:
            - Định nghĩa ngắn gọn
            - Thông tin chi tiết chính
            - Các ứng dụng hoặc ví dụ
            """
            
            messages = [SystemMessage(content=system_prompt)]
            response = await self.llm.ainvoke(messages)
            
            return {
                "title": query,
                "summary": response.content[:200] + "...",
                "content": response.content,
                "url": f"https://wikipedia.org/wiki/{query.replace(' ', '_')}"
            }
            
        except Exception as e:
            logger.error(f"Error searching Wikipedia: {e}")
            return {"error": str(e)}
    
    async def _search_educational_resources(self, query: str, subject: str = None) -> List[Dict[str, Any]]:
        """Tìm kiếm tài nguyên giáo dục"""
        try:
            # Mock educational resource search
            # In real implementation, call APIs like Khan Academy, Coursera, etc.
            
            resources = [
                {
                    "title": f"Bài học về {query}",
                    "type": "video",
                    "platform": "Khan Academy",
                    "url": f"https://khanacademy.org/search/{query}",
                    "description": f"Video giảng dạy chi tiết về {query}",
                    "duration": "15 phút",
                    "level": "Trung học"
                },
                {
                    "title": f"Bài tập thực hành {query}",
                    "type": "exercise",
                    "platform": "Education.com",
                    "url": f"https://education.com/search/{query}",
                    "description": f"Bài tập và worksheet về {query}",
                    "difficulty": "Cơ bản đến nâng cao"
                },
                {
                    "title": f"Tài liệu tham khảo {query}",
                    "type": "article",
                    "platform": "Britannica",
                    "url": f"https://britannica.com/search/{query}",
                    "description": f"Bài viết học thuật về {query}",
                    "reading_time": "10 phút"
                }
            ]
            
            return resources
            
        except Exception as e:
            logger.error(f"Error searching educational resources: {e}")
            return []
    
    async def _search_academic_content(self, query: str) -> List[Dict[str, Any]]:
        """Tìm kiếm nội dung học thuật"""
        try:
            # Mock academic search
            # In real implementation, use Google Scholar API, PubMed, etc.
            
            papers = [
                {
                    "title": f"Research on {query}: A Comprehensive Study",
                    "authors": ["Dr. Academic", "Prof. Research"],
                    "abstract": f"This paper presents a comprehensive analysis of {query}...",
                    "publication_year": 2023,
                    "journal": "Journal of Educational Research",
                    "citation_count": 45,
                    "url": f"https://scholar.google.com/search?q={query}"
                }
            ]
            
            return papers
            
        except Exception as e:
            logger.error(f"Error searching academic content: {e}")
            return []
    
    async def enrich_content_with_external_sources(self, topic: str, subject: str, existing_content: str = "") -> Dict[str, Any]:
        """Làm giàu nội dung với các nguồn bên ngoài"""
        try:
            # Search for additional content
            search_results = await self.search_educational_content(topic, subject)
            
            # Use LLM to integrate external sources with existing content
            system_prompt = f"""
            Bạn là chuyên gia giáo dục. Hãy làm giàu nội dung sau với thông tin từ các nguồn bên ngoài.
            
            Chủ đề: {topic}
            Môn học: {subject}
            Nội dung hiện tại: {existing_content}
            
            Thông tin bổ sung từ các nguồn:
            {search_results}
            
            Hãy:
            1. Tích hợp thông tin mới một cách tự nhiên
            2. Thêm ví dụ thực tế và ứng dụng
            3. Bao gồm tài liệu tham khảo
            4. Đảm bảo tính chính xác và phù hợp với cấp độ học tập
            
            Trả về nội dung đã được làm giàu và danh sách nguồn tham khảo.
            """
            
            messages = [SystemMessage(content=system_prompt)]
            response = await self.llm.ainvoke(messages)
            
            # Extract sources from search results
            sources = []
            if search_results.get("wikipedia"):
                sources.append(search_results["wikipedia"].get("url", ""))
            
            for resource in search_results.get("educational_resources", []):
                sources.append(resource.get("url", ""))
            
            return {
                "enriched_content": response.content,
                "sources": sources,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Error enriching content: {e}")
            return {
                "enriched_content": existing_content,
                "sources": [],
                "status": "error",
                "message": str(e)
            }
    
    async def get_multimedia_resources(self, topic: str, resource_type: str = "all") -> List[Dict[str, Any]]:
        """Lấy tài nguyên đa phương tiện"""
        try:
            resources = []
            
            if resource_type in ["all", "images"]:
                # Mock image search
                images = [
                    {
                        "type": "image",
                        "title": f"Hình ảnh minh họa {topic}",
                        "url": f"https://unsplash.com/search/photos/{topic}",
                        "description": f"Hình ảnh chất lượng cao về {topic}",
                        "license": "Free to use"
                    }
                ]
                resources.extend(images)
            
            if resource_type in ["all", "videos"]:
                # Mock video search
                videos = [
                    {
                        "type": "video",
                        "title": f"Video giảng dạy {topic}",
                        "url": f"https://youtube.com/search?q={topic}+education",
                        "description": f"Video giáo dục về {topic}",
                        "duration": "10-15 phút",
                        "platform": "YouTube EDU"
                    }
                ]
                resources.extend(videos)
            
            if resource_type in ["all", "simulations"]:
                # Mock simulation/interactive content
                simulations = [
                    {
                        "type": "simulation",
                        "title": f"Mô phỏng tương tác {topic}",
                        "url": f"https://phet.colorado.edu/search?q={topic}",
                        "description": f"Mô phỏng tương tác để học {topic}",
                        "platform": "PhET Interactive Simulations"
                    }
                ]
                resources.extend(simulations)
            
            return resources
            
        except Exception as e:
            logger.error(f"Error getting multimedia resources: {e}")
            return []

# Initialize external agent
external_agent = ExternalAgent()

# API Endpoints
@app.post("/search", response_model=WebSearchResponse)
async def web_search(request: WebSearchRequest):
    """Tìm kiếm nội dung giáo dục từ web"""
    try:
        results = await external_agent.search_educational_content(request.query)
        
        # Format results for response
        formatted_results = []
        
        if results.get("wikipedia"):
            formatted_results.append({
                "title": results["wikipedia"].get("title", ""),
                "content": results["wikipedia"].get("summary", ""),
                "url": results["wikipedia"].get("url", ""),
                "source": "Wikipedia"
            })
        
        for resource in results.get("educational_resources", []):
            formatted_results.append({
                "title": resource.get("title", ""),
                "content": resource.get("description", ""),
                "url": resource.get("url", ""),
                "source": resource.get("platform", "")
            })
        
        return WebSearchResponse(
            results=formatted_results[:request.num_results],
            status="success"
        )
        
    except Exception as e:
        logger.error(f"Error in web search: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/enrich-content", response_model=ContentEnrichmentResponse)
async def enrich_content(request: ContentEnrichmentRequest):
    """Làm giàu nội dung với các nguồn bên ngoài"""
    try:
        result = await external_agent.enrich_content_with_external_sources(
            topic=request.topic,
            subject=request.subject
        )
        
        return ContentEnrichmentResponse(
            enriched_content=result["enriched_content"],
            sources=result["sources"],
            status=result["status"]
        )
        
    except Exception as e:
        logger.error(f"Error enriching content: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/get-resources", response_model=ExternalResourceResponse)
async def get_external_resources(request: ExternalResourceRequest):
    """Lấy tài nguyên bên ngoài cho chủ đề"""
    try:
        resources = await external_agent.get_multimedia_resources(
            topic=request.topic,
            resource_type=request.resource_type
        )
        
        return ExternalResourceResponse(
            resources=resources,
            status="success"
        )
        
    except Exception as e:
        logger.error(f"Error getting external resources: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "external_agent"}

@app.post("/translate")
async def translate_content(
    text: str,
    source_lang: str = "vi",
    target_lang: str = "en"
):
    """Dịch nội dung (mock implementation)"""
    try:
        system_prompt = f"""
        Hãy dịch văn bản sau từ {source_lang} sang {target_lang}:
        
        "{text}"
        
        Đảm bảo:
        - Giữ nguyên ý nghĩa và ngữ cảnh
        - Sử dụng thuật ngữ chuyên môn phù hợp
        - Văn phong tự nhiên
        """
        
        messages = [SystemMessage(content=system_prompt)]
        response = await llm.ainvoke(messages)
        
        return {
            "translated_text": response.content,
            "source_lang": source_lang,
            "target_lang": target_lang,
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error translating content: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/fact-check")
async def fact_check(content: str, topic: str):
    """Kiểm tra tính chính xác của nội dung"""
    try:
        # Search for supporting information
        search_results = await external_agent.search_educational_content(topic)
        
        system_prompt = f"""
        Hãy kiểm tra tính chính xác của nội dung sau:
        
        "{content}"
        
        Dựa trên thông tin tham khảo:
        {search_results}
        
        Đánh giá:
        1. Tính chính xác của thông tin
        2. Các thông tin cần cập nhật hoặc bổ sung
        3. Nguồn tham khảo đáng tin cậy
        
        Trả về đánh giá chi tiết và gợi ý cải thiện.
        """
        
        messages = [SystemMessage(content=system_prompt)]
        response = await llm.ainvoke(messages)
        
        return {
            "fact_check_result": response.content,
            "confidence_score": 0.85,  # Mock score
            "sources_checked": len(search_results.get("educational_resources", [])),
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error fact checking: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
