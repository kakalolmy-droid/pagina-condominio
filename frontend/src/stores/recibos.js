import { defineStore } from 'pinia'
import { ref } from 'vue'
import { recibosService } from '@/services'

export const useRecibosStore = defineStore('recibos', () => {
  const lista = ref([])
  const cargando = ref(false)
  const error = ref(null)

  async function cargar(params = {}) {
    cargando.value = true
    try {
      const { data } = await recibosService.listar(params)
      lista.value = data
    } catch (e) {
      error.value = e.response?.data?.detail || 'Error al cargar recibos'
    } finally {
      cargando.value = false
    }
  }

  async function cargarMisRecibos() {
    cargando.value = true
    try {
      const { data } = await recibosService.misRecibos()
      lista.value = data
    } catch (e) {
      error.value = e.response?.data?.detail || 'Error al cargar sus recibos'
    } finally {
      cargando.value = false
    }
  }

  async function emitirMasivo(datos) {
    const { data } = await recibosService.emitirMasivo(datos)
    return data
  }

  return { lista, cargando, error, cargar, cargarMisRecibos, emitirMasivo }
})
