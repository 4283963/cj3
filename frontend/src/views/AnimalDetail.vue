<template>
  <div class="detail-page">
    <div class="container">
      <div class="back-bar">
        <button class="back-btn" @click="goBack">
          <span class="back-arrow">←</span> 返回列表
        </button>
      </div>

      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>加载中...</p>
      </div>

      <div v-else-if="error" class="error-state">
        <p class="error-msg">😿 {{ error }}</p>
        <button class="retry-btn" @click="loadDetail">重新加载</button>
      </div>

      <div v-else-if="animal" class="content">
        <div class="animal-hero">
          <div class="hero-image">
            <img
              v-if="animal.image_url"
              :src="animal.image_url"
              :alt="animal.name"
              @error="handleImgError"
            />
            <div v-else class="placeholder-img">
              <span class="emoji">{{ animal.species === '猫' ? '🐱' : animal.species === '狗' ? '🐶' : '🐾' }}</span>
            </div>
          </div>
          <div class="hero-info">
            <div class="hero-header">
              <h1 class="animal-name">{{ animal.name }}</h1>
              <span class="status-badge" :class="'status-' + statusClass">{{ animal.status }}</span>
            </div>
            <div class="meta-tags">
              <span class="tag tag-species">{{ animal.species }}</span>
              <span v-if="animal.gender" class="tag tag-gender">
                {{ animal.gender === '公' ? '♂️ 公' : '♀️ 母' }}
              </span>
              <span v-if="animal.age" class="tag tag-age">📅 {{ animal.age }}</span>
              <span class="tag tag-sterilized" :class="{ 'yes': animal.sterilized }">
                {{ animal.sterilized ? '✅ 已绝育' : '⏳ 未绝育' }}
              </span>
            </div>
            <div class="info-grid">
              <div v-if="animal.health_status" class="info-item">
                <span class="info-label">💊 健康情况</span>
                <span class="info-value">{{ animal.health_status }}</span>
              </div>
              <div v-if="animal.found_location" class="info-item">
                <span class="info-label">📍 发现地点</span>
                <span class="info-value">{{ animal.found_location }}</span>
              </div>
              <div v-if="animal.description" class="info-item info-desc">
                <span class="info-label">📝 性格描述</span>
                <span class="info-value">{{ animal.description }}</span>
              </div>
            </div>
            <div class="hero-actions">
              <button
                v-if="animal.status === '待领养'"
                class="btn-primary btn-apply"
                @click="goApply"
              >
                💕 申请领养
              </button>
              <button
                v-else-if="animal.status === '申请中'"
                class="btn-disabled"
                disabled
              >
                📋 已有申请审核中
              </button>
              <button
                v-else
                class="btn-disabled"
                disabled
              >
                🏡 已找到温暖的家
              </button>
            </div>
          </div>
        </div>

        <section class="timeline-section">
          <div class="section-header">
            <h2 class="section-title">
              <span class="title-icon">✨</span>
              成长时光机
              <span class="timeline-count">({{ timelines.length }}条动态)</span>
            </h2>
          </div>

          <div class="post-card">
            <div class="post-header">
              <span class="post-avatar">📮</span>
              <span class="post-title">发一条近况，记录TA的成长</span>
            </div>
            <div class="post-form">
              <input
                v-model="newPost.author_name"
                class="post-input post-name"
                type="text"
                placeholder="你的名字（志愿者 / 领养人）"
                maxlength="20"
              />
              <textarea
                v-model="newPost.content"
                class="post-input post-content"
                placeholder="分享TA的近况、趣事、心情...（必填）"
                rows="3"
                maxlength="500"
              ></textarea>
              <input
                v-model="newPost.image_url"
                class="post-input post-img"
                type="text"
                placeholder="（可选）附上一张照片的链接"
              />
              <div class="post-footer">
                <span class="hint">内容不能为空哦</span>
                <button
                  class="btn-submit"
                  :disabled="!canSubmit || submitting"
                  @click="submitPost"
                >
                  {{ submitting ? '发布中...' : '发布动态' }}
                </button>
              </div>
            </div>
          </div>

          <div v-if="timelines.length === 0" class="empty-timeline">
            <span class="empty-emoji">📭</span>
            <p>还没有动态，快来发布第一条吧！</p>
          </div>

          <div v-else class="timeline-wrap">
            <div class="timeline-line"></div>

            <div
              v-for="(item, index) in timelines"
              :key="item.id"
              class="timeline-item"
            >
              <div class="timeline-node" :class="{ first: index === 0, last: index === timelines.length - 1 }">
                <span class="node-icon">📌</span>
              </div>

              <div class="timeline-card">
                <div class="card-header">
                  <div class="author-info">
                    <span class="author-avatar">👤</span>
                    <span class="author-name">{{ item.author_name }}</span>
                  </div>
                  <span class="post-time">{{ formatTime(item.created_at) }}</span>
                </div>

                <div class="card-content">
                  <p class="content-text">{{ item.content }}</p>
                  <div v-if="item.image_url" class="content-image">
                    <img
                      :src="item.image_url"
                      alt="动态图片"
                      @error="handleTimelineImgError($event)"
                      loading="lazy"
                    />
                  </div>
                </div>

                <div class="card-footer">
                  <button
                    class="like-btn"
                    :class="{ liked: item.liked_by_me }"
                    :disabled="!!likeLoadingMap[item.id]"
                    @click="toggleLike(item)"
                  >
                    <span class="like-icon">{{ item.liked_by_me ? '❤️' : '🤍' }}</span>
                    <span class="like-count">{{ item.like_count || 0 }}</span>
                    <span class="like-text">{{ item.liked_by_me ? '已赞' : '点赞' }}</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>

    <Transition name="toast">
      <div v-if="toast.show" class="toast" :class="toast.type">
        {{ toast.message }}
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { animalApi } from '@/api'

