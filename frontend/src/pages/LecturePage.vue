<template>
  <div class="lecture-page">
    <div class="page-header">
      <h1>📚 Quản lý Bài giảng</h1>
      <button @click="showCreateModal = true" class="create-button">
        ➕ Tạo bài giảng mới
      </button>
    </div>

    <div class="lectures-grid" v-if="lectures.length > 0">
      <div
        v-for="lecture in lectures"
        :key="lecture.id"
        class="lecture-card"
        @click="viewLecture(lecture)"
      >
        <div class="lecture-header">
          <h3>{{ lecture.title }}</h3>
          <div class="lecture-actions">
            <button @click.stop="editLecture(lecture)" class="action-btn edit">✏️</button>
            <button @click.stop="deleteLecture(lecture.id)" class="action-btn delete">🗑️</button>
          </div>
        </div>
        <p class="lecture-subject">{{ lecture.subject }}</p>
        <p class="lecture-description">{{ lecture.description }}</p>
        <div class="lecture-meta">
          <span class="lecture-date">{{ formatDate(lecture.createdAt) }}</span>
          <span class="lecture-status" :class="lecture.status">{{ lecture.status }}</span>
        </div>
      </div>
    </div>

    <div v-else class="empty-state">
      <div class="empty-content">
        <h3>📝 Chưa có bài giảng nào</h3>
        <p>Bắt đầu tạo bài giảng đầu tiên của bạn!</p>
        <button @click="showCreateModal = true" class="create-button">
          Tạo bài giảng mới
        </button>
      </div>
    </div>

    <!-- Modal tạo/chỉnh sửa bài giảng -->
    <div v-if="showCreateModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>{{ editingLecture ? 'Chỉnh sửa bài giảng' : 'Tạo bài giảng mới' }}</h2>
          <button @click="closeModal" class="close-btn">✕</button>
        </div>
        
        <form @submit.prevent="handleSubmit" class="lecture-form">
          <div class="form-group">
            <label for="title">Tiêu đề bài giảng *</label>
            <input
              id="title"
              v-model="lectureForm.title"
              type="text"
              placeholder="VD: Giới thiệu về Toán học"
              required
            />
          </div>

          <div class="form-group">
            <label for="subject">Môn học *</label>
            <input
              id="subject"
              v-model="lectureForm.subject"
              type="text"
              placeholder="VD: Toán học, Vật lý, Hóa học..."
              required
            />
          </div>

          <div class="form-group">
            <label for="grade">Lớp/Cấp độ</label>
            <select id="grade" v-model="lectureForm.grade">
              <option value="">Chọn cấp độ</option>
              <option value="elementary">Tiểu học</option>
              <option value="middle">THCS</option>
              <option value="high">THPT</option>
              <option value="university">Đại học</option>
            </select>
          </div>

          <div class="form-group">
            <label for="description">Mô tả ngắn</label>
            <textarea
              id="description"
              v-model="lectureForm.description"
              rows="3"
              placeholder="Mô tả ngắn gọn về nội dung bài giảng..."
            ></textarea>
          </div>

          <div class="form-group">
            <label for="requirements">Yêu cầu chi tiết *</label>
            <textarea
              id="requirements"
              v-model="lectureForm.requirements"
              rows="6"
              placeholder="Mô tả chi tiết yêu cầu cho bài giảng:
- Các chủ đề chính cần đề cập
- Mục tiêu học tập
- Phương pháp giảng dạy mong muốn
- Thời lượng dự kiến
- Đối tượng học sinh..."
              required
            ></textarea>
          </div>

          <div class="form-actions">
            <button type="button" @click="closeModal" class="cancel-btn">
              Hủy
            </button>
            <button type="submit" :disabled="isCreating" class="submit-btn">
              {{ isCreating ? 'Đang tạo...' : (editingLecture ? 'Cập nhật' : 'Tạo bài giảng') }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Modal xem chi tiết bài giảng -->
    <div v-if="viewingLecture" class="modal-overlay" @click="closeViewModal">
      <div class="modal-content large" @click.stop>
        <div class="modal-header">
          <h2>{{ viewingLecture.title }}</h2>
          <div class="header-actions">
            <button @click="exportLecture(viewingLecture.id)" class="export-btn">
              📥 Xuất file
            </button>
            <button @click="closeViewModal" class="close-btn">✕</button>
          </div>
        </div>
        
        <div class="lecture-content">
          <div class="lecture-info">
            <p><strong>Môn học:</strong> {{ viewingLecture.subject }}</p>
            <p><strong>Cấp độ:</strong> {{ getGradeLabel(viewingLecture.grade) }}</p>
            <p><strong>Ngày tạo:</strong> {{ formatDate(viewingLecture.createdAt) }}</p>
            <p><strong>Mô tả:</strong> {{ viewingLecture.description }}</p>
          </div>
          
          <div class="lecture-body" v-html="formatLectureContent(viewingLecture.content)">
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import lectureService from '../services/lectureService'

const lectures = ref([])
const showCreateModal = ref(false)
const editingLecture = ref(null)
const viewingLecture = ref(null)
const isCreating = ref(false)

const lectureForm = ref({
  title: '',
  subject: '',
  grade: '',
  description: '',
  requirements: ''
})

const loadLectures = async () => {
  try {
    const response = await lectureService.getLectures()
    lectures.value = response.data.lectures || []
  } catch (error) {
    console.error('Error loading lectures:', error)
    alert('Không thể tải danh sách bài giảng')
  }
}

const handleSubmit = async () => {
  try {
    isCreating.value = true
    
    if (editingLecture.value) {
      await lectureService.updateLecture(editingLecture.value.id, lectureForm.value)
    } else {
      await lectureService.createLecture(lectureForm.value)
    }
    
    await loadLectures()
    closeModal()
    
    alert(editingLecture.value ? 'Cập nhật bài giảng thành công!' : 'Tạo bài giảng thành công!')
  } catch (error) {
    console.error('Error creating/updating lecture:', error)
    alert('Có lỗi xảy ra. Vui lòng thử lại.')
  } finally {
    isCreating.value = false
  }
}

const editLecture = (lecture) => {
  editingLecture.value = lecture
  lectureForm.value = { ...lecture }
  showCreateModal.value = true
}

const viewLecture = async (lecture) => {
  try {
    const response = await lectureService.getLecture(lecture.id)
    viewingLecture.value = response.data
  } catch (error) {
    console.error('Error loading lecture:', error)
    alert('Không thể tải chi tiết bài giảng')
  }
}

const deleteLecture = async (lectureId) => {
  if (!confirm('Bạn có chắc chắn muốn xóa bài giảng này?')) return
  
  try {
    await lectureService.deleteLecture(lectureId)
    await loadLectures()
    alert('Xóa bài giảng thành công!')
  } catch (error) {
    console.error('Error deleting lecture:', error)
    alert('Không thể xóa bài giảng')
  }
}

const exportLecture = async (lectureId) => {
  try {
    const response = await lectureService.exportLecture(lectureId)
    
    // Tạo link download
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `bai-giang-${lectureId}.pdf`)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
  } catch (error) {
    console.error('Error exporting lecture:', error)
    alert('Không thể xuất file bài giảng')
  }
}

