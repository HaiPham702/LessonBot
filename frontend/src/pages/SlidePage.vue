<template>
  <div class="slide-page">
    <div class="page-header">
      <h1>🎯 Quản lý Slide thuyết trình</h1>
      <div class="header-actions">
        <button @click="showCreateModal = true" class="create-button">
          ➕ Tạo slide mới
        </button>
        <button @click="showLectureModal = true" class="create-from-lecture-btn">
          📚 Tạo từ bài giảng
        </button>
      </div>
    </div>

    <div class="slides-grid" v-if="slides.length > 0">
      <div
        v-for="slide in slides"
        :key="slide.id"
        class="slide-card"
        @click="viewSlide(slide)"
      >
        <div class="slide-preview">
          <div class="slide-thumbnail">
            <span class="slide-icon">🎯</span>
            <span class="slide-count">{{ slide.slideCount || 0 }} slides</span>
          </div>
        </div>
        
        <div class="slide-info">
          <div class="slide-header">
            <h3>{{ slide.title }}</h3>
            <div class="slide-actions">
              <button @click.stop="editSlide(slide)" class="action-btn edit">✏️</button>
              <button @click.stop="deleteSlide(slide.id)" class="action-btn delete">🗑️</button>
            </div>
          </div>
          <p class="slide-subject">{{ slide.subject }}</p>
          <p class="slide-description">{{ slide.description }}</p>
          <div class="slide-meta">
            <span class="slide-date">{{ formatDate(slide.createdAt) }}</span>
            <span class="slide-status" :class="slide.status">{{ slide.status }}</span>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="empty-state">
      <div class="empty-content">
        <h3>📊 Chưa có slide nào</h3>
        <p>Bắt đầu tạo slide thuyết trình đầu tiên của bạn!</p>
        <div class="empty-actions">
          <button @click="showCreateModal = true" class="create-button">
            Tạo slide mới
          </button>
          <button @click="showLectureModal = true" class="create-from-lecture-btn">
            Tạo từ bài giảng
          </button>
        </div>
      </div>
    </div>

    <!-- Modal tạo/chỉnh sửa slide -->
    <div v-if="showCreateModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>{{ editingSlide ? 'Chỉnh sửa slide' : 'Tạo slide mới' }}</h2>
          <button @click="closeModal" class="close-btn">✕</button>
        </div>
        
        <form @submit.prevent="handleSubmit" class="slide-form">
          <div class="form-group">
            <label for="title">Tiêu đề slide *</label>
            <input
              id="title"
              v-model="slideForm.title"
              type="text"
              placeholder="VD: Bài thuyết trình về Toán học"
              required
            />
          </div>

          <div class="form-group">
            <label for="subject">Môn học *</label>
            <input
              id="subject"
              v-model="slideForm.subject"
              type="text"
              placeholder="VD: Toán học, Vật lý, Hóa học..."
              required
            />
          </div>

          <div class="form-group">
            <label for="presentation-type">Loại thuyết trình</label>
            <select id="presentation-type" v-model="slideForm.presentationType">
              <option value="">Chọn loại</option>
              <option value="lecture">Bài giảng</option>
              <option value="workshop">Workshop</option>
              <option value="seminar">Seminar</option>
              <option value="conference">Hội thảo</option>
            </select>
          </div>

          <div class="form-group">
            <label for="duration">Thời lượng (phút)</label>
            <input
              id="duration"
              v-model="slideForm.duration"
              type="number"
              min="5"
              max="300"
              placeholder="45"
            />
          </div>

          <div class="form-group">
            <label for="description">Mô tả ngắn</label>
            <textarea
              id="description"
              v-model="slideForm.description"
              rows="3"
              placeholder="Mô tả ngắn gọn về nội dung slide..."
            ></textarea>
          </div>

          <div class="form-group">
            <label for="requirements">Yêu cầu chi tiết *</label>
            <textarea
              id="requirements"
              v-model="slideForm.requirements"
              rows="8"
              placeholder="Mô tả chi tiết yêu cầu cho slide:
