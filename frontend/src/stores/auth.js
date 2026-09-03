import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || null)
  const rol = ref(localStorage.getItem('rol') || null)
  const nombre = ref(localStorage.getItem('nombre') || null)
  const usuarioId = ref(localStorage.getItem('usuarioId') || null)

  const isAuthenticated = computed(() => !!token.value)
  const isAdmin = computed(() => ['admin', 'junta'].includes(rol.value))
  const isPropietario = computed(() => rol.value === 'propietario')

  async function login(email, password) {
    const response = await api.post('/auth/login', {
      email: email.trim(),
      password: password,
    })

    const data = response.data
    token.value = data.access_token
    rol.value = data.rol
    nombre.value = data.nombre
    usuarioId.value = String(data.usuario_id)

    localStorage.setItem('token', data.access_token)
    localStorage.setItem('rol', data.rol)
    localStorage.setItem('nombre', data.nombre)
    localStorage.setItem('usuarioId', String(data.usuario_id))

    api.defaults.headers.common['Authorization'] = `Bearer ${data.access_token}`

    return data
  }

  async function registro(payload) {
    const response = await api.post('/auth/registro', payload)
    const data = response.data
    token.value = data.access_token
    rol.value = data.rol
    nombre.value = data.nombre
    usuarioId.value = String(data.usuario_id)

    localStorage.setItem('token', data.access_token)
    localStorage.setItem('rol', data.rol)
    localStorage.setItem('nombre', data.nombre)
    localStorage.setItem('usuarioId', String(data.usuario_id))

    api.defaults.headers.common['Authorization'] = `Bearer ${data.access_token}`

    return data
  }

  function logout() {
    token.value = null
    rol.value = null
    nombre.value = null
    usuarioId.value = null

    localStorage.removeItem('token')
    localStorage.removeItem('rol')
    localStorage.removeItem('nombre')
    localStorage.removeItem('usuarioId')

    delete api.defaults.headers.common['Authorization']
  }

  function inicializarToken() {
    if (token.value) {
      api.defaults.headers.common['Authorization'] = `Bearer ${token.value}`
    }
  }

  return {
    token,
    rol,
    nombre,
    usuarioId,
    isAuthenticated,
    isAdmin,
    isPropietario,
    login,
    registro,
    logout,
    inicializarToken,
  }
})
