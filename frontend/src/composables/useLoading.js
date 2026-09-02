import { ref } from 'vue'

export function useLoading() {
  const cargando = ref(false)
  const error = ref(null)

  async function ejecutar(fn) {
    cargando.value = true
    error.value = null
    try {
      return await fn()
    } catch (e) {
      error.value = e.response?.data?.detail || e.message || 'Error desconocido'
      throw e
    } finally {
      cargando.value = false
    }
  }

  function limpiarError() {
    error.value = null
  }

  return { cargando, error, ejecutar, limpiarError }
}
