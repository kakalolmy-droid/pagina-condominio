import { defineStore } from 'pinia'
import { ref } from 'vue'
import { usuariosService } from '@/services'

export const useUsuariosStore = defineStore('usuarios', () => {
  const lista = ref([])
  const cargando = ref(false)
  const error = ref(null)

  async function cargar(params = {}) {
    cargando.value = true
    error.value = null
    try {
      const { data } = await usuariosService.listar(params)
      lista.value = data
    } catch (e) {
      error.value = e.response?.data?.detail || 'Error al cargar usuarios'
    } finally {
      cargando.value = false
    }
  }

  async function crear(data) {
    const { data: nuevo } = await usuariosService.crear(data)
    lista.value.push(nuevo)
    return nuevo
  }

  async function actualizar(id, data) {
    const { data: actualizado } = await usuariosService.actualizar(id, data)
    const idx = lista.value.findIndex(u => u.id === id)
    if (idx !== -1) lista.value[idx] = actualizado
    return actualizado
  }

  async function eliminar(id) {
    await usuariosService.eliminar(id)
    lista.value = lista.value.filter(u => u.id !== id)
  }

  return { lista, cargando, error, cargar, crear, actualizar, eliminar }
})
