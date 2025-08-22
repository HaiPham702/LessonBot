import { defineStore } from 'pinia'
import { ref } from 'vue'
import chatService from '../services/chatService'

export const useChatStore = defineStore('chat', () => {
  const messages = ref([])
  const sessions = ref([])
  const isLoading = ref(false)
  const currentSessionId = ref(null)

  const addMessage = (message) => {
    messages.value.push({
      id: Date.now(),
      ...message,
      timestamp: new Date()
    })
  }

  const sendMessage = async (content, metadata = null) => {
    try {
      isLoading.value = true
      
      // Thêm tin nhắn người dùng
      addMessage({
        content,
        sender: 'user',
        metadata: metadata || {}
      })

      // Gọi API chatbot
      const response = await chatService.sendMessage({
        message: content,
        sessionId: currentSessionId.value,
        metadata: metadata
      })

      // Thêm phản hồi của bot
      addMessage({
        content: response.data.reply,
        sender: 'bot',
        metadata: response.data.metadata || {}
      })

      // Cập nhật session ID nếu có
      if (response.data.sessionId) {
        currentSessionId.value = response.data.sessionId
        
        // Auto-generate title for new session based on first message
        const session = sessions.value.find(s => s.id === response.data.sessionId)
        if (session && (!session.title || session.title === 'Chat không tiêu đề')) {
          const title = content.length > 50 ? content.substring(0, 50) + '...' : content
          updateSessionTitle(response.data.sessionId, title)
        }
      }

    } catch (error) {
      console.error('Error sending message:', error)
      addMessage({
        content: 'Xin lỗi, có lỗi xảy ra. Vui lòng thử lại.',
        sender: 'bot',
        isError: true
      })
    } finally {
      isLoading.value = false
    }
  }

  const loadChatHistory = async (sessionId) => {
    try {
      const response = await chatService.getChatHistory(sessionId)
      messages.value = response.data.messages || []
      currentSessionId.value = sessionId
    } catch (error) {
      console.error('Error loading chat history:', error)
    }
  }

  const loadSessions = async () => {
    try {
      const response = await chatService.getSessions()
      sessions.value = response.data.sessions || []
    } catch (error) {
      console.error('Error loading sessions:', error)
    }
  }

  const createNewSession = async () => {
    try {
      const response = await chatService.createSession()
      const newSession = response.data
      sessions.value.unshift(newSession)
      return newSession.id
    } catch (error) {
      console.error('Error creating session:', error)
      return null
    }
  }

  const switchToSession = async (sessionId) => {
    if (sessionId === currentSessionId.value) return
    
    currentSessionId.value = sessionId
    await loadChatHistory(sessionId)
    
    // Cập nhật session as active
    sessions.value = sessions.value.map(session => ({
      ...session,
      isActive: session.id === sessionId
    }))
  }

  const clearChat = () => {
    messages.value = []
    currentSessionId.value = null
  }

  const updateSessionTitle = (sessionId, title) => {
    const session = sessions.value.find(s => s.id === sessionId)
    if (session) {
      session.title = title
    }
  }

  const deleteSession = async (sessionId) => {
    try {
      await chatService.deleteSession(sessionId)
      
      // Remove from sessions list
      sessions.value = sessions.value.filter(s => s.id !== sessionId)
      
      // If this was the current session, navigate to first available session
      if (sessionId === currentSessionId.value) {
        if (sessions.value.length > 0) {
          return sessions.value[0].id  // Return new session ID for navigation
        } else {
          clearChat()
          return null
        }
      }
      
      return true
    } catch (error) {
      console.error('Error deleting session:', error)
      return false
    }
  }

  return {
    messages,
    sessions,
    isLoading,
    currentSessionId,
    sendMessage,
    loadChatHistory,
    loadSessions,
    createNewSession,
    switchToSession,
    clearChat,
    addMessage,
    updateSessionTitle,
    deleteSession
  }
})
