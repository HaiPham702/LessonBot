import os
import asyncio
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(title="EduBot Main Agent", version="1.0.0")

# Initialize LLM
llm = ChatOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
    temperature=0.7
)

# Backend API URL
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000/api/v1")

class ProcessRequest(BaseModel):
    message: str
    chat_history: List[Dict[str, Any]] = []
    user_id: str = None

class ProcessResponse(BaseModel):
    reply: str
    metadata: Dict[str, Any] = {}

class LectureGenerationRequest(BaseModel):
    title: str
    subject: str
    grade: str = None
    requirements: str
    user_preferences: Dict[str, Any] = {}

class SlideGenerationRequest(BaseModel):
    title: str
    subject: str
    presentation_type: str = None
    duration: int = None
    requirements: str
    user_preferences: Dict[str, Any] = {}

class SlideFromLectureRequest(BaseModel):
    lecture_content: str
    lecture_title: str
    lecture_subject: str
    include_intro: bool = True
    include_conclusion: bool = True
    include_questions: bool = False
    slide_style: str = "professional"

# Agent State
class AgentState(BaseModel):
    message: str
    chat_history: List[Dict[str, Any]] = []
    user_id: Optional[str] = None
    intent: Optional[str] = None
    entities: Dict[str, Any] = {}
    response: Optional[str] = None
    tools_used: List[str] = []
    metadata: Dict[str, Any] = {}

