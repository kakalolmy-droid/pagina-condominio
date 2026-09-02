import axios from 'axios'

// Usar ruta directa al backend en localhost:8000 para desarrollo
const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  timeout: 15000,
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
