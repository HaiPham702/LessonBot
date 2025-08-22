<template>
  <div class="lecture-outline-container">
    <div class="lecture-header">
      <div class="lecture-title-section">
        <input 
          v-if="editMode" 
          v-model="editableData.title" 
          class="title-input"
          @blur="saveChanges"
        />
        <h3 v-else @click="enableEdit" class="lecture-title">
          {{ lectureData.title }}
        </h3>
        
        <div class="lecture-meta">
          <span class="meta-item">📚 {{ lectureData.subject }}</span>
          <span class="meta-item">🎓 {{ getGradeLabel(lectureData.grade) }}</span>
          <span class="meta-item">⏱️ {{ lectureData.duration }}</span>
        </div>
      </div>
      
      <div class="lecture-actions">
        <button @click="toggleEdit" class="edit-btn">
          {{ editMode ? '💾 Lưu' : '✏️ Sửa' }}
        </button>
        <button @click="createSlide" class="create-slide-btn">
          🎯 Tạo Slide
        </button>
      </div>
    </div>

    <!-- Objectives -->
    <div class="objectives-section">
      <h4>🎯 Mục tiêu bài học:</h4>
      <ul class="objectives-list">
        <li v-for="(objective, index) in editableData.objectives" :key="index" class="objective-item">
          <input 
            v-if="editMode" 
            v-model="editableData.objectives[index]"
            class="objective-input"
            @blur="saveChanges"
          />
          <span v-else>{{ objective }}</span>
          <button v-if="editMode" @click="removeObjective(index)" class="remove-btn">❌</button>
        </li>
      </ul>
      <button v-if="editMode" @click="addObjective" class="add-btn">➕ Thêm mục tiêu</button>
    </div>

    <!-- Outline -->
    <div class="outline-section">
      <h4>📋 Dàn ý chi tiết:</h4>
      <div v-for="(section, sectionIndex) in editableData.outline" :key="sectionIndex" class="section-item">
        <div class="section-header">
          <input 
            v-if="editMode" 
            v-model="section.section"
            class="section-title-input"
            @blur="saveChanges"
          />
          <h5 v-else class="section-title">{{ section.section }}</h5>
          <span class="section-duration">({{ section.duration }})</span>
        </div>

        <div v-for="(topic, topicIndex) in section.topics" :key="topicIndex" class="topic-item">
          <div class="main-topic">
            <input 
              v-if="editMode" 
              v-model="topic.main_topic"
              class="topic-input"
              @blur="saveChanges"
            />
            <strong v-else>{{ topic.main_topic }}</strong>
          </div>

          <div v-for="(subtopic, subtopicIndex) in topic.subtopics" :key="subtopicIndex" class="subtopic-item">
            <div class="subtopic-header">
              <input 
                v-if="editMode" 
                v-model="subtopic.subtitle"
                class="subtopic-input"
                @blur="saveChanges"
              />
              <span v-else class="subtopic-title">{{ subtopic.subtitle }}</span>
            </div>
            
            <div class="subtopic-content">
              <textarea 
                v-if="editMode" 
                v-model="subtopic.content"
                class="content-textarea"
                @blur="saveChanges"
              ></textarea>
              <p v-else>{{ subtopic.content }}</p>
            </div>

            <div v-if="subtopic.activities && subtopic.activities.length > 0" class="activities">
              <strong>Hoạt động:</strong>
              <ul>
                <li v-for="activity in subtopic.activities" :key="activity">{{ activity }}</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Resources & Assessment -->
    <div class="footer-sections">
      <div class="resources-section">
        <h4>📚 Tài liệu tham khảo:</h4>
        <ul>
          <li v-for="resource in editableData.resources" :key="resource">{{ resource }}</li>
        </ul>
      </div>

      <div class="assessment-section">
        <h4>📝 Đánh giá:</h4>
        <textarea 
          v-if="editMode" 
          v-model="editableData.assessment"
          class="assessment-textarea"
          @blur="saveChanges"
        ></textarea>
        <p v-else>{{ editableData.assessment }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'

const props = defineProps({
  lectureData: {
    type: Object,
    required: true
  },
  editable: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['update-lecture', 'create-slide'])

const editMode = ref(false)
const editableData = reactive({ ...props.lectureData })

// Watch for changes in lectureData
watch(() => props.lectureData, (newData) => {
  Object.assign(editableData, newData)
}, { deep: true })

const enableEdit = () => {
  if (props.editable) {
    editMode.value = true
  }
}

const toggleEdit = () => {
  if (editMode.value) {
    saveChanges()
  }
  editMode.value = !editMode.value
}

const saveChanges = () => {
  emit('update-lecture', { ...editableData })
}

const addObjective = () => {
  editableData.objectives.push('Mục tiêu mới')
}

const removeObjective = (index) => {
  editableData.objectives.splice(index, 1)
  saveChanges()
}

const createSlide = () => {
  emit('create-slide', { ...editableData })
}

const getGradeLabel = (grade) => {
  const gradeMap = {
    'elementary': 'Tiểu học',
    'middle': 'THCS',
    'high': 'THPT',
    'university': 'Đại học'
  }
  return gradeMap[grade] || grade
}
</script>

<style scoped>
.lecture-outline-container {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 12px;
  padding: 1.5rem;
  margin: 0.5rem 0;
  max-width: 100%;
}

.lecture-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #e9ecef;
}

.lecture-title {
  color: #2c3e50;
  margin: 0 0 0.5rem 0;
  cursor: pointer;
  transition: color 0.2s;
}

.lecture-title:hover {
  color: #3498db;
}

.title-input {
  font-size: 1.25rem;
  font-weight: bold;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 0.5rem;
  width: 100%;
  background: white;
}

.lecture-meta {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.meta-item {
  background: #e3f2fd;
  color: #1976d2;
  padding: 0.25rem 0.5rem;
  border-radius: 16px;
  font-size: 0.875rem;
}

.lecture-actions {
  display: flex;
  gap: 0.5rem;
  flex-shrink: 0;
}

.edit-btn, .create-slide-btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.875rem;
  transition: all 0.2s;
}

.edit-btn {
  background: #ffc107;
  color: #000;
}

.edit-btn:hover {
  background: #ffb300;
}

.create-slide-btn {
  background: #28a745;
  color: white;
}

.create-slide-btn:hover {
  background: #218838;
}

.objectives-section, .outline-section, .footer-sections {
  margin-bottom: 1.5rem;
}

.objectives-section h4, .outline-section h4, .footer-sections h4 {
  color: #495057;
  margin-bottom: 0.75rem;
}

.objectives-list {
  list-style: none;
  padding: 0;
}

.objective-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
  padding: 0.5rem;
  background: white;
  border-radius: 6px;
  border: 1px solid #e9ecef;
}

