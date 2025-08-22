# 🤖 EduBot - Chatbot Hỗ trợ Giáo viên Soạn giảng

## 📝 Tổng quan

EduBot là một ứng dụng AI chatbot tiên tiến được thiết kế đặc biệt để hỗ trợ giáo viên trong công việc soạn giảng. Sử dụng công nghệ LangGraph và OpenAI, EduBot có thể:

- 🎯 **Tạo bài giảng chi tiết** từ yêu cầu của giáo viên
- 📊 **Thiết kế slide thuyết trình** chuyên nghiệp
- 💬 **Tư vấn phương pháp giảng dạy** thông qua chat AI
- 🔍 **Tìm kiếm và quản lý** tài liệu giảng dạy

## 🏗️ Kiến trúc Monorepo

```
edu-chatbot/
├── frontend/          # Vue.js + Vite - Giao diện người dùng
├── backend/           # FastAPI - REST API và business logic  
├── agent/             # LangGraph - AI agents và workflows
├── database/          # MongoDB setup và initialization
├── docs/              # Documentation và hướng dẫn
└── docker-compose.yml # Orchestration toàn dự án
```

## 🚀 Quick Start

### 1. Prerequisites
```bash
# Cài đặt các dependency cần thiết
- Python 3.8+
- Node.js 16+  
- Docker & Docker Compose
- OpenAI API Key
```

### 2. Clone và Setup
```bash
# Clone repository
git clone <your-repo-url>
cd edu-chatbot

# Khởi động database
cd database && docker-compose up -d

# Setup backend
cd ../backend
pip install -r requirements.txt
cp env.example .env  # Cấu hình environment variables
python -m app.main   # Chạy backend (port 8000)

# Setup agents (cần 2 terminal)
cd ../agent
pip install -r requirements.txt
python main_agent.py     # Terminal 1: Main agent (port 8001)
python external_agent.py # Terminal 2: External agent (port 8002)

# Setup frontend
cd ../frontend
npm install
npm run dev  # Chạy frontend (port 3000)
```

### 3. Truy cập ứng dụng
- 🌐 **Frontend**: http://localhost:3000
- 🔧 **Backend API**: http://localhost:8000/docs
- 🤖 **Main Agent**: http://localhost:8001/docs
- 🌍 **External Agent**: http://localhost:8002/docs
- 📊 **MongoDB Express**: http://localhost:8081

## ✨ Tính năng chính

### 💬 Chat với AI Giáo dục
- Trò chuyện tự nhiên với AI chuyên về giáo dục
- Tư vấn phương pháp giảng dạy
- Gợi ý nội dung và hoạt động học tập
- Lưu lịch sử chat theo session

### 📚 Tạo Bài giảng Tự động
- Input: Tiêu đề, môn học, cấp độ, yêu cầu chi tiết
- Output: Bài giảng đầy đủ với cấu trúc chuyên nghiệp
- Bao gồm: Mục tiêu, nội dung, phương pháp, bài tập, tài liệu tham khảo
- Hỗ trợ nhiều môn học: Toán, Lý, Hóa, Văn, Anh, v.v.

### 🎯 Thiết kế Slide Thuyết trình
- Tạo slide từ requirements hoặc từ bài giảng có sẵn
- Nhiều template: Professional, Creative, Minimal
- Auto-generate 10-15 slides với nội dung phù hợp
- Export PowerPoint (.pptx) và PDF

### 🔍 Quản lý Nội dung
- Tìm kiếm bài giảng và slides đã tạo
- Phân loại theo môn học và cấp độ
- Chỉnh sửa và cập nhật nội dung
- Chia sẻ và export tài liệu

## 🔧 Công nghệ sử dụng

### Frontend Stack
- **Vue.js 3** - Progressive framework
- **Vite** - Build tool và dev server
- **Pinia** - State management
- **Axios** - HTTP client

### Backend Stack  
- **FastAPI** - Modern Python web framework
- **MongoDB** - NoSQL database
- **Motor** - Async MongoDB driver
- **Pydantic** - Data validation

### AI/Agent Stack
- **LangGraph** - Agent workflow framework
- **LangChain** - LLM application framework  
- **OpenAI GPT** - Large language model
- **HTTPX** - Async HTTP client

## 📖 Documentation

- [📘 Chi tiết Documentation](./docs/README.md)
- [🏗️ Kiến trúc hệ thống](./docs/architecture.md)
- [🔌 API Reference](./docs/api.md)
- [🚀 Deployment Guide](./docs/deployment.md)

## 🔧 Configuration

### Environment Variables
```env
# Backend (.env)
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=edubot
SECRET_KEY=your-secret-key
OPENAI_API_KEY=your-openai-api-key
AGENT_MAIN_URL=http://localhost:8001
AGENT_EXTERNAL_URL=http://localhost:8002

# Frontend (vite.config.js)
VITE_API_BASE_URL=http://localhost:3000/api/v1/
```

## 📊 Example Usage

### Tạo bài giảng qua Chat
```
User: "Tôi muốn tạo bài giảng về phương trình bậc hai cho học sinh lớp 9"

Bot: "Tôi sẽ tạo bài giảng về phương trình bậc hai cho bạn. Bài giảng sẽ bao gồm:
- Khái niệm và dạng tổng quát
- Công thức nghiệm và biệt thức delta  
- Ví dụ minh họa
- Bài tập thực hành
Bài giảng đang được tạo và sẽ sẵn sàng trong vài phút."
```

### Tạo slide từ bài giảng
```javascript
// API call
POST /api/v1/slides/from-lecture/64f8b2a1c9d4e123456789ab
{
  "include_intro": true,
  "include_conclusion": true, 
  "include_questions": true,
  "slide_style": "professional"
}
```

## 🧪 Testing

```bash
# Test backend
cd backend && python -m pytest

# Test frontend  
cd frontend && npm run test

# Test agents
cd agent && python -m pytest
```

## 🚀 Production Deployment

```bash
# Using Docker Compose
docker-compose -f docker-compose.prod.yml up -d

# Manual deployment
# 1. Setup production database
# 2. Deploy backend với gunicorn
# 3. Deploy frontend build 
# 4. Setup nginx reverse proxy
# 5. Configure SSL certificates
```

## 🤝 Contributing

1. Fork repository
2. Tạo feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push branch: `git push origin feature/amazing-feature`
5. Tạo Pull Request

## 📝 License

Dự án được phân phối dưới giấy phép MIT. Xem file `LICENSE` để biết thêm chi tiết.

## 📞 Support & Contact

- 🐛 **Bug Reports**: Tạo issue trên GitHub
- 💡 **Feature Requests**: GitHub Discussions
- 📧 **Email Support**: support@edubot.com
- 📚 **Documentation**: [docs.edubot.com](./docs/)

## 🎯 Roadmap

### ✅ Version 1.0 (Current)
- [x] Chat interface với AI
- [x] Tạo bài giảng tự động
- [x] Thiết kế slide thuyết trình  
- [x] Quản lý nội dung cơ bản

### 🔄 Version 1.1 (Planning)
- [ ] User authentication & authorization
- [ ] Advanced slide templates
- [ ] Export nhiều formats (Word, PDF)
- [ ] Collaborative editing

### 🚀 Version 2.0 (Future)
- [ ] Mobile app
- [ ] Multi-language support
- [ ] Integration với LMS
- [ ] Advanced analytics & insights

---

<div align="center">
  <strong>Made with ❤️ for Vietnamese educators</strong>
  <br>
  <em>Hỗ trợ giáo viên Việt Nam trong kỷ nguyên số</em>
</div>
