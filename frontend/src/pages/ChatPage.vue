<template>
  <div class="chat-page">
    <!-- Sidebar -->
    <div class="sidebar" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
      <div class="sidebar-header">
        <h3 v-if="!sidebarCollapsed">💬 Phiên Chat</h3>
        <button @click="toggleSidebar" class="sidebar-toggle">
          {{ sidebarCollapsed ? '→' : '←' }}
        </button>
      </div>
      
      <div class="sidebar-content" v-if="!sidebarCollapsed">
        <button @click="createNewChat" class="new-chat-button">
          ➕ Chat mới
        </button>
        
        <div class="sessions-list">
          <div
            v-for="session in sessions"
            :key="session.id"
            :class="['session-item', { active: session.id === currentSessionId }]"
          >
            <div class="session-content" @click="selectSession(session.id)">
              <div class="session-title">
                {{ session.title || 'Chat không tiêu đề' }}
              </div>
              <div class="session-time">
                {{ formatSessionTime(session.updated_at || session.created_at) }}
              </div>
            </div>
            <div class="session-actions">
              <button 
                @click.stop="confirmDeleteSession(session.id)"
                class="delete-button"
                title="Xóa phiên chat"
              >
                🗑️
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Chat Area -->
    <div class="main-content">
      <div class="chat-header">
        <h1>🤖 Trợ lý Soạn giảng AI</h1>
        <p>Hỏi tôi bất cứ điều gì về việc tạo bài giảng và slide thuyết trình!</p>
      </div>

      <div class="chat-container">
      <div class="chat-messages" ref="messagesContainer">
        <div v-if="messages.length === 0" class="welcome-message">
          <div class="welcome-content">
            <h3>👋 Xin chào!</h3>
            <p>Tôi có thể giúp bạn:</p>
            <ul>
              <li>📚 Tạo bài giảng chi tiết</li>
              <li>🎯 Soạn slide thuyết trình</li>
              <li>💡 Gợi ý nội dung giảng dạy</li>
              <li>📝 Tối ưu hóa phương pháp giảng dạy</li>
            </ul>
            <p><strong>Hãy bắt đầu bằng cách mô tả chủ đề bạn muốn soạn giảng!</strong></p>
          </div>
        </div>

        <div
          v-for="message in messages"
          :key="message.id"
          :class="['message', message.sender]"
        >
          <div class="message-content">
            <!-- Regular text message -->
            <div v-if="!isLectureMessage(message)" class="message-text" v-html="formatMessage(message.content)"></div>
            
            <!-- Lecture outline message -->
            <div v-else class="lecture-outline">
              <LectureOutline 
                :lecture-data="message.metadata.lecture_data"
                :editable="message.metadata.editable"
                @update-lecture="updateLecture"
                @create-slide="createSlideFromLecture"
              />
            </div>
            
            <div class="message-time">
              {{ formatTime(message.timestamp) }}
            </div>
          </div>
        </div>

        <div v-if="isLoading" class="message bot">
          <div class="message-content">
            <div class="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        </div>
      </div>

      <div class="chat-input-container">
        <form @submit.prevent="handleSendMessage" class="chat-form">
          <textarea
            v-model="inputMessage"
            placeholder="Nhập câu hỏi hoặc yêu cầu của bạn..."
            class="chat-input"
            @keydown.enter.prevent="handleSendMessage"
            :disabled="isLoading"
            rows="3"
          ></textarea>
          <button
            type="submit"
            class="send-button"
            :disabled="!inputMessage.trim() || isLoading"
          >
            📤 Gửi
          </button>
        </form>
      </div>
    </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useChatStore } from '../store/chat'
import { storeToRefs } from 'pinia'
import LectureOutline from '../components/LectureOutline.vue'

// Props from router
const props = defineProps({
  sessionId: String
})

const route = useRoute()
const router = useRouter()
const chatStore = useChatStore()
const { messages, sessions, isLoading, currentSessionId } = storeToRefs(chatStore)

const inputMessage = ref('')
const messagesContainer = ref(null)
const sidebarCollapsed = ref(false)

