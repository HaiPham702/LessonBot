import axios from 'axios'

const API_BASE_URL = '/api/v1'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000, // Longer timeout cho việc tạo lecture
  headers: {
    'Content-Type': 'application/json'
  }
})

const lectureService = {
  // Tạo bài giảng
  createLecture: (data) => {
    return apiClient.post('/lectures/create', data)
  },

  // Lấy danh sách bài giảng
  getLectures: (params = {}) => {
    return apiClient.get('/lectures', { params })
  },

  // Lấy chi tiết bài giảng
  getLecture: (lectureId) => {
    return apiClient.get(`/lectures/${lectureId}`)
  },

  // Cập nhật bài giảng
  updateLecture: (lectureId, data) => {
    return apiClient.put(`/lectures/${lectureId}`, data)
  },

  // Xóa bài giảng
  deleteLecture: (lectureId) => {
    return apiClient.delete(`/lectures/${lectureId}`)
  },

  // Xuất bài giảng ra file
  exportLecture: (lectureId, format = 'pdf') => {
    return apiClient.get(`/lectures/${lectureId}/export`, {
      params: { format },
      responseType: 'blob'
    })
  }
}

export default lectureService