class EduBotAgent:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.llm = llm
        self.graph = self._create_graph()
    
    def _create_graph(self):
        """Tạo LangGraph workflow"""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("understand_intent", self.understand_intent)
        workflow.add_node("route_request", self.route_request)
        workflow.add_node("handle_chat", self.handle_chat)
        workflow.add_node("handle_lecture_creation", self.handle_lecture_creation)
        workflow.add_node("handle_slide_creation", self.handle_slide_creation)
        workflow.add_node("handle_search", self.handle_search)
        workflow.add_node("generate_response", self.generate_response)
        
        # Set entry point
        workflow.set_entry_point("understand_intent")
        
        # Add edges
        workflow.add_edge("understand_intent", "route_request")
        workflow.add_conditional_edges(
            "route_request",
            self.route_decision,
            {
                "chat": "handle_chat",
                "create_lecture": "handle_lecture_creation",
                "create_slide": "handle_slide_creation",
                "search": "handle_search"
            }
        )
        workflow.add_edge("handle_chat", "generate_response")
        workflow.add_edge("handle_lecture_creation", "generate_response")
        workflow.add_edge("handle_slide_creation", "generate_response")
        workflow.add_edge("handle_search", "generate_response")
        workflow.add_edge("generate_response", END)
        
        return workflow.compile(checkpointer=MemorySaver())
    
    async def understand_intent(self, state: AgentState) -> AgentState:
        """Phân tích ý định của user"""
        try:
            system_prompt = """
            Bạn là trợ lý AI chuyên hỗ trợ giáo viên soạn giảng. Hãy phân tích tin nhắn của user và xác định ý định.
            
            Các ý định có thể:
            - "create_lecture": Muốn tạo bài giảng mới
            - "create_slide": Muốn tạo slide thuyết trình
            - "search": Muốn tìm kiếm bài giảng/slide có sẵn
            - "chat": Trò chuyện thông thường, hỏi đáp
            
            Trả về JSON với format:
            {
                "intent": "intent_name",
                "entities": {
                    "subject": "môn học nếu có",
                    "topic": "chủ đề nếu có",
                    "grade": "cấp độ nếu có"
                }
            }
            """
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"Tin nhắn user: {state.message}")
            ]
            
            response = await self.llm.ainvoke(messages)
            
            # Parse response (simplified - in real app would use structured output)
            import json
            try:
                result = json.loads(response.content)
                state.intent = result.get("intent", "chat")
                state.entities = result.get("entities", {})
            except:
                state.intent = "chat"
                state.entities = {}
            
            logger.info(f"Intent detected: {state.intent}")
            return state
            
        except Exception as e:
            logger.error(f"Error in understand_intent: {e}")
            state.intent = "chat"
            return state
    
    def route_decision(self, state: AgentState) -> str:
        """Quyết định route dựa trên intent"""
        return state.intent
    
    async def route_request(self, state: AgentState) -> AgentState:
        """Route request to appropriate handler"""
        return state
    
    async def handle_chat(self, state: AgentState) -> AgentState:
        """Xử lý chat thông thường"""
        try:
            # Tạo context từ chat history
            context = ""
            if state.chat_history:
                recent_messages = state.chat_history[-5:]  # 5 tin nhắn gần nhất
                for msg in recent_messages:
                    context += f"{msg['sender']}: {msg['content']}\n"
            
            system_prompt = f"""
            Bạn là trợ lý AI chuyên hỗ trợ giáo viên soạn giảng. Bạn có thể:
            
            1. Tư vấn về phương pháp giảng dạy
            2. Gợi ý nội dung bài giảng
            3. Hướng dẫn tạo slide thuyết trình
            4. Giải đáp thắc mắc về giáo dục
            
            Context cuộc trò chuyện:
            {context}
            
            Hãy trả lời một cách hữu ích, thân thiện và chuyên nghiệp.
            """
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=state.message)
            ]
            
            response = await self.llm.ainvoke(messages)
            state.response = response.content
            state.tools_used.append("chat_completion")
            
            return state
            
        except Exception as e:
            logger.error(f"Error in handle_chat: {e}")
            state.response = "Xin lỗi, tôi gặp sự cố khi xử lý tin nhắn. Vui lòng thử lại."
            return state
    
    async def handle_lecture_creation(self, state: AgentState) -> AgentState:
        """Xử lý tạo bài giảng"""
        try:
            # Create detailed lecture outline
            system_prompt = """
            Bạn là chuyên gia giáo dục. Hãy tạo một dàn ý bài giảng thật chi tiết dựa vào yêu cầu của user.
            
            Trả về JSON với format sau:
            {
                "title": "tiêu đề bài giảng",
                "subject": "môn học", 
                "grade": "cấp độ học (elementary/middle/high/university)",
                "duration": "thời lượng (phút)",
                "objectives": ["mục tiêu 1", "mục tiêu 2", "..."],
                "outline": [
                    {
                        "section": "Phần I: Tên phần",
                        "duration": "15 phút",
                        "topics": [
                            {
                                "main_topic": "Đầu mục lớn 1",
                                "subtopics": [
                                    {
                                        "subtitle": "Đầu mục nhỏ 1.1",
                                        "content": "Nội dung chi tiết...",
                                        "activities": ["hoạt động 1", "hoạt động 2"]
                                    }
                                ]
                            }
                        ]
                    }
                ],
                "resources": ["tài liệu 1", "tài liệu 2"],
                "assessment": "phương pháp đánh giá"
            }
            
            Hãy tạo dàn ý thật chi tiết và phù hợp với yêu cầu.
            """
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"Yêu cầu: {state.message}")
            ]
            
            response = await self.llm.ainvoke(messages)
            
            # Parse and create lecture (simplified)
            import json
            import re
            try:
                # Try to extract JSON from response
                response_text = response.content
                logger.info(f"Raw response: {response_text}")
                
                                # Try direct JSON parsing first
                try:
                    lecture_data = json.loads(response_text)
                    logger.info(f"lecture_data: {lecture_data}")
                except json.JSONDecodeError:
                    # If direct parsing fails, try to extract JSON block
                    json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                    if json_match:
                        json_str = json_match.group(0)
                        lecture_data = json.loads(json_str)
                    else:
                        # Fallback: create simple data from response text
                        lecture_data = {
                            "title": "Bài giảng theo yêu cầu",
                            "subject": "Tổng hợp",
                            "grade": "elementary",
                            "duration": "45 phút",
                            "objectives": ["Hiểu nội dung cơ bản"],
                            "outline": [{
                                "section": "Phần chính",
                                "duration": "30 phút",
                                "topics": [{
                                    "main_topic": "Nội dung chính",
                                    "subtopics": [{
                                        "subtitle": "Chi tiết",
                                        "content": response_text[:200] + "...",
                                        "activities": ["Thảo luận", "Thực hành"]
                                    }]
                                }]
                            }],
                            "resources": ["Tài liệu tham khảo"],
                            "assessment": "Đánh giá qua bài tập"
                        }

                # Prepare response with detailed lecture outline
                state.response = f"✅ **Dàn ý bài giảng: {lecture_data.get('title')}**\n\n"
                
                # Set metadata for FE to recognize this as a lecture response
                state.metadata = {
                    "type": "lecture",
                    "lecture_data": lecture_data,
                    "editable": True,
                    "show_create_slide_button": True
                }
                state.tools_used.append("create_lecture")
                        
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing JSON response: {e}")
                state.response = "Không thể hiểu yêu cầu tạo bài giảng. Vui lòng mô tả chi tiết hơn."
            except httpx.ReadTimeout as e:
                logger.error(f"Timeout khi gọi backend: {e}")
                state.response = "Backend phản hồi chậm. Vui lòng thử lại sau."
            except Exception as e:
                logger.error(f"Error creating lecture: {e}")
                state.response = f"Có lỗi xảy ra khi tạo bài giảng: {str(e)}"
            
            return state
            
        except Exception as e:
            logger.error(f"Error in handle_lecture_creation: {e}")
            state.response = "Có lỗi xảy ra khi tạo bài giảng."
            return state
    
    async def handle_slide_creation(self, state: AgentState) -> AgentState:
        """Xử lý tạo slide"""
        try:
            # Similar to lecture creation but for slides
            system_prompt = """
            Hãy trích xuất thông tin để tạo slide từ yêu cầu của user.
            
            Trả về JSON với format:
            {
                "title": "tiêu đề slide",
                "subject": "môn học",
                "presentation_type": "lecture/workshop/seminar/conference",
                "duration": 45,
                "requirements": "yêu cầu chi tiết về nội dung slide"
            }
            """
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"Yêu cầu: {state.message}")
            ]
            
            response = await self.llm.ainvoke(messages)
            
            # Parse and create slide
            import json
            import re
            try:
                # Try to extract JSON from response
                response_text = response.content
                logger.info(f"Raw slide response: {response_text}")
                
                # Try direct JSON parsing first
                try:
                    slide_data = json.loads(response_text)
                except json.JSONDecodeError:
                    # If direct parsing fails, try to extract JSON block
                    json_match = re.search(r'\{[^}]*\}', response_text, re.DOTALL)
                    if json_match:
                        json_str = json_match.group(0)
                        slide_data = json.loads(json_str)
                    else:
                        # Fallback: create data from response text
                        slide_data = {
                            "title": "Slide theo yêu cầu",
                            "type": "content",
                            "content": state.message
                        }
                
                # Call backend to create slide
                async with httpx.AsyncClient() as client:
                    backend_response = await client.post(
                        f"{self.backend_url}/tools/create-slide-draft",
                        json={
                            "title": slide_data.get("title", "Slide mới"),
                            "subject": slide_data.get("subject", ""),
                            "presentation_type": slide_data.get("presentation_type"),
                            "duration": slide_data.get("duration"),
                            "requirements": slide_data.get("requirements", state.message),
                            "user_id": state.user_id
                        }
                    )
                    
                    if backend_response.status_code == 200:
                        result = backend_response.json()
                        state.response = f"Tôi đã tạo slide '{slide_data.get('title')}' cho bạn. Slide đang được sinh nội dung tự động và sẽ sẵn sàng trong vài phút."
                        state.metadata["slide_id"] = result.get("slide_id")
                        state.tools_used.append("create_slide")
                    else:
                        state.response = "Có lỗi xảy ra khi tạo slide. Vui lòng thử lại."
                        
            except Exception as e:
                logger.error(f"Error parsing slide data: {e}")
                state.response = "Không thể hiểu yêu cầu tạo slide. Vui lòng mô tả chi tiết hơn."
            
            return state
            
        except Exception as e:
            logger.error(f"Error in handle_slide_creation: {e}")
            state.response = "Có lỗi xảy ra khi tạo slide."
            return state
    
    async def handle_search(self, state: AgentState) -> AgentState:
        """Xử lý tìm kiếm"""
        try:
            # Search both lectures and slides
            async with httpx.AsyncClient() as client:
                # Search lectures
                lecture_response = await client.post(
                    f"{self.backend_url}/tools/search-lectures",
                    json={
                        "query": state.message,
                        "user_id": state.user_id,
                        "limit": 3
                    }
                )
                
                # Search slides
                slide_response = await client.post(
                    f"{self.backend_url}/tools/search-slides",
                    json={
                        "query": state.message,
                        "user_id": state.user_id,
                        "limit": 3
                    }
                )
                
                lectures = []
                slides = []
                
                if lecture_response.status_code == 200:
                    lecture_data = lecture_response.json()
                    lectures = lecture_data.get("lectures", [])
                
                if slide_response.status_code == 200:
                    slide_data = slide_response.json()
                    slides = slide_data.get("slides", [])
                
                # Format response
                if lectures or slides:
                    response_parts = ["Tôi tìm thấy các tài liệu sau:\n"]
                    
                    if lectures:
                        response_parts.append("📚 **Bài giảng:**")
                        for lecture in lectures:
                            response_parts.append(f"- {lecture['title']} ({lecture['subject']})")
                    
                    if slides:
                        response_parts.append("\n🎯 **Slides:**")
                        for slide in slides:
                            response_parts.append(f"- {slide['title']} ({slide['slide_count']} slides)")
                    
                    state.response = "\n".join(response_parts)
                    state.metadata["search_results"] = {"lectures": lectures, "slides": slides}
                    state.tools_used.append("search")
                else:
                    state.response = "Không tìm thấy tài liệu nào phù hợp. Bạn có muốn tôi tạo mới không?"
            
            return state
            
        except Exception as e:
            logger.error(f"Error in handle_search: {e}")
            state.response = "Có lỗi xảy ra khi tìm kiếm."
            return state
    
    async def generate_response(self, state: AgentState) -> AgentState:
        """Tạo phản hồi cuối cùng"""
        # Response đã được tạo ở các handler trước đó
        if not state.response:
            state.response = "Tôi chưa hiểu yêu cầu của bạn. Bạn có thể mô tả chi tiết hơn không?"
        
        return state
    
    async def process(self, request: ProcessRequest) -> ProcessResponse:
        """Xử lý request chính"""
        try:
            # Create initial state
            initial_state = AgentState(
                message=request.message,
                chat_history=request.chat_history,
                user_id=request.user_id
            ).model_dump()
            
            # Run the graph
            config = {"configurable": {"thread_id": request.user_id or "default"}}
            result = await self.graph.ainvoke(initial_state, config)
            
            return ProcessResponse(
                reply=result.get("response", "Xin lỗi, không thể tạo phản hồi."),
                metadata=result.get("metadata", {})
            )
            
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            return ProcessResponse(
                reply="Xin lỗi, tôi gặp sự cố kỹ thuật. Vui lòng thử lại sau.",
                metadata={"error": True}
            )

