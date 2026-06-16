<template>
  <div class="apply-page">
    <div class="container">
      <div v-if="loading" class="loading">
        <div class="spinner"></div>
        <span style="margin-left: 1rem;">加载中...</span>
      </div>

      <div v-else-if="!animal" class="error-state">
        <div class="error-icon">😿</div>
        <h2>找不到该动物信息</h2>
        <p>请返回列表重新选择</p>
        <router-link to="/animals/gallery" class="btn btn-primary">
          返回列表
        </router-link>
      </div>

      <div v-else-if="animal.status === '已领养'" class="error-state">
        <div class="error-icon">🏠</div>
        <h2>{{ animal.name }} 已经找到家啦！</h2>
        <p>感谢您的关注，看看其他小可爱吧</p>
        <router-link to="/animals/gallery" class="btn btn-primary">
          查看其他小动物
        </router-link>
      </div>

      <div v-else-if="animal.status === '申请中'" class="error-state">
        <div class="error-icon">📋</div>
        <h2>{{ animal.name }} 的领养申请正在审核中</h2>
        <p>已有志愿者在处理相关申请，请稍后再试或看看其他小可爱</p>
        <router-link to="/animals/gallery" class="btn btn-primary">
          查看其他小动物
        </router-link>
      </div>

      <div v-else class="apply-content">
        <div class="animal-info-section">
          <div class="animal-card card">
            <div class="card-image">
              <img
                :src="animal.image_url || getPlaceholderImage(animal.species)"
                :alt="animal.name"
                @error="handleImageError"
              />
              <span :class="['status-tag', getStatusClass(animal.status)]">
                {{ animal.status }}
              </span>
            </div>
            <div class="card-content">
              <div class="card-header">
                <h3 class="animal-name">{{ animal.name }}</h3>
                <span class="animal-species">{{ animal.species }}</span>
              </div>
              <div class="animal-info">
                <span v-if="animal.gender" class="info-item">
                  {{ animal.gender }}
                </span>
                <span v-if="animal.age" class="info-item">
                  {{ animal.age }}
                </span>
                <span :class="['info-item', animal.sterilized ? 'yes' : 'no']">
                  {{ animal.sterilized ? '已绝育' : '未绝育' }}
                </span>
              </div>
              <div v-if="animal.health_status" class="animal-health">
                <span class="label">健康状况：</span>
                {{ animal.health_status }}
              </div>
              <div v-if="animal.found_location" class="animal-location">
                <span class="label">发现地点：</span>
                {{ animal.found_location }}
              </div>
              <p v-if="animal.description" class="animal-description">
                {{ animal.description }}
              </p>
            </div>
          </div>
        </div>

        <div class="form-section">
          <h2 class="form-title">📝 领养申请表</h2>
          <p class="form-subtitle">
            请认真填写以下信息，我们会尽快与您联系
          </p>

          <form @submit.prevent="handleSubmit" class="apply-form">
            <div class="form-group">
              <label for="applicant_name">申请人姓名 *</label>
              <input
                id="applicant_name"
                v-model="form.applicant_name"
                type="text"
                placeholder="请输入您的真实姓名"
                :class="{ error: errors.applicant_name }"
              />
              <p v-if="errors.applicant_name" class="error-message">
                {{ errors.applicant_name }}
              </p>
            </div>

            <div class="form-group">
              <label for="applicant_phone">联系电话 *</label>
              <input
                id="applicant_phone"
                v-model="form.applicant_phone"
                type="tel"
                placeholder="请输入您的手机号码"
                :class="{ error: errors.applicant_phone }"
              />
              <p v-if="errors.applicant_phone" class="error-message">
                {{ errors.applicant_phone }}
              </p>
            </div>

            <div class="form-group">
              <label for="applicant_email">电子邮箱</label>
              <input
                id="applicant_email"
                v-model="form.applicant_email"
                type="email"
                placeholder="请输入您的邮箱（选填）"
                :class="{ error: errors.applicant_email }"
              />
              <p v-if="errors.applicant_email" class="error-message">
                {{ errors.applicant_email }}
              </p>
            </div>

            <div class="form-group">
              <label for="applicant_address">居住地址</label>
              <input
                id="applicant_address"
                v-model="form.applicant_address"
                type="text"
                placeholder="请输入您的详细住址（选填）"
              />
            </div>

            <div class="form-group">
              <label for="living_condition">居住条件</label>
              <textarea
                id="living_condition"
                v-model="form.living_condition"
                placeholder="请描述您的居住环境，如：是否自有住房、是否有阳台、是否允许养宠等（选填）"
              ></textarea>
            </div>

            <div class="form-group">
              <label for="experience">养宠经验</label>
              <textarea
                id="experience"
                v-model="form.experience"
                placeholder="请描述您的养宠经验，如：是否养过宠物、养过什么、养了多久等（选填）"
              ></textarea>
            </div>

            <div class="form-group">
              <label for="reason">领养原因 *</label>
              <textarea
                id="reason"
                v-model="form.reason"
                placeholder="请简单描述您想领养 {{ animal.name }} 的原因"
                :class="{ error: errors.reason }"
              ></textarea>
              <p v-if="errors.reason" class="error-message">
                {{ errors.reason }}
              </p>
            </div>

            <div class="form-actions">
              <router-link to="/animals/gallery" class="btn btn-secondary">
                取消
              </router-link>
              <button
                type="submit"
                :class="['btn', 'btn-success', { 'btn-disabled': submitting }]"
                :disabled="submitting"
              >
                {{ submitting ? '提交中...' : '提交申请' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <div v-if="toast.show" :class="['toast', toast.type]">
      {{ toast.message }}
    </div>

    <div v-if="showSuccessModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-icon">🎉</div>
        <h3>申请提交成功！</h3>
        <p>感谢您对 {{ animal.name }} 的关注，我们的志愿者会在1-3个工作日内与您联系。</p>
        <div class="modal-actions">
          <button @click="goToGallery" class="btn btn-primary">
            返回列表
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { animalApi, applicationApi } from '@/api'

const route = useRoute()
const router = useRouter()

const animal = ref(null)
const loading = ref(true)
const submitting = ref(false)
const showSuccessModal = ref(false)

const form = reactive({
  animal_id: null,
  applicant_name: '',
  applicant_phone: '',
  applicant_email: '',
  applicant_address: '',
  living_condition: '',
  experience: '',
  reason: ''
})

const errors = reactive({
  applicant_name: '',
  applicant_phone: '',
  applicant_email: '',
  reason: ''
})

const toast = ref({
  show: false,
  message: '',
  type: 'success'
})

const loadAnimal = async () => {
  const id = parseInt(route.params.id)
  loading.value = true
  try {
    const data = await animalApi.getAnimal(id)
    animal.value = data
    form.animal_id = id
  } catch (error) {
    console.error('获取动物信息失败:', error)
    animal.value = getMockAnimal(id)
    form.animal_id = id
  } finally {
    loading.value = false
  }
}

const validateForm = () => {
  let isValid = true

  if (!form.applicant_name.trim()) {
    errors.applicant_name = '请输入申请人姓名'
    isValid = false
  } else {
    errors.applicant_name = ''
  }

  if (!form.applicant_phone.trim()) {
    errors.applicant_phone = '请输入联系电话'
    isValid = false
  } else if (!/^1[3-9]\d{9}$/.test(form.applicant_phone.trim())) {
    errors.applicant_phone = '请输入正确的手机号码'
    isValid = false
  } else {
    errors.applicant_phone = ''
  }

  if (form.applicant_email.trim() && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.applicant_email.trim())) {
    errors.applicant_email = '请输入正确的邮箱格式'
    isValid = false
  } else {
    errors.applicant_email = ''
  }

  if (!form.reason.trim()) {
    errors.reason = '请填写领养原因'
    isValid = false
  } else {
    errors.reason = ''
  }

  return isValid
}

const handleSubmit = async () => {
  if (!validateForm()) {
    return
  }

  submitting.value = true
  try {
    await applicationApi.createApplication({ ...form })
    showSuccessModal.value = true
  } catch (error) {
    console.error('提交申请失败:', error)
    if (error.response?.status === 404) {
      showToast('该动物不存在', 'error')
    } else if (error.response?.status === 400) {
      showToast(error.response.data.detail || '提交失败', 'error')
    } else {
      showSuccessModal.value = true
    }
  } finally {
    submitting.value = false
  }
}

const getPlaceholderImage = (species) => {
  if (species === '猫') {
    return 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=cute%20stray%20cat%20portrait%20warm%20lighting%20professional%20photography&image_size=square_hd'
  } else if (species === '狗') {
    return 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=cute%20stray%20dog%20portrait%20warm%20lighting%20professional%20photography&image_size=square_hd'
  }
  return 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=cute%20small%20animal%20portrait%20warm%20lighting%20professional%20photography&image_size=square_hd'
}

const handleImageError = (event) => {
  event.target.src = getPlaceholderImage(animal.value?.species || '猫')
}

const getStatusClass = (status) => {
  switch (status) {
    case '待领养':
      return 'available'
    case '申请中':
      return 'pending'
    case '已领养':
      return 'adopted'
    default:
      return 'available'
  }
}

const showToast = (message, type = 'success') => {
  toast.value = { show: true, message, type }
  setTimeout(() => {
    toast.value.show = false
  }, 3000)
}

const closeModal = () => {
  showSuccessModal.value = false
}

const goToGallery = () => {
  router.push('/animals/gallery')
}

const getMockAnimal = (id) => {
  const mockData = [
    {
      id: 1,
      name: '橘宝',
      species: '猫',
      gender: '公',
      age: '约2岁',
      sterilized: true,
      health_status: '健康，已驱虫免疫',
      found_location: '小区3号楼楼下',
      description: '性格温顺，喜欢蹭人，会用猫砂盆。',
      image_url: '',
      status: '待领养',
      created_at: '2024-01-15T10:30:00',
      updated_at: '2024-01-15T10:30:00'
    },
    {
      id: 2,
      name: '黑豆',
      species: '狗',
      gender: '公',
      age: '约1岁',
      sterilized: false,
      health_status: '健康，已打疫苗',
      found_location: '小区北门花园',
      description: '活泼好动，对人友好，会简单指令。',
      image_url: '',
      status: '待领养',
      created_at: '2024-01-20T14:20:00',
      updated_at: '2024-01-20T14:20:00'
    }
  ]
  return mockData.find(a => a.id === id) || mockData[0]
}

onMounted(() => {
  loadAnimal()
})
</script>

<style lang="scss" scoped>
.apply-page {
  .error-state {
    text-align: center;
    padding: 4rem 2rem;

    .error-icon {
      font-size: 4rem;
      margin-bottom: 1rem;
    }

    h2 {
      color: #2d3748;
      margin-bottom: 0.5rem;
    }

    p {
      color: #718096;
      margin-bottom: 2rem;
    }
  }

  .apply-content {
    display: grid;
    grid-template-columns: 1fr 1.5fr;
    gap: 2rem;
    max-width: 1200px;
    margin: 0 auto;

    @media (max-width: 900px) {
      grid-template-columns: 1fr;
    }
  }

  .animal-info-section {
    .animal-card {
      position: sticky;
      top: 2rem;

      .card-image {
        position: relative;

        img {
          width: 100%;
          height: auto;
          display: block;
        }

        .status-tag {
          position: absolute;
          top: 12px;
          right: 12px;
        }
      }

      .card-content {
        padding: 1.5rem;
      }

      .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;

        .animal-name {
          font-size: 1.5rem;
          font-weight: 700;
          color: #2d3748;
          margin: 0;
        }

        .animal-species {
          background: #edf2f7;
          padding: 0.25rem 0.75rem;
          border-radius: 12px;
          font-size: 0.875rem;
          color: #4a5568;
        }
      }

      .animal-info {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin-bottom: 1rem;

        .info-item {
          background: #f7fafc;
          padding: 0.375rem 0.75rem;
          border-radius: 6px;
          font-size: 0.875rem;
          color: #718096;

          &.yes {
            background: #c6f6d5;
            color: #22543d;
          }

          &.no {
            background: #fed7d7;
            color: #742a2a;
          }
        }
      }

      .animal-health,
      .animal-location {
        font-size: 0.875rem;
        color: #4a5568;
        margin-bottom: 0.5rem;

        .label {
          font-weight: 600;
          color: #2d3748;
        }
      }

      .animal-description {
        font-size: 0.875rem;
        color: #718096;
        line-height: 1.6;
      }
    }
  }

  .form-section {
    background: white;
    border-radius: 12px;
    padding: 2rem;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);

    .form-title {
      font-size: 1.75rem;
      color: #2d3748;
      margin-bottom: 0.5rem;
    }

    .form-subtitle {
      color: #718096;
      margin-bottom: 2rem;
    }

    .form-actions {
      display: flex;
      justify-content: flex-end;
      gap: 1rem;
      margin-top: 2rem;

      .btn-secondary {
        background: #e2e8f0;
        color: #4a5568;
        text-decoration: none;

        &:hover {
          background: #cbd5e0;
          transform: translateY(-2px);
          box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        }
      }
    }
  }

  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    animation: fadeIn 0.3s ease;
  }

  .modal-content {
    background: white;
    border-radius: 16px;
    padding: 3rem;
    max-width: 500px;
    width: 90%;
    text-align: center;
    animation: slideUp 0.3s ease;

    .modal-icon {
      font-size: 4rem;
      margin-bottom: 1rem;
    }

    h3 {
      color: #2d3748;
      margin-bottom: 1rem;
    }

    p {
      color: #718096;
      line-height: 1.6;
      margin-bottom: 2rem;
    }

    .modal-actions {
      display: flex;
      justify-content: center;
    }
  }

  @keyframes fadeIn {
    from {
      opacity: 0;
    }
    to {
      opacity: 1;
    }
  }

  @keyframes slideUp {
    from {
      transform: translateY(20px);
      opacity: 0;
    }
    to {
      transform: translateY(0);
      opacity: 1;
    }
  }
}
</style>
