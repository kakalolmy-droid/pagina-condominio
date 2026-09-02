import axios from 'axios'

// Detecta automáticamente la URL del backend según el entorno
const getBaseURL = () => {
  const envUrl = import.meta.env.VITE_API_URL
  if (envUrl) {
    return envUrl.endsWith('/api') ? envUrl : `${envUrl}/api`
  }
  if (typeof window !== 'undefined' && window.location.hostname !== 'localhost') {
    return 'https://alcatraz-api.onrender.com/api'
  }
  return 'http://localhost:8000/api'
}

const api = axios.create({
  baseURL: getBaseURL(),
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Interceptor para inyectar el Bearer Token en todas las peticiones
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Interceptor de respuesta: maneja errores 401 globalmente EXCEPTO en login
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const esLogin = error.config?.url?.includes('/auth/login')
    if (error.response?.status === 401 && !esLogin) {
      localStorage.removeItem('token')
      localStorage.removeItem('rol')
      localStorage.removeItem('nombre')
      localStorage.removeItem('usuarioId')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default api