# Initialize agent
agent = EduBotAgent()

# API Endpoints
@app.post("/process", response_model=ProcessResponse)
async def process_message(request: ProcessRequest):
    """Main endpoint để xử lý tin nhắn"""
    return await agent.process(request)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "main_agent"}

@app.post("/generate/lecture")
async def generate_lecture(request: LectureGenerationRequest):
    """Generate lecture content"""
    try:
        system_prompt = f"""
        Bạn là chuyên gia giáo dục. Hãy tạo một bài giảng chi tiết với các yêu cầu sau:
        
        Tiêu đề: {request.title}
        Môn học: {request.subject}
        Cấp độ: {request.grade or "Không xác định"}
        Yêu cầu: {request.requirements}
        
        Bài giảng cần có:
        1. Mục tiêu học tập rõ ràng
        2. Nội dung chi tiết theo từng phần
        3. Phương pháp giảng dạy phù hợp
        4. Bài tập và câu hỏi kiểm tra
        5. Tài liệu tham khảo
        
        Hãy viết bài giảng đầy đủ và chuyên nghiệp.
        """
        
        messages = [SystemMessage(content=system_prompt)]
        response = await llm.ainvoke(messages)
        
        return {
            "content": response.content,
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error generating lecture: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate/slide")
async def generate_slide(request: SlideGenerationRequest):
    """Generate slide content"""
    try:
        system_prompt = f"""
        Bạn là chuyên gia thiết kế slide giáo dục. Hãy tạo nội dung slide với các yêu cầu sau:
        
        Tiêu đề: {request.title}
        Môn học: {request.subject}
        Loại thuyết trình: {request.presentation_type or "Bài giảng"}
        Thời lượng: {request.duration or 45} phút
        Yêu cầu: {request.requirements}
        
        Tạo từ 10-15 slides bao gồm:
        1. Slide tiêu đề
        2. Slide mục tiêu
        3. Slide nội dung chính (8-10 slides)
        4. Slide tổng kết
        5. Slide Q&A
        
        Mỗi slide trả về JSON format:
        {{
            "title": "Tiêu đề slide",
            "content": "Nội dung slide",
            "slide_type": "title/content/image/conclusion",
            "notes": "Ghi chú cho giáo viên"
        }}
        
        Trả về array các slides theo format trên.
        """
        
        messages = [SystemMessage(content=system_prompt)]
        response = await llm.ainvoke(messages)
        
        # Parse slides (simplified - would need better parsing)
        try:
            import json
            import re
            response_text = response.content
            logger.info(f"Raw slides response: {response_text}")
            
            try:
                slides = json.loads(response_text)
            except json.JSONDecodeError:
                # Try to extract JSON array
                json_match = re.search(r'\[[^\]]*\]', response_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    slides = json.loads(json_str)
                else:
                    raise ValueError("No JSON found")
        except:
            # Fallback if parsing fails
            slides = [
                {
                    "title": request.title,
                    "content": response.content,
                    "slide_type": "content",
                    "notes": "Nội dung được tạo tự động"
                }
            ]
        
        return {
            "slides": slides,
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error generating slide: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate/slide-from-lecture")
async def generate_slide_from_lecture(request: SlideFromLectureRequest):
    """Generate slides from lecture content"""
    try:
        system_prompt = f"""
        Hãy tạo slide thuyết trình từ nội dung bài giảng sau:
        
        Tiêu đề bài giảng: {request.lecture_title}
        Môn học: {request.lecture_subject}
        Nội dung: {request.lecture_content[:2000]}...
        
        Tùy chọn:
        - Slide giới thiệu: {request.include_intro}
        - Slide kết luận: {request.include_conclusion}
        - Slide câu hỏi: {request.include_questions}
        - Phong cách: {request.slide_style}
        
        Tạo 8-12 slides với format JSON như sau:
        [
            {{
                "title": "Tiêu đề slide",
                "content": "Nội dung slide",
                "slide_type": "title/content/conclusion/question",
                "notes": "Ghi chú"
            }}
        ]
        """
        
        messages = [SystemMessage(content=system_prompt)]
        response = await llm.ainvoke(messages)
        
        # Parse slides
        try:
            import json
            import re
            response_text = response.content
            logger.info(f"Raw lecture slides response: {response_text}")
            
            try:
                slides = json.loads(response_text)
            except json.JSONDecodeError:
                # Try to extract JSON array
                json_match = re.search(r'\[[^\]]*\]', response_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    slides = json.loads(json_str)
                else:
                    raise ValueError("No JSON found")
        except:
            slides = [
                {
                    "title": f"Slide: {request.lecture_title}",
                    "content": response.content,
                    "slide_type": "content",
                    "notes": "Được tạo từ bài giảng"
                }
            ]
        
        return {
            "slides": slides,
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error generating slide from lecture: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