- Các chủ đề chính cần trình bày
- Số lượng slide mong muốn
- Phong cách thiết kế (formal, creative, minimal...)
- Nội dung cần nhấn mạnh
- Đối tượng khán giả
- Yêu cầu về hình ảnh/biểu đồ..."
              required
            ></textarea>
          </div>

          <div class="form-actions">
            <button type="button" @click="closeModal" class="cancel-btn">
              Hủy
            </button>
            <button type="submit" :disabled="isCreating" class="submit-btn">
              {{ isCreating ? 'Đang tạo...' : (editingSlide ? 'Cập nhật' : 'Tạo slide') }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Modal tạo slide từ bài giảng -->
    <div v-if="showLectureModal" class="modal-overlay" @click="closeLectureModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>Tạo slide từ bài giảng</h2>
          <button @click="closeLectureModal" class="close-btn">✕</button>
        </div>
        
        <div class="lecture-selection">
          <div v-if="availableLectures.length === 0" class="no-lectures">
            <p>Không có bài giảng nào để tạo slide.</p>
            <p>Vui lòng tạo bài giảng trước!</p>
          </div>
          
          <div v-else>
            <div class="form-group">
              <label>Chọn bài giảng:</label>
              <div class="lecture-list">
                <div
                  v-for="lecture in availableLectures"
                  :key="lecture.id"
                  :class="['lecture-item', { selected: selectedLecture?.id === lecture.id }]"
                  @click="selectedLecture = lecture"
                >
                  <h4>{{ lecture.title }}</h4>
                  <p>{{ lecture.subject }} - {{ formatDate(lecture.createdAt) }}</p>
                </div>
              </div>
            </div>

            <div v-if="selectedLecture" class="form-group">
              <label for="slide-options">Tùy chọn slide:</label>
              <div class="slide-options">
                <div class="option-item">
                  <label>
                    <input
                      type="checkbox"
                      v-model="slideOptions.includeIntro"
                    />
                    Slide giới thiệu
                  </label>
                </div>
                <div class="option-item">
                  <label>
                    <input
                      type="checkbox"
                      v-model="slideOptions.includeConclusion"
                    />
                    Slide kết luận
                  </label>
                </div>
                <div class="option-item">
                  <label>
                    <input
                      type="checkbox"
                      v-model="slideOptions.includeQuestions"
                    />
                    Slide câu hỏi
                  </label>
                </div>
              </div>
            </div>

            <div class="form-actions">
              <button type="button" @click="closeLectureModal" class="cancel-btn">
                Hủy
              </button>
              <button
                type="button"
                @click="createSlideFromLecture"
                :disabled="!selectedLecture || isCreating"
                class="submit-btn"
              >
                {{ isCreating ? 'Đang tạo...' : 'Tạo slide' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal xem chi tiết slide -->
    <div v-if="viewingSlide" class="modal-overlay" @click="closeViewModal">
      <div class="modal-content large" @click.stop>
        <div class="modal-header">
          <h2>{{ viewingSlide.title }}</h2>
          <div class="header-actions">
            <button @click="exportSlide(viewingSlide.id)" class="export-btn">
              📥 Xuất PowerPoint
            </button>
            <button @click="closeViewModal" class="close-btn">✕</button>
          </div>
        </div>
        
        <div class="slide-content">
          <div class="slide-info-detail">
            <p><strong>Môn học:</strong> {{ viewingSlide.subject }}</p>
            <p><strong>Loại:</strong> {{ getPresentationTypeLabel(viewingSlide.presentationType) }}</p>
            <p><strong>Thời lượng:</strong> {{ viewingSlide.duration }} phút</p>
            <p><strong>Số slide:</strong> {{ viewingSlide.slideCount || 0 }}</p>
            <p><strong>Ngày tạo:</strong> {{ formatDate(viewingSlide.createdAt) }}</p>
            <p><strong>Mô tả:</strong> {{ viewingSlide.description }}</p>
          </div>
          
          <div class="slides-preview">
            <h3>Nội dung slides:</h3>
            <div class="slide-list" v-if="viewingSlide.slides && viewingSlide.slides.length > 0">
              <div
                v-for="(slide, index) in viewingSlide.slides"
                :key="index"
                class="slide-item"
              >
                <div class="slide-number">{{ index + 1 }}</div>
                <div class="slide-content-item">
                  <h4>{{ slide.title }}</h4>
                  <div v-html="formatSlideContent(slide.content)"></div>
                </div>
              </div>
            </div>
            <div v-else class="no-slides">
              <p>Chưa có nội dung slide</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import slideService from '../services/slideService'
import lectureService from '../services/lectureService'

const slides = ref([])
const availableLectures = ref([])
const showCreateModal = ref(false)
const showLectureModal = ref(false)
const editingSlide = ref(null)
const viewingSlide = ref(null)
const selectedLecture = ref(null)
const isCreating = ref(false)

const slideForm = ref({
  title: '',
  subject: '',
  presentationType: '',
  duration: 45,
  description: '',
  requirements: ''
})

const slideOptions = ref({
  includeIntro: true,
  includeConclusion: true,
  includeQuestions: false
})

const loadSlides = async () => {
  try {
    const response = await slideService.getSlides()
    slides.value = response.data.slides || []
  } catch (error) {
    console.error('Error loading slides:', error)
    alert('Không thể tải danh sách slide')
  }
}

const loadLectures = async () => {
  try {
    const response = await lectureService.getLectures()
    availableLectures.value = response.data.lectures || []
  } catch (error) {
    console.error('Error loading lectures:', error)
  }
}

const handleSubmit = async () => {
  try {
    isCreating.value = true
    
    if (editingSlide.value) {
      await slideService.updateSlide(editingSlide.value.id, slideForm.value)
    } else {
      await slideService.createSlides(slideForm.value)
    }
    
    await loadSlides()
    closeModal()
    
    alert(editingSlide.value ? 'Cập nhật slide thành công!' : 'Tạo slide thành công!')
  } catch (error) {
    console.error('Error creating/updating slide:', error)
    alert('Có lỗi xảy ra. Vui lòng thử lại.')
  } finally {
    isCreating.value = false
  }
}

const createSlideFromLecture = async () => {
  if (!selectedLecture.value) return
  
  try {
    isCreating.value = true
    
    await slideService.createSlidesFromLecture(selectedLecture.value.id, slideOptions.value)
    
    await loadSlides()
    closeLectureModal()
    
    alert('Tạo slide từ bài giảng thành công!')
  } catch (error) {
    console.error('Error creating slide from lecture:', error)
    alert('Có lỗi xảy ra khi tạo slide từ bài giảng.')
  } finally {
    isCreating.value = false
  }
}

const editSlide = (slide) => {
  editingSlide.value = slide
  slideForm.value = { ...slide }
  showCreateModal.value = true
}

const viewSlide = async (slide) => {
  try {
    const response = await slideService.getSlide(slide.id)
    viewingSlide.value = response.data
  } catch (error) {
    console.error('Error loading slide:', error)
    alert('Không thể tải chi tiết slide')
  }
}

const deleteSlide = async (slideId) => {
  if (!confirm('Bạn có chắc chắn muốn xóa slide này?')) return
  
  try {
    await slideService.deleteSlide(slideId)
    await loadSlides()
    alert('Xóa slide thành công!')
  } catch (error) {
    console.error('Error deleting slide:', error)
    alert('Không thể xóa slide')
  }
}

const exportSlide = async (slideId) => {
  try {
    const response = await slideService.exportSlide(slideId)
    
    // Tạo link download
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `slide-${slideId}.pptx`)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
  } catch (error) {
    console.error('Error exporting slide:', error)
    alert('Không thể xuất file slide')
  }
}

const closeModal = () => {
  showCreateModal.value = false
  editingSlide.value = null
  slideForm.value = {
    title: '',
    subject: '',
    presentationType: '',
    duration: 45,
    description: '',
    requirements: ''
  }
}

const closeLectureModal = () => {
  showLectureModal.value = false
  selectedLecture.value = null
  slideOptions.value = {
    includeIntro: true,
    includeConclusion: true,
    includeQuestions: false
  }
}

const closeViewModal = () => {
  viewingSlide.value = null
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('vi-VN')
}

const formatSlideContent = (content) => {
  if (!content) return '<p>Không có nội dung</p>'
  
  return content
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/\n/g, '<br>')
}

const getPresentationTypeLabel = (type) => {
  const labels = {
    lecture: 'Bài giảng',
    workshop: 'Workshop',
    seminar: 'Seminar',
    conference: 'Hội thảo'
  }
  return labels[type] || 'Không xác định'
}

onMounted(() => {
  loadSlides()
  loadLectures()
})
</script>

<style scoped>
/* Tái sử dụng styles từ LecturePage và thêm styles riêng cho slide */
.slide-page {
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

.header-actions {
  display: flex;
  gap: 1rem;
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

.create-from-lecture-btn {
  background: #17a2b8;
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

.create-from-lecture-btn:hover {
  background: #138496;
}

.slides-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.slide-card {
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.slide-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.slide-preview {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.slide-thumbnail {
  text-align: center;
}

.slide-icon {
  font-size: 2rem;
  display: block;
  margin-bottom: 0.5rem;
}

.slide-count {
  font-size: 0.9rem;
  opacity: 0.9;
}

.slide-info {
  padding: 1.5rem;
}

.slide-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.slide-header h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.25rem;
}

.slide-actions {
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

.slide-subject {
  color: #6c757d;
  font-weight: 500;
  margin: 0 0 0.5rem 0;
}

.slide-description {
  color: #495057;
  margin: 0 0 1rem 0;
  line-height: 1.4;
}

.slide-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 1rem;
  border-top: 1px solid #e9ecef;
}

.slide-date {
  color: #6c757d;
  font-size: 0.9rem;
}

.slide-status {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 500;
}

.slide-status.completed {
  background: #d4edda;
  color: #155724;
}

.slide-status.draft {
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

.empty-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-top: 2rem;
}

/* Modal styles (tái sử dụng từ LecturePage) */
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

.slide-form {
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

/* Lecture selection styles */
.lecture-selection {
  padding: 1.5rem;
}

.no-lectures {
  text-align: center;
  padding: 2rem;
  color: #6c757d;
}

.lecture-list {
  max-height: 300px;
  overflow-y: auto;
  border: 1px solid #e9ecef;
  border-radius: 6px;
}

.lecture-item {
  padding: 1rem;
  border-bottom: 1px solid #e9ecef;
  cursor: pointer;
  transition: background-color 0.2s;
}

.lecture-item:last-child {
  border-bottom: none;
}

.lecture-item:hover {
  background: #f8f9fa;
}

.lecture-item.selected {
  background: #e7f3ff;
  border-color: #007bff;
}

.lecture-item h4 {
  margin: 0 0 0.5rem 0;
  color: #2c3e50;
}

.lecture-item p {
  margin: 0;
  color: #6c757d;
  font-size: 0.9rem;
}

.slide-options {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.option-item label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.option-item input[type="checkbox"] {
  width: auto;
}

/* Slide content styles */
.slide-content {
  padding: 1.5rem;
}

.slide-info-detail {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 6px;
  margin-bottom: 1.5rem;
}

.slide-info-detail p {
  margin: 0.5rem 0;
}

.slides-preview h3 {
  margin-bottom: 1rem;
  color: #2c3e50;
}

.slide-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.slide-item {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  background: white;
}

.slide-number {
  flex-shrink: 0;
  width: 40px;
  height: 40px;
  background: #007bff;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
}

.slide-content-item {
  flex: 1;
}

.slide-content-item h4 {
  margin: 0 0 0.5rem 0;
  color: #2c3e50;
}

.no-slides {
  text-align: center;
  padding: 2rem;
  color: #6c757d;
}
</style>
