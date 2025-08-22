# EduBot - Chatbot Hỗ trợ Giáo viên Soạn giảng

## 📖 Giới thiệu

EduBot là một ứng dụng AI chatbot được thiết kế để hỗ trợ giáo viên trong việc soạn giảng, tạo bài giảng chi tiết và thiết kế slide thuyết trình. Hệ thống sử dụng công nghệ LangGraph để xử lý các yêu cầu phức tạp và tạo ra nội dung giáo dục chất lượng cao.

## 🏗️ Kiến trúc hệ thống

### Tổng quan
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │     Backend     │    │     Agent       │
│   (Vue.js)      │◄──►│    (FastAPI)    │◄──►│   (LangGraph)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                        ┌─────────────────┐    ┌─────────────────┐
                        │    MongoDB      │    │ External APIs   │
                        │   (Database)    │    │  (Wikipedia,    │
                        └─────────────────┘    │   Educational)  │
                                              └─────────────────┘
```

### Thành phần chính

1. **Frontend (Vue.js + Vite)**
   - Giao diện người dùng
   - Chat interface
   - Quản lý bài giảng và slides
   - Tích hợp với backend qua REST API

2. **Backend (FastAPI)**
   - API endpoints cho chat, lectures, slides
   - Business logic và data processing
   - Tích hợp với MongoDB
   - Tool endpoints cho Agent

3. **Agent (LangGraph)**
   - Main Agent: Xử lý logic chính
   - External Agent: Gọi dịch vụ bên ngoài
   - Tools và workflows

4. **Database (MongoDB)**
   - Lưu trữ lịch sử chat
   - Quản lý bài giảng và slides
   - User data và metadata

## 🚀 Cài đặt và chạy

### Yêu cầu hệ thống
- Python 3.8+
- Node.js 16+
- Docker và Docker Compose
- MongoDB (hoặc chạy qua Docker)

### 1. Clone repository
```bash
git clone <repository-url>
cd edu-chatbot
```

### 2. Setup Database
```bash
cd database
docker-compose up -d
```

### 3. Setup Backend
```bash
cd backend
pip install -r requirements.txt

# Copy và cấu hình environment
cp env.example .env
# Chỉnh sửa .env với các thông tin cần thiết

# Chạy backend
python -m app.main
```

### 4. Setup Agent
```bash
cd agent
pip install -r requirements.txt

# Chạy main agent
python main_agent.py

# Chạy external agent (terminal khác)
python external_agent.py
```

### 5. Setup Frontend
```bash
cd frontend
npm install

# Chạy development server
npm run dev
```

### 6. Truy cập ứng dụng
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Main Agent: http://localhost:8001
- External Agent: http://localhost:8002
- MongoDB Express: http://localhost:8081

## 📱 Tính năng chính

### 1. Chat với AI
- Trò chuyện tự nhiên với AI chatbot
- Lưu lịch sử chat theo session
- Context-aware conversations

### 2. Tạo bài giảng
- Tạo bài giảng chi tiết từ yêu cầu
- Hỗ trợ nhiều môn học và cấp độ
- Auto-generate nội dung với AI
- Quản lý và chỉnh sửa bài giảng

### 3. Tạo slide thuyết trình
- Tạo slide từ requirements
- Tạo slide từ bài giảng có sẵn
- Nhiều template và style
- Export PowerPoint/PDF

### 4. Tìm kiếm và quản lý
- Tìm kiếm bài giảng và slides
- Phân loại theo môn học
- Lưu trữ và organize content

## 🔧 API Documentation

### Backend APIs

#### Chat APIs
- `POST /api/v1/chat/message` - Gửi tin nhắn
- `GET /api/v1/chat/history/{session_id}` - Lấy lịch sử chat
- `POST /api/v1/chat/session` - Tạo session mới

#### Lecture APIs  
- `POST /api/v1/lectures/create` - Tạo bài giảng
- `GET /api/v1/lectures` - Lấy danh sách bài giảng
- `GET /api/v1/lectures/{id}` - Lấy chi tiết bài giảng
- `PUT /api/v1/lectures/{id}` - Cập nhật bài giảng
- `DELETE /api/v1/lectures/{id}` - Xóa bài giảng

#### Slide APIs
- `POST /api/v1/slides/create` - Tạo slide
- `POST /api/v1/slides/from-lecture/{lecture_id}` - Tạo slide từ bài giảng
- `GET /api/v1/slides` - Lấy danh sách slides
- `GET /api/v1/slides/{id}` - Lấy chi tiết slide

### Agent APIs

#### Main Agent
- `POST /process` - Xử lý tin nhắn chính
- `POST /generate/lecture` - Sinh nội dung bài giảng
- `POST /generate/slide` - Sinh nội dung slide

#### External Agent
- `POST /search` - Tìm kiếm web
- `POST /enrich-content` - Làm giàu nội dung
- `POST /get-resources` - Lấy tài nguyên bên ngoài

## 🔒 Cấu hình bảo mật

### Environment Variables
```env
# Database
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=edubot

