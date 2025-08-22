import axios from 'axios'

const API_BASE_URL = '/api/v1'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    console.log('API Request:', config.method?.toUpperCase(), config.url)
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
apiClient.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    console.error('API Error:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)

const chatService = {
  // Gửi tin nhắn chat
  sendMessage: (data) => {
    return apiClient.post('/chat/message', data)
  },

  // Lấy lịch sử chat
  getChatHistory: (sessionId) => {
    return apiClient.get(`/chat/history/${sessionId}`)
  },

  // Tạo session chat mới
  createSession: () => {
    return apiClient.post('/chat/session')
  },

  // Lấy danh sách sessions
  getSessions: () => {
    return apiClient.get('/chat/sessions')
  },

  // Xóa session
  deleteSession: (sessionId) => {
    return apiClient.delete(`/chat/session/${sessionId}`)
  }
}

export default chatService
