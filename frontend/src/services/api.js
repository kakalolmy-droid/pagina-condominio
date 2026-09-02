import axios from 'axios'

// Detecta automáticamente si está corriendo en Vercel o en Localhost
const getBaseURL = () => {
  if (import.meta.env.VITE_API_URL) {
    return `${import.meta.env.VITE_API_URL}/api`
  }
  // Si está en producción en Vercel o similar
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