const route = useRoute()
const router = useRouter()

const animalId = computed(() => Number(route.params.id))
const loading = ref(true)
const error = ref('')
const animal = ref(null)
const timelines = ref([])
const submitting = ref(false)
const likeLoadingMap = ref({})

const newPost = ref({
  author_name: '',
  content: '',
  image_url: ''
})

const toast = ref({ show: false, message: '', type: 'success' })
const visitorId = ref('')

function ensureVisitorId() {
  let id = localStorage.getItem('rescue_visitor_id')
  if (!id) {
    id = 'v_' + Date.now() + '_' + Math.random().toString(36).slice(2, 8)
    localStorage.setItem('rescue_visitor_id', id)
  }
  visitorId.value = id
  return id
}

const statusClass = computed(() => {
  if (!animal.value) return ''
  const s = animal.value.status
  if (s === '待领养') return 'available'
  if (s === '申请中') return 'pending'
  if (s === '已领养') return 'adopted'
  return ''
})

const canSubmit = computed(() => {
  return newPost.value.author_name.trim() && newPost.value.content.trim()
})

async function loadDetail() {
  loading.value = true
  error.value = ''
  try {
    const vid = ensureVisitorId()
    const data = await animalApi.getAnimalDetail(animalId.value, vid)
    animal.value = data
    timelines.value = data.timelines || []
  } catch (e) {
    console.error('加载详情失败:', e)
    const msg = e?.response?.data?.detail || '加载动物详情失败，请稍后重试'
    error.value = msg
  } finally {
    loading.value = false
  }
}

async function submitPost() {
  if (!canSubmit.value || submitting.value) return
  submitting.value = true
  try {
    const result = await animalApi.createTimeline(animalId.value, {
      author_name: newPost.value.author_name.trim(),
      content: newPost.value.content.trim(),
      image_url: newPost.value.image_url.trim() || null
    })
    timelines.value.push({
      ...result,
      liked_by_me: false,
      like_count: 0
    })
    newPost.value = { author_name: '', content: '', image_url: '' }
    showToast('🎉 动态发布成功！', 'success')
  } catch (e) {
    console.error('发布失败:', e)
    const msg = e?.response?.data?.detail || '发布失败，请稍后重试'
    showToast('❌ ' + msg, 'error')
  } finally {
    submitting.value = false
  }
}

