<template>
  <div class="gallery-page">
    <div class="container">
      <div class="page-header">
        <h2 class="page-title">🐱 待领养小动物 🐶</h2>
        <p class="page-subtitle">每一个生命都值得被温柔以待</p>
      </div>

      <div class="filter-bar">
        <button
          v-for="filter in filters"
          :key="filter.value"
          :class="['filter-btn', { active: currentFilter === filter.value }]"
          @click="currentFilter = filter.value"
        >
          {{ filter.label }}
        </button>
      </div>

      <div v-if="loading" class="loading">
        <div class="spinner"></div>
        <span style="margin-left: 1rem;">加载中...</span>
      </div>

      <div v-else-if="animals.length === 0" class="empty-state">
        <div class="empty-icon">🐾</div>
        <p>暂无{{ currentFilter === 'all' ? '' : filterLabels[currentFilter] }}的小动物</p>
      </div>

      <div v-else class="masonry-container">
        <div
          v-for="animal in filteredAnimals"
          :key="animal.id"
          class="masonry-item"
        >
          <div class="animal-card card">
            <div class="card-image">
              <img
                :src="animal.image_url || getPlaceholderImage(animal.species)"
                :alt="animal.name"
                @error="handleImageError($event, animal.species)"
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
              <router-link
                :to="`/animals/apply/${animal.id}`"
                :class="['btn', 'btn-primary', 'apply-btn', { disabled: animal.status === '已领养' }]"
                @click.native.prevent="handleApplyClick(animal)"
              >
                {{ animal.status === '待领养' ? '申请领养' : animal.status === '申请中' ? '已有人申请' : '已领养' }}
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="toast.show" :class="['toast', toast.type]">
      {{ toast.message }}
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { animalApi } from '@/api'

const router = useRouter()

const animals = ref([])
const loading = ref(true)
const currentFilter = ref('all')

const filters = [
  { label: '全部', value: 'all' },
  { label: '待领养', value: '待领养' },
  { label: '申请中', value: '申请中' },
  { label: '已领养', value: '已领养' }
]

const filterLabels = {
  '待领养': '待领养',
  '申请中': '申请中',
  '已领养': '已领养'
}

const toast = ref({
  show: false,
  message: '',
  type: 'success'
})

const filteredAnimals = computed(() => {
  if (currentFilter.value === 'all') {
    return animals.value
  }
  return animals.value.filter(a => a.status === currentFilter.value)
})

const loadAnimals = async () => {
  loading.value = true
  try {
    const data = await animalApi.getAnimals()
    animals.value = data
  } catch (error) {
    console.error('加载动物列表失败:', error)
    showToast('加载数据失败，请稍后重试', 'error')
    animals.value = getMockData()
  } finally {
    loading.value = false
  }
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

const getPlaceholderImage = (species) => {
  if (species === '猫') {
    return 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=cute%20stray%20cat%20portrait%20warm%20lighting%20professional%20photography&image_size=square_hd'
  } else if (species === '狗') {
    return 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=cute%20stray%20dog%20portrait%20warm%20lighting%20professional%20photography&image_size=square_hd'
  }
  return 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=cute%20small%20animal%20portrait%20warm%20lighting%20professional%20photography&image_size=square_hd'
}

const handleImageError = (event, species) => {
  event.target.src = getPlaceholderImage(species)
}

const handleApplyClick = (animal) => {
  if (animal.status === '已领养') {
    showToast('该动物已被领养', 'error')
    return
  }
  if (animal.status === '申请中') {
    showToast('该动物已有申请正在审核中', 'error')
    return
  }
  router.push(`/animals/apply/${animal.id}`)
}

const showToast = (message, type = 'success') => {
  toast.value = { show: true, message, type }
  setTimeout(() => {
    toast.value.show = false
  }, 3000)
}

const getMockData = () => [
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
  },
  {
    id: 3,
    name: '小白',
    species: '猫',
    gender: '母',
    age: '约6个月',
    sterilized: false,
    health_status: '健康',
    found_location: '小区5号楼地下室',
    description: '胆小但很粘人，熟悉后会非常亲人。',
    image_url: '',
    status: '申请中',
    created_at: '2024-02-01T09:15:00',
    updated_at: '2024-02-10T16:30:00'
  }
]

onMounted(() => {
  loadAnimals()
})
</script>

<style lang="scss" scoped>
.gallery-page {
  .page-header {
    text-align: center;
    margin-bottom: 2rem;

    .page-title {
      font-size: 2.5rem;
      color: #2d3748;
      margin-bottom: 0.5rem;
    }

    .page-subtitle {
      font-size: 1.125rem;
      color: #718096;
    }
  }

  .filter-bar {
    display: flex;
    justify-content: center;
    gap: 1rem;
    margin-bottom: 2rem;
    flex-wrap: wrap;

    .filter-btn {
      padding: 0.5rem 1.5rem;
      border: 2px solid #e2e8f0;
      background: white;
      border-radius: 20px;
      cursor: pointer;
      transition: all 0.3s;
      font-size: 0.875rem;
      font-weight: 500;

      &:hover {
        border-color: #667eea;
        color: #667eea;
      }

      &.active {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-color: transparent;
        color: white;
      }
    }
  }

  .empty-state {
    text-align: center;
    padding: 4rem 2rem;
    color: #a0aec0;

    .empty-icon {
      font-size: 4rem;
      margin-bottom: 1rem;
    }

    p {
      font-size: 1.125rem;
    }
  }

  .masonry-container {
    column-count: 4;
    column-gap: 1.5rem;

    @media (max-width: 1024px) {
      column-count: 3;
    }

    @media (max-width: 768px) {
      column-count: 2;
    }

    @media (max-width: 480px) {
      column-count: 1;
    }
  }

  .masonry-item {
    break-inside: avoid;
    margin-bottom: 1.5rem;
  }

  .animal-card {
    .card-image {
      position: relative;
      width: 100%;

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
      padding: 1.25rem;
    }

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 0.75rem;

      .animal-name {
        font-size: 1.25rem;
        font-weight: 700;
        color: #2d3748;
        margin: 0;
      }

      .animal-species {
        background: #edf2f7;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.75rem;
        color: #4a5568;
      }
    }

    .animal-info {
      display: flex;
      flex-wrap: wrap;
      gap: 0.5rem;
      margin-bottom: 0.75rem;

      .info-item {
        background: #f7fafc;
        padding: 0.25rem 0.5rem;
        border-radius: 6px;
        font-size: 0.75rem;
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
      margin-bottom: 1rem;
      line-height: 1.5;
    }

    .apply-btn {
      width: 100%;

      &.disabled {
        background: #cbd5e0;
        cursor: not-allowed;

        &:hover {
          transform: none;
          box-shadow: none;
        }
      }
    }
  }
}
</style>
