// MongoDB initialization script for EduBot
print('Initializing EduBot database...');

// Switch to edubot database
db = db.getSiblingDB('edubot');

// Create collections with initial setup
print('Creating collections...');

// Chat sessions collection
db.createCollection('chat_sessions');
db.chat_sessions.createIndex({ user_id: 1 });
db.chat_sessions.createIndex({ created_at: -1 });
db.chat_sessions.createIndex({ status: 1 });

// Chat messages collection
db.createCollection('chat_messages');
db.chat_messages.createIndex({ session_id: 1, created_at: 1 });
db.chat_messages.createIndex({ sender: 1 });

// Lectures collection
db.createCollection('lectures');
db.lectures.createIndex({ user_id: 1 });
db.lectures.createIndex({ subject: 1 });
db.lectures.createIndex({ created_at: -1 });
db.lectures.createIndex({ status: 1 });
db.lectures.createIndex({ title: "text", description: "text" });

// Slides collection
db.createCollection('slides');
db.slides.createIndex({ user_id: 1 });
db.slides.createIndex({ subject: 1 });
db.slides.createIndex({ created_at: -1 });
db.slides.createIndex({ status: 1 });
db.slides.createIndex({ source_lecture_id: 1 });
db.slides.createIndex({ title: "text", description: "text" });

// Users collection (optional for future use)
db.createCollection('users');
db.users.createIndex({ email: 1 }, { unique: true });
db.users.createIndex({ created_at: -1 });

// Insert sample data for testing
print('Inserting sample data...');

// Sample user
const sampleUserId = "user_test_001";

// Sample chat session
const sessionResult = db.chat_sessions.insertOne({
  user_id: sampleUserId,
  title: "Chat thử nghiệm",
  status: "active",
  created_at: new Date(),
  updated_at: new Date(),
  metadata: {
    sample: true
  }
});

const sessionId = sessionResult.insertedId.toString();

// Sample chat messages
db.chat_messages.insertMany([
  {
    session_id: sessionId,
    content: "Xin chào, tôi muốn tạo bài giảng về toán học",
    sender: "user",
    message_type: "text",
    metadata: {},
    created_at: new Date()
  },
  {
    session_id: sessionId,
    content: "Chào bạn! Tôi có thể giúp bạn tạo bài giảng toán học. Bạn muốn tạo bài giảng về chủ đề gì cụ thể?",
    sender: "bot",
    message_type: "text",
    metadata: {},
    created_at: new Date()
  }
]);

// Sample lecture
db.lectures.insertOne({
  user_id: sampleUserId,
  title: "Giới thiệu về Đại số",
  subject: "Toán học",
  grade: "high",
  description: "Bài giảng giới thiệu các khái niệm cơ bản về đại số",
  requirements: "Học sinh cần nắm được các phép tính cơ bản và hiểu về biến số",
  content: `# Giới thiệu về Đại số

## Mục tiêu học tập
- Hiểu khái niệm về biến số
- Nắm được các phép tính đại số cơ bản
- Áp dụng được vào giải bài tập

## Nội dung chính

### 1. Khái niệm biến số
Biến số là một ký hiệu (thường là chữ cái) đại diện cho một giá trị chưa biết...

### 2. Các phép tính cơ bản
- Phép cộng và trừ
- Phép nhân và chia
- Luỹ thừa

### 3. Ví dụ thực tế
[Các ví dụ minh họa]

## Bài tập
1. Tính giá trị biểu thức...
2. Giải phương trình...

## Tài liệu tham khảo
- Sách giáo khoa Toán học lớp 9
- Tài liệu bổ trợ về đại số`,
  status: "completed",
  created_at: new Date(),
  updated_at: new Date(),
  metadata: {
    sample: true,
    auto_generated: true
  }
});

// Sample slide
db.slides.insertOne({
  user_id: sampleUserId,
  title: "Slide Giới thiệu Đại số",
  subject: "Toán học",
  presentation_type: "lecture",
  duration: 45,
  description: "Slide thuyết trình về các khái niệm cơ bản của đại số",
  requirements: "Tạo slide sinh động, dễ hiểu cho học sinh THPT",
  slides: [
    {
      title: "Giới thiệu về Đại số",
      content: "Chào mừng đến với bài học về Đại số\n\nMôn học: Toán học\nCấp độ: THPT",
      slide_type: "title",
      notes: "Slide mở đầu, giới thiệu chủ đề"
    },
    {
      title: "Mục tiêu học tập",
      content: "Sau bài học này, học sinh sẽ:\n• Hiểu khái niệm biến số\n• Nắm được các phép tính đại số\n• Áp dụng vào bài tập thực tế",
      slide_type: "content",
      notes: "Nêu rõ mục tiêu để học sinh biết được sẽ học gì"
    },
    {
      title: "Biến số là gì?",
      content: "Biến số là ký hiệu đại diện cho giá trị chưa biết\n\nVí dụ: x, y, a, b...\n\nThí dụ: x + 3 = 7\nTìm x = ?",
      slide_type: "content",
      notes: "Giải thích khái niệm cơ bản với ví dụ đơn giản"
    }
  ],
  slide_count: 3,
  status: "completed",
  created_at: new Date(),
  updated_at: new Date(),
  metadata: {
    sample: true,
    auto_generated: true
  }
});

print('Database initialization completed successfully!');
print('Collections created:');
print('- chat_sessions');
print('- chat_messages'); 
print('- lectures');
print('- slides');
print('- users');
print('');
print('Sample data inserted for testing.');
print('You can now start the application and test the functionality.');
