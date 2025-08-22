import axios from 'axios'

const API_BASE_URL = '/api/v1'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000, // Longer timeout cho việc tạo slides
  headers: {
    'Content-Type': 'application/json'
  }
})

const slideService = {
  // Tạo slide thuyết trình
  createSlides: (data) => {
    return apiClient.post('/slides/create', data)
  },

  // Lấy danh sách slides
  getSlides: (params = {}) => {
    return apiClient.get('/slides', { params })
  },

  // Lấy chi tiết slide
  getSlide: (slideId) => {
    return apiClient.get(`/slides/${slideId}`)
  },

  // Cập nhật slide
  updateSlide: (slideId, data) => {
    return apiClient.put(`/slides/${slideId}`, data)
  },

  // Xóa slide
  deleteSlide: (slideId) => {
    return apiClient.delete(`/slides/${slideId}`)
  },

  // Xuất slide ra file PowerPoint
  exportSlide: (slideId, format = 'pptx') => {
    return apiClient.get(`/slides/${slideId}/export`, {
      params: { format },
      responseType: 'blob'
    })
  },

  // Tạo slide từ bài giảng có sẵn
  createSlidesFromLecture: (lectureId, options = {}) => {
    return apiClient.post(`/slides/from-lecture/${lectureId}`, options)
  }
}

export default slideService
