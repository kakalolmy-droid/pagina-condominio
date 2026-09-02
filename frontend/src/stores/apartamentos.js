import { defineStore } from 'pinia'
import { ref } from 'vue'
import { apartamentosService } from '@/services'

export const useApartamentosStore = defineStore('apartamentos', () => {
  const lista = ref([])
  const matrizDeudas = ref([])
  const cargando = ref(false)
  const error = ref(null)

  async function cargar() {
    cargando.value = true
    try {
      const { data } = await apartamentosService.listar()
      lista.value = data
    } catch (e) {
      error.value = e.response?.data?.detail || 'Error al cargar apartamentos'
    } finally {
      cargando.value = false
    }
  }

  async function cargarMatrizDeudas() {
    cargando.value = true
    try {
      const { data } = await apartamentosService.matrizDeudas()
      matrizDeudas.value = data
    } catch (e) {
      error.value = e.response?.data?.detail || 'Error al cargar deudas'
    } finally {
      cargando.value = false
    }
  }

  async function crear(data) {
    const { data: nuevo } = await apartamentosService.crear(data)
    lista.value.push(nuevo)
    return nuevo
  }

  async function actualizar(id, data) {
    const { data: actualizado } = await apartamentosService.actualizar(id, data)
    const idx = lista.value.findIndex(a => a.id === id)
    if (idx !== -1) lista.value[idx] = actualizado
    return actualizado
  }

  async function eliminar(id) {
    await apartamentosService.eliminar(id)
    lista.value = lista.value.filter(a => a.id !== id)
  }

  return { lista, matrizDeudas, cargando, error, cargar, cargarMatrizDeudas, crear, actualizar, eliminar }
})