# Security
SECRET_KEY=your-super-secret-key

# OpenAI
OPENAI_API_KEY=your-openai-api-key

# Agent URLs
AGENT_MAIN_URL=http://localhost:8001
AGENT_EXTERNAL_URL=http://localhost:8002
```

## 📊 Database Schema

### Chat Sessions
```javascript
{
  _id: ObjectId,
  user_id: String,
  title: String,
  status: String, // active, archived, deleted
  created_at: Date,
  updated_at: Date,
  metadata: Object
}
```

### Chat Messages
```javascript
{
  _id: ObjectId,
  session_id: String,
  content: String,
  sender: String, // user, bot
  message_type: String,
  metadata: Object,
  created_at: Date
}
```

### Lectures
```javascript
{
  _id: ObjectId,
  user_id: String,
  title: String,
  subject: String,
  grade: String,
  description: String,
  requirements: String,
  content: String,
  status: String, // draft, generating, completed, error
  created_at: Date,
  updated_at: Date
}
```

### Slides
```javascript
{
  _id: ObjectId,
  user_id: String,
  title: String,
  subject: String,
  presentation_type: String,
  duration: Number,
  slides: [
    {
      title: String,
      content: String,
      slide_type: String,
      notes: String
    }
  ],
  slide_count: Number,
  status: String,
  source_lecture_id: String
}
```

## 🧪 Testing

### Backend Testing
```bash
cd backend
pytest tests/
```

### Frontend Testing
```bash
cd frontend
npm run test
```

### Agent Testing
```bash
cd agent
python -m pytest tests/
```

## 🚀 Deployment

### Docker Deployment
```bash
# Build và chạy toàn bộ stack
docker-compose up -d

# Scale services
docker-compose up -d --scale backend=2 --scale agent=2
```

### Production Considerations
- Sử dụng reverse proxy (Nginx)
- SSL/TLS certificates
- Environment variables cho production
- Monitoring và logging
- Database backup strategy

## 🤝 Contributing

1. Fork repository
2. Tạo feature branch
3. Commit changes
4. Push và tạo Pull Request

### Code Style
- Python: Black formatter, flake8 linter
- JavaScript: ESLint, Prettier
- Commit messages: Conventional Commits

## 📝 License

MIT License - xem file LICENSE để biết thêm chi tiết.

## 📞 Support

- Issues: Tạo issue trên GitHub
- Documentation: Xem thêm trong thư mục `docs/`
- API Docs: http://localhost:8000/docs (khi chạy backend)

## 🔄 Roadmap

### Version 1.1
- [ ] User authentication và authorization
- [ ] Advanced slide templates
- [ ] Collaborative editing
- [ ] Export formats (Word, PDF)

### Version 1.2
- [ ] Multi-language support
- [ ] Advanced AI features
- [ ] Integration với LMS
- [ ] Mobile app

### Version 2.0
- [ ] Real-time collaboration
- [ ] Advanced analytics
- [ ] AI-powered content recommendations
- [ ] Plugin system