const handleSendMessage = async () => {
  if (!inputMessage.value.trim() || isLoading.value) return

  const message = inputMessage.value.trim()
  inputMessage.value = ''

  await chatStore.sendMessage(message)
  await scrollToBottom()
}

const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

const formatMessage = (content) => {
  // Chuyển đổi markdown cơ bản
  return content
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`(.*?)`/g, '<code>$1</code>')
    .replace(/\n/g, '<br>')
}

const formatTime = (timestamp) => {
  if (!timestamp) return ''
  return new Date(timestamp).toLocaleTimeString('vi-VN', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatSessionTime = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now - date
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  
  if (days === 0) {
    return date.toLocaleTimeString('vi-VN', {
      hour: '2-digit',
      minute: '2-digit'
    })
  } else if (days === 1) {
    return 'Hôm qua'
  } else if (days < 7) {
    return `${days} ngày trước`
  } else {
    return date.toLocaleDateString('vi-VN')
  }
}

const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

const createNewChat = async () => {
  const newSessionId = await chatStore.createNewSession()
  if (newSessionId) {
    router.push(`/chat/${newSessionId}`)
  }
}

const selectSession = async (sessionId) => {
  if (sessionId !== currentSessionId.value) {
    router.push(`/chat/${sessionId}`)
  }
}

const confirmDeleteSession = async (sessionId) => {
  const session = sessions.value.find(s => s.id === sessionId)
  const sessionTitle = session?.title || 'Chat không tiêu đề'
  
  if (confirm(`Bạn có chắc chắn muốn xóa phiên chat "${sessionTitle}"?`)) {
    const result = await chatStore.deleteSession(sessionId)
    
    if (result === false) {
      alert('Có lỗi xảy ra khi xóa phiên chat. Vui lòng thử lại.')
      return
    }
    
    // If current session was deleted, navigate to new session or home
    if (result && typeof result === 'string') {
      router.push(`/chat/${result}`)
    } else if (result === null) {
      router.push('/')
    }
  }
}

const isLectureMessage = (message) => {
  return message.metadata && message.metadata.type === 'lecture'
}

const updateLecture = (updatedLectureData, messageId) => {
  // Update lecture data in message
  const message = messages.value.find(m => m.id === messageId)
  if (message && message.metadata) {
    message.metadata.lecture_data = updatedLectureData
  }
}

const createSlideFromLecture = async (lectureData) => {
  // Send request to create slide from lecture
  const slideMessage = `Tạo slide PowerPoint từ dàn ý bài giảng: ${lectureData.title}`
  
  await chatStore.sendMessage(slideMessage, {
    type: 'create_slide_from_lecture',
    lecture_data: lectureData
  })
  
  await scrollToBottom()
}

// Watch for route changes
watch(() => route.params.sessionId, async (newSessionId) => {
  if (newSessionId && newSessionId !== currentSessionId.value) {
    await chatStore.switchToSession(newSessionId)
    await scrollToBottom()
  }
}, { immediate: true })

onMounted(async () => {
  // Load sessions
  await chatStore.loadSessions()
  
  // Load current session if provided in route
  const sessionId = route.params.sessionId || props.sessionId
  if (sessionId) {
    await chatStore.switchToSession(sessionId)
  } else if (sessions.value.length > 0) {
    // Navigate to most recent session
    router.replace(`/chat/${sessions.value[0].id}`)
  }
  
  await scrollToBottom()
})
</script>

<style scoped>
.chat-page {
  height: calc(100vh - 100px);
  display: flex;
}

.sidebar {
  width: 280px;
  background: #2c3e50;
  color: white;
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
}

.sidebar-collapsed {
  width: 60px;
}

.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid #34495e;
}

.sidebar-header h3 {
  margin: 0;
  font-size: 1.1rem;
}