.objective-input {
  flex: 1;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 0.25rem 0.5rem;
}

.section-item {
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1rem;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.section-title {
  color: #343a40;
  margin: 0;
  flex: 1;
}

.section-title-input {
  flex: 1;
  font-weight: bold;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 0.25rem 0.5rem;
}

.section-duration {
  color: #6c757d;
  font-size: 0.875rem;
}

.topic-item {
  margin-left: 1rem;
  margin-bottom: 1rem;
}

.main-topic {
  margin-bottom: 0.5rem;
}

.topic-input {
  font-weight: bold;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 0.25rem 0.5rem;
  width: 100%;
}

.subtopic-item {
  margin-left: 1rem;
  margin-bottom: 0.75rem;
  padding: 0.75rem;
  background: #f8f9fa;
  border-radius: 6px;
  border-left: 3px solid #007bff;
}

.subtopic-header {
  margin-bottom: 0.5rem;
}

.subtopic-title {
  font-weight: 500;
  color: #495057;
}

.subtopic-input {
  font-weight: 500;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 0.25rem 0.5rem;
  width: 100%;
}

.subtopic-content p {
  margin: 0.5rem 0;
  line-height: 1.6;
  color: #6c757d;
}

.content-textarea {
  width: 100%;
  min-height: 60px;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 0.5rem;
  resize: vertical;
  font-family: inherit;
}

.activities {
  margin-top: 0.5rem;
  padding: 0.5rem;
  background: #e3f2fd;
  border-radius: 4px;
}

.activities ul {
  margin: 0.25rem 0 0 1rem;
}

.footer-sections {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.resources-section, .assessment-section {
  background: white;
  padding: 1rem;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.assessment-textarea {
  width: 100%;
  min-height: 80px;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 0.5rem;
  resize: vertical;
  font-family: inherit;
}

.add-btn {
  background: #17a2b8;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 0.5rem 1rem;
  cursor: pointer;
  font-size: 0.875rem;
}

.add-btn:hover {
  background: #138496;
}

.remove-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 0.75rem;
  padding: 0.25rem;
}

@media (max-width: 768px) {
  .lecture-header {
    flex-direction: column;
    gap: 1rem;
  }
  
  .lecture-actions {
    width: 100%;
    justify-content: stretch;
  }
  
  .edit-btn, .create-slide-btn {
    flex: 1;
  }
  
  .footer-sections {
    grid-template-columns: 1fr;
  }
}
</style>
