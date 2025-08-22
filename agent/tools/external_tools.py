import httpx
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class ExternalTools:
    """Tools để gọi external services"""
    
    def __init__(self, external_agent_url: str):
        self.external_agent_url = external_agent_url
    
    async def web_search(self, query: str, num_results: int = 5) -> Dict[str, Any]:
        """Tìm kiếm nội dung giáo dục từ web"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.external_agent_url}/search",
                    json={
                        "query": query,
                        "num_results": num_results
                    }
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error in web search: {e}")
            return {"status": "error", "results": [], "error": str(e)}
    
    async def enrich_content(self, topic: str, subject: str, content_type: str = "educational") -> Dict[str, Any]:
        """Làm giàu nội dung với các nguồn bên ngoài"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.external_agent_url}/enrich-content",
                    json={
                        "topic": topic,
                        "subject": subject,
                        "content_type": content_type
                    }
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error enriching content: {e}")
            return {"status": "error", "enriched_content": "", "sources": [], "error": str(e)}
    
    async def get_external_resources(self, 
                                   subject: str, 
                                   grade_level: str, 
                                   topic: str, 
                                   resource_type: str = "all") -> Dict[str, Any]:
        """Lấy tài nguyên bên ngoài"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.external_agent_url}/get-resources",
                    json={
                        "subject": subject,
                        "grade_level": grade_level,
                        "topic": topic,
                        "resource_type": resource_type
                    }
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error getting external resources: {e}")
            return {"status": "error", "resources": [], "error": str(e)}
    
    async def translate_content(self, 
                              text: str, 
                              source_lang: str = "vi", 
                              target_lang: str = "en") -> Dict[str, Any]:
        """Dịch nội dung"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.external_agent_url}/translate",
                    params={
                        "text": text,
                        "source_lang": source_lang,
                        "target_lang": target_lang
                    }
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error translating content: {e}")
            return {
                "status": "error", 
                "translated_text": text, 
                "error": str(e)
            }
    
    async def fact_check(self, content: str, topic: str) -> Dict[str, Any]:
        """Kiểm tra tính chính xác của nội dung"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.external_agent_url}/fact-check",
                    json={
                        "content": content,
                        "topic": topic
                    }
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error fact checking: {e}")
            return {
                "status": "error", 
                "fact_check_result": "Không thể kiểm tra", 
                "confidence_score": 0.0,
                "error": str(e)
            }

class WikipediaTools:
    """Tools để tương tác với Wikipedia"""
    
    async def search_wikipedia(self, query: str, lang: str = "vi") -> Dict[str, Any]:
        """Tìm kiếm thông tin từ Wikipedia"""
        try:
            # Mock implementation - in real app would use wikipedia API
            async with httpx.AsyncClient() as client:
                url = f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{query}"
                response = await client.get(url)
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "title": data.get("title", ""),
                        "summary": data.get("extract", ""),
                        "url": data.get("content_urls", {}).get("desktop", {}).get("page", ""),
                        "status": "success"
                    }
                else:
                    return {"status": "not_found", "error": "Không tìm thấy trang Wikipedia"}
                    
        except Exception as e:
            logger.error(f"Error searching Wikipedia: {e}")
            return {"status": "error", "error": str(e)}

class EducationalAPIs:
    """Tools để gọi các API giáo dục"""
    
    async def get_khan_academy_content(self, topic: str) -> Dict[str, Any]:
        """Lấy nội dung từ Khan Academy (mock)"""
        try:
            # Mock implementation
            return {
                "videos": [
                    {
                        "title": f"Học {topic} cơ bản",
                        "url": f"https://khanacademy.org/search?q={topic}",
                        "duration": "15 phút",
                        "level": "Cơ bản"
                    }
                ],
                "exercises": [
                    {
                        "title": f"Bài tập {topic}",
                        "url": f"https://khanacademy.org/exercise/{topic}",
                        "difficulty": "Cơ bản"
                    }
                ],
                "status": "success"
            }
        except Exception as e:
            logger.error(f"Error getting Khan Academy content: {e}")
            return {"status": "error", "error": str(e)}
    
    async def get_coursera_courses(self, subject: str) -> Dict[str, Any]:
        """Lấy khóa học từ Coursera (mock)"""
        try:
            # Mock implementation
            return {
                "courses": [
                    {
                        "title": f"Khóa học {subject} chuyên sâu",
                        "provider": "University Partner",
                        "url": f"https://coursera.org/search?query={subject}",
                        "duration": "4-6 tuần",
                        "level": "Trung cấp"
                    }
                ],
                "status": "success"
            }
        except Exception as e:
            logger.error(f"Error getting Coursera courses: {e}")
            return {"status": "error", "error": str(e)}
    
    async def get_educational_videos(self, topic: str, platform: str = "youtube") -> Dict[str, Any]:
        """Lấy video giáo dục"""
        try:
            # Mock implementation
            videos = []
            
            if platform == "youtube":
                videos = [
                    {
                        "title": f"Giảng dạy {topic} - Phần 1",
                        "channel": "Kênh Giáo dục",
                        "url": f"https://youtube.com/search?q={topic}+giảng+dạy",
                        "duration": "20 phút",
                        "views": "10,000+"
                    }
                ]
            elif platform == "ted":
                videos = [
                    {
                        "title": f"TED Talk về {topic}",
                        "speaker": "Chuyên gia giáo dục",
                        "url": f"https://ted.com/search?q={topic}",
                        "duration": "18 phút",
                        "views": "500,000+"
                    }
                ]
            
            return {
                "videos": videos,
                "platform": platform,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Error getting educational videos: {e}")
            return {"status": "error", "error": str(e)}

class ResearchTools:
    """Tools để nghiên cứu và fact-checking"""
    
    async def search_academic_papers(self, query: str, limit: int = 5) -> Dict[str, Any]:
        """Tìm kiếm bài báo khoa học (mock Google Scholar)"""
        try:
            # Mock implementation
            papers = []
            for i in range(min(limit, 3)):
                papers.append({
                    "title": f"Research on {query}: Study {i+1}",
                    "authors": [f"Author {i+1}", f"Co-author {i+1}"],
                    "abstract": f"This study investigates {query} and presents findings...",
                    "year": 2023 - i,
                    "citations": 50 - i*10,
                    "url": f"https://scholar.google.com/search?q={query}",
                    "journal": f"Journal of {query.title()} Research"
                })
            
            return {
                "papers": papers,
                "total_results": len(papers),
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Error searching academic papers: {e}")
            return {"status": "error", "error": str(e)}
    
    async def verify_facts(self, statement: str, domain: str = "education") -> Dict[str, Any]:
        """Xác minh tính chính xác của thông tin"""
        try:
            # Mock fact-checking implementation
            confidence_score = 0.85  # Mock confidence
            
            return {
                "statement": statement,
                "verification_result": "Likely accurate",
                "confidence_score": confidence_score,
                "sources_checked": 3,
                "domain": domain,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Error verifying facts: {e}")
            return {"status": "error", "error": str(e)}