.sidebar-toggle {
  background: none;
  border: none;
  color: white;
  cursor: pointer;
  font-size: 1.2rem;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.sidebar-toggle:hover {
  background: #34495e;
}

.sidebar-content {
  flex: 1;
  padding: 1rem;
  overflow-y: auto;
}

.new-chat-button {
  width: 100%;
  padding: 0.75rem;
  background: #3498db;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  margin-bottom: 1rem;
  font-size: 0.9rem;
  transition: background-color 0.2s;
}

.new-chat-button:hover {
  background: #2980b9;
}

.sessions-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.session-item {
  background: #34495e;
  border-radius: 8px;
  transition: background-color 0.2s;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.session-item:hover {
  background: #4a5f7a;
}

.session-item.active {
  background: #3498db;
}

.session-content {
  flex: 1;
  padding: 0.75rem;
  cursor: pointer;
}

.session-title {
  font-weight: 500;
  margin-bottom: 0.25rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.session-time {
  font-size: 0.75rem;
  opacity: 0.7;
}

.session-actions {
  padding: 0.5rem;
  display: flex;
  gap: 0.25rem;
}

.delete-button {
  background: none;
  border: none;
  color: #e74c3c;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 4px;
  font-size: 0.9rem;
  transition: all 0.2s;
  opacity: 0.7;
}

.delete-button:hover {
  opacity: 1;
  background: rgba(231, 76, 60, 0.1);
  transform: scale(1.1);
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.chat-header {
  text-align: center;
  margin-bottom: 2rem;
  padding: 1rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 8px;
}

.chat-header h1 {
  margin: 0 0 0.5rem 0;
  font-size: 2rem;
}

.chat-header p {
  margin: 0;
  opacity: 0.9;
}

.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  border: 1px solid #e1e8ed;
  border-radius: 8px;
  overflow: hidden;
  background: white;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  background: #f8f9fa;
}

.welcome-message {
  text-align: center;
}

.welcome-content {
  max-width: 500px;
  margin: 0 auto;
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.welcome-content h3 {
  color: #2c3e50;
  margin-bottom: 1rem;
}

.welcome-content ul {
  text-align: left;
  margin: 1rem 0;
}

.welcome-content li {
  margin: 0.5rem 0;
  color: #555;
}

.message {
  margin-bottom: 1rem;
  display: flex;
}

.message.user {
  justify-content: flex-end;
}

.message.bot {
  justify-content: flex-start;
}

.message-content {
  max-width: 80%;
  padding: 0.75rem 1rem;
  border-radius: 18px;
  position: relative;
}

.message.user .message-content {
  background: #007bff;
  color: white;
}

.message.bot .message-content {
  background: white;
  color: #333;
  border: 1px solid #e1e8ed;
}

.message-text {
  line-height: 1.4;
}

.lecture-outline {
  max-width: 100%;
  overflow-x: auto;
}

.message-time {
  font-size: 0.75rem;
  opacity: 0.6;
  margin-top: 0.25rem;
}

.typing-indicator {
  display: flex;
  gap: 4px;
  align-items: center;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #999;
  animation: typing 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
.typing-indicator span:nth-child(2) { animation-delay: -0.16s; }

@keyframes typing {
  0%, 80%, 100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}

.chat-input-container {
  padding: 1rem;
  background: white;
  border-top: 1px solid #e1e8ed;
}

.chat-form {
  display: flex;
  gap: 1rem;
  align-items: flex-end;
}

.chat-input {
  flex: 1;
  border: 1px solid #ddd;
  border-radius: 20px;
  padding: 0.75rem 1rem;
  resize: none;
  font-family: inherit;
  line-height: 1.4;
}

.chat-input:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
}

.send-button {
  border-radius: 20px;
  padding: 0.75rem 1.5rem;
  background: #007bff;
  color: white;
  border: none;
  cursor: pointer;
  transition: background-color 0.2s;
}

.send-button:hover:not(:disabled) {
  background: #0056b3;
}

.send-button:disabled {
  background: #ccc;
  cursor: not-allowed;
}

/* Responsive */
@media (max-width: 768px) {
  .sidebar {
    width: 100%;
    height: auto;
    position: fixed;
    top: 0;
    left: 0;
    z-index: 1000;
    transform: translateX(-100%);
  }
  
  .sidebar:not(.sidebar-collapsed) {
    transform: translateX(0);
  }
  
  .main-content {
    width: 100%;
  }
}
</style>