const closeModal = () => {
  showCreateModal.value = false
  editingLecture.value = null
  lectureForm.value = {
    title: '',
    subject: '',
    grade: '',
    description: '',
    requirements: ''
  }
}

const closeViewModal = () => {
  viewingLecture.value = null
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('vi-VN')
}

const formatLectureContent = (content) => {
  if (!content) return '<p>Đang tải nội dung...</p>'
  
  return content
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/\n/g, '<br>')
}

const getGradeLabel = (grade) => {
  const labels = {
    elementary: 'Tiểu học',
    middle: 'THCS',
    high: 'THPT',
    university: 'Đại học'
  }
  return labels[grade] || 'Không xác định'
}

onMounted(() => {
  loadLectures()
})
</script>

<style scoped>
.lecture-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #e9ecef;
}

.page-header h1 {
  margin: 0;
  color: #2c3e50;
}

.create-button {
  background: #28a745;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.2s;
}

.create-button:hover {
  background: #218838;
}

.lectures-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.lecture-card {
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 12px;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.lecture-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.lecture-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.lecture-header h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.25rem;
}

.lecture-actions {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 4px;
  font-size: 1.1rem;
}

.action-btn:hover {
  background: #f8f9fa;
}

.lecture-subject {
  color: #6c757d;
  font-weight: 500;
  margin: 0 0 0.5rem 0;
}

.lecture-description {
  color: #495057;
  margin: 0 0 1rem 0;
  line-height: 1.4;
}

.lecture-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 1rem;
  border-top: 1px solid #e9ecef;
}

.lecture-date {
  color: #6c757d;
  font-size: 0.9rem;
}

.lecture-status {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 500;
}

.lecture-status.completed {
  background: #d4edda;
  color: #155724;
}

.lecture-status.draft {
  background: #fff3cd;
  color: #856404;
}

.empty-state {
  text-align: center;
  padding: 4rem 2rem;
}

.empty-content {
  max-width: 400px;
  margin: 0 auto;
}

.empty-content h3 {
  color: #6c757d;
  margin-bottom: 1rem;
}

/* Modal styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  padding: 0;
  max-width: 600px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-content.large {
  max-width: 900px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e9ecef;
}

.modal-header h2 {
  margin: 0;
  color: #2c3e50;
}

.header-actions {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #6c757d;
}

.close-btn:hover {
  color: #495057;
}

.lecture-form {
  padding: 1.5rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #495057;
}

.form-group input,
.form-group textarea,
.form-group select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ced4da;
  border-radius: 6px;
  font-family: inherit;
}

.form-group input:focus,
.form-group textarea:focus,
.form-group select:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 2px rgba(0,123,255,0.25);
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  padding-top: 1rem;
  border-top: 1px solid #e9ecef;
}

.cancel-btn {
  background: #6c757d;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  cursor: pointer;
}

.submit-btn {
  background: #007bff;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  cursor: pointer;
}

.submit-btn:disabled {
  background: #6c757d;
  cursor: not-allowed;
}

.export-btn {
  background: #17a2b8;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
}

.lecture-content {
  padding: 1.5rem;
}

.lecture-info {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 6px;
  margin-bottom: 1.5rem;
}

.lecture-info p {
  margin: 0.5rem 0;
}

.lecture-body {
  line-height: 1.6;
  color: #495057;
}
</style>