async function toggleLike(item) {
  if (likeLoadingMap.value[item.id]) return
  likeLoadingMap.value[item.id] = true
  const vid = ensureVisitorId()
  try {
    const result = await animalApi.toggleTimelineLike(item.id, vid)
    item.like_count = result.like_count
    item.liked_by_me = result.liked_by_me
  } catch (e) {
    console.error('点赞失败:', e)
    const msg = e?.response?.data?.detail || '操作失败'
    showToast('❌ ' + msg, 'error')
  } finally {
    delete likeLoadingMap.value[item.id]
  }
}

function showToast(message, type = 'success') {
  toast.value = { show: true, message, type }
  setTimeout(() => {
    toast.value.show = false
  }, 2500)
}

function goBack() {
  if (window.history.length > 1) {
    router.back()
  } else {
    router.push('/animals/gallery')
  }
}

function goApply() {
  router.push(`/animals/apply/${animalId.value}`)
}

function handleImgError(e) {
  e.target.style.display = 'none'
}

function handleTimelineImgError(e) {
  e.target.parentElement.style.display = 'none'
}

function formatTime(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  const now = new Date()
  const diffMs = now - d
  const diffMin = Math.floor(diffMs / 60000)
  const diffHour = Math.floor(diffMs / 3600000)
  const diffDay = Math.floor(diffMs / 86400000)

  if (diffMin < 1) return '刚刚'
  if (diffMin < 60) return `${diffMin}分钟前`
  if (diffHour < 24) return `${diffHour}小时前`
  if (diffDay < 7) return `${diffDay}天前`

  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const hh = String(d.getHours()).padStart(2, '0')
  const mm = String(d.getMinutes()).padStart(2, '0')
  return `${y}-${m}-${day} ${hh}:${mm}`
}

watch(() => route.params.id, () => {
  loadDetail()
})

onMounted(() => {
  ensureVisitorId()
  loadDetail()
})
</script>

