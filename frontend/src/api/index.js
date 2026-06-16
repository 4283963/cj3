import axios from 'axios'

const api = axios.create({
  baseURL: '/api/vinit',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

api.interceptors.request.use(
  (config) => {
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

api.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

export const animalApi = {
  getAnimals: (status = '') => {
    const params = status ? { status } : {}
    return api.get('/animals', { params })
  },

  getAnimal: (id) => {
    return api.get(`/animals/${id}`)
  },

  createAnimal: (data) => {
    return api.post('/animals', data)
  },

  updateAnimal: (id, data) => {
    return api.patch(`/animals/${id}`, data)
  }
}

export const applicationApi = {
  createApplication: (data) => {
    return api.post('/apply', data)
  },

  getApplications: () => {
    return api.get('/applications')
  }
}

export default api