<style scoped>
.detail-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #fef7f0 0%, #f5f7ff 100%);
  padding-bottom: 60px;
}
.container {
  max-width: 960px;
  margin: 0 auto;
  padding: 24px 16px;
}
.back-bar { margin-bottom: 16px; }
.back-btn {
  display: inline-flex; align-items: center; gap: 4px;
  background: white; border: 1px solid #e5e7eb;
  padding: 8px 16px; border-radius: 999px;
  font-size: 14px; color: #4b5563; cursor: pointer;
  transition: all .2s;
}
.back-btn:hover { background: #f9fafb; border-color: #fbbf24; color: #92400e; }
.back-arrow { font-size: 18px; }

.loading-state, .error-state {
  text-align: center; padding: 80px 20px; color: #6b7280;
}
.spinner {
  width: 40px; height: 40px; border: 4px solid #fed7aa;
  border-top-color: #f97316; border-radius: 50%;
  margin: 0 auto 16px; animation: spin 1s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.error-msg { font-size: 16px; margin-bottom: 16px; }
.retry-btn {
  padding: 8px 20px; background: #f97316; color: white;
  border: none; border-radius: 8px; cursor: pointer; font-size: 14px;
}

.animal-hero {
  background: white; border-radius: 24px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.06);
  overflow: hidden; margin-bottom: 28px;
  display: grid; grid-template-columns: 380px 1fr;
}
@media (max-width: 768px) {
  .animal-hero { grid-template-columns: 1fr; }
}
.hero-image {
  width: 100%; aspect-ratio: 4/3; background: #f3f4f6;
  position: relative; overflow: hidden;
}
.hero-image img {
  width: 100%; height: 100%; object-fit: cover;
}
.placeholder-img {
  width: 100%; height: 100%;
  display: flex; align-items: center; justify-content: center;
  background: linear-gradient(135deg, #fef3c7, #fde68a);
}
.emoji { font-size: 120px; }

.hero-info { padding: 28px; }
.hero-header {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 14px; gap: 12px; flex-wrap: wrap;
}
.animal-name {
  font-size: 32px; font-weight: 800; color: #1f2937;
  margin: 0;
}
.status-badge {
  display: inline-block; padding: 6px 16px; border-radius: 999px;
  font-size: 13px; font-weight: 600; flex-shrink: 0;
}
.status-available { background: #ecfdf5; color: #059669; border: 1px solid #6ee7b7; }
.status-pending { background: #fffbeb; color: #d97706; border: 1px solid #fcd34d; }
.status-adopted { background: #eff6ff; color: #2563eb; border: 1px solid #93c5fd; }

.meta-tags { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 20px; }
.tag {
  display: inline-flex; align-items: center; gap: 4px;
  padding: 5px 12px; border-radius: 999px; font-size: 13px;
  background: #f3f4f6; color: #4b5563; border: 1px solid #e5e7eb;
}
.tag-species { background: #eef2ff; color: #4f46e5; border-color: #c7d2fe; }
.tag-gender { background: #fdf2f8; color: #db2777; border-color: #f9a8d4; }
.tag-age { background: #ecfdf5; color: #059669; border-color: #6ee7b7; }
.tag-sterilized.yes { background: #ecfdf5; color: #059669; border-color: #6ee7b7; }

.info-grid {
  display: grid; grid-template-columns: 1fr 1fr; gap: 12px;
  margin-bottom: 22px;
}
@media (max-width: 640px) {
  .info-grid { grid-template-columns: 1fr; }
}
.info-item {
  display: flex; flex-direction: column; gap: 4px;
  background: #fafafa; padding: 12px 14px; border-radius: 12px;
  border: 1px solid #f0f0f0;
}
.info-item.info-desc { grid-column: 1 / -1; }
.info-label { font-size: 12px; color: #9ca3af; font-weight: 500; }
.info-value { font-size: 14px; color: #374151; line-height: 1.55; }

.hero-actions { }
.btn-primary, .btn-disabled, .btn-apply {
  display: inline-flex; align-items: center; justify-content: center;
  gap: 6px; padding: 12px 28px; border-radius: 12px;
  font-size: 15px; font-weight: 600; cursor: pointer; border: none;
  transition: all .2s;
}
.btn-primary {
  background: linear-gradient(135deg, #f97316, #ef4444); color: white;
  box-shadow: 0 4px 12px rgba(249, 115, 22, 0.28);
}
.btn-primary:hover:not(:disabled) { transform: translateY(-1px); }
.btn-primary:active:not(:disabled) { transform: translateY(0); }
.btn-disabled {
  background: #f3f4f6; color: #9ca3af; cursor: not-allowed;
}

.section-header { margin-bottom: 20px; }
.section-title {
  font-size: 22px; font-weight: 700; color: #1f2937;
  margin: 0; display: flex; align-items: center; gap: 8px; flex-wrap: wrap;
}
.title-icon { font-size: 24px; }
.timeline-count {
  font-size: 14px; color: #9ca3af; font-weight: 500;
}

.post-card {
  background: white; border-radius: 20px; padding: 22px;
  box-shadow: 0 2px 16px rgba(0,0,0,0.05);
  border: 1px solid #f3f4f6; margin-bottom: 28px;
}
.post-header {
  display: flex; align-items: center; gap: 10px; margin-bottom: 14px;
}
.post-avatar { font-size: 22px; }
.post-title { font-size: 15px; color: #374151; font-weight: 600; }

.post-form { display: flex; flex-direction: column; gap: 10px; }
.post-input {
  width: 100%; padding: 12px 14px; border: 1.5px solid #e5e7eb;
  border-radius: 12px; font-size: 14px; color: #1f2937;
  background: #fafafa; transition: all .2s; box-sizing: border-box;
  font-family: inherit;
}
.post-input:focus {
  outline: none; background: white;
  border-color: #fbbf24; box-shadow: 0 0 0 4px rgba(251, 191, 36, 0.12);
}
.post-content { resize: vertical; min-height: 80px; line-height: 1.6; }
.post-footer {
  display: flex; justify-content: space-between; align-items: center;
  margin-top: 4px;
}
.hint { font-size: 12px; color: #9ca3af; }
.btn-submit {
  padding: 10px 22px; background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white; border: none; border-radius: 10px;
  font-size: 14px; font-weight: 600; cursor: pointer; transition: all .2s;
}
.btn-submit:hover:not(:disabled) { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(245,158,11,.3); }
.btn-submit:disabled { opacity: 0.5; cursor: not-allowed; }

.empty-timeline {
  text-align: center; padding: 60px 20px; color: #6b7280;
  background: white; border-radius: 20px; border: 2px dashed #e5e7eb;
}
.empty-emoji { font-size: 48px; display: block; margin-bottom: 12px; }
.empty-timeline p { margin: 0; font-size: 15px; }

.timeline-wrap { position: relative; padding-left: 36px; }
.timeline-line {
  position: absolute; left: 16px; top: 12px; bottom: 12px;
  width: 2px; background: linear-gradient(180deg, #fbbf24, #f97316, #ec4899);
  border-radius: 2px;
}

.timeline-item {
  position: relative; margin-bottom: 24px;
}
.timeline-node {
  position: absolute; left: -36px; top: 14px;
  width: 36px; height: 36px;
  display: flex; align-items: center; justify-content: center;
  background: white; border: 2.5px solid #fbbf24;
  border-radius: 50%; z-index: 2;
}
.timeline-node.first { border-color: #10b981; background: #ecfdf5; }
.timeline-node.last { border-color: #ef4444; background: #fef2f2; }
.node-icon { font-size: 16px; }

.timeline-card {
  background: white; border-radius: 18px;
  box-shadow: 0 2px 14px rgba(0,0,0,0.05);
  border: 1px solid #f0f0f0; overflow: hidden;
  transition: all .2s;
}
.timeline-card:hover {
  box-shadow: 0 6px 22px rgba(0,0,0,0.08);
  transform: translateY(-2px);
}
.card-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 14px 18px; background: #fafafa;
  border-bottom: 1px solid #f3f4f6;
}
.author-info { display: flex; align-items: center; gap: 8px; }
.author-avatar { font-size: 18px; }
.author-name { font-size: 14px; font-weight: 600; color: #1f2937; }
.post-time { font-size: 12px; color: #9ca3af; }

.card-content { padding: 16px 18px; }
.content-text {
  font-size: 15px; color: #374151; line-height: 1.75;
  margin: 0 0 12px 0; white-space: pre-wrap;
}
.content-image {
  border-radius: 12px; overflow: hidden;
  max-height: 400px; background: #f3f4f6;
}
.content-image img {
  width: 100%; height: auto; display: block; max-height: 400px;
  object-fit: cover;
}

.card-footer {
  padding: 10px 18px; border-top: 1px solid #f3f4f6;
  background: #fafafa;
}
.like-btn {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 6px 14px; background: white; border: 1.5px solid #e5e7eb;
  border-radius: 999px; cursor: pointer; font-size: 13px; color: #6b7280;
  transition: all .2s;
}
.like-btn:hover { border-color: #fca5a5; background: #fff5f5; }
.like-btn.liked {
  background: #fef2f2; border-color: #f87171; color: #dc2626;
}
.like-icon { font-size: 16px; transition: transform .2s; }
.like-btn:hover:not(:disabled) .like-icon { transform: scale(1.2); }
.like-count { font-weight: 600; }
.like-btn:disabled { opacity: 0.6; cursor: not-allowed; }

.toast {
  position: fixed; top: 24px; left: 50%; transform: translateX(-50%);
  z-index: 9999; padding: 12px 24px; border-radius: 12px;
  font-size: 14px; font-weight: 500; color: white;
  box-shadow: 0 8px 24px rgba(0,0,0,0.15);
}
.toast.success { background: linear-gradient(135deg, #10b981, #059669); }
.toast.error { background: linear-gradient(135deg, #ef4444, #dc2626); }
.toast-enter-active, .toast-leave-active { transition: all .25s ease; }
.toast-enter-from, .toast-leave-to { opacity: 0; transform: translate(-50%, -16px); }
</style>
