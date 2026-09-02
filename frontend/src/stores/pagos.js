import { defineStore } from 'pinia'
import { ref } from 'vue'
import { pagosService, conciliacionService } from '@/services'

export const usePagosStore = defineStore('pagos', () => {
  const misPagos = ref([])
  const pendientesConciliacion = ref([])
  const cargando = ref(false)
  const error = ref(null)

  async function cargarMisPagos() {
    cargando.value = true
    try {
      const { data } = await pagosService.misPagos()
      misPagos.value = data
    } catch (e) {
      error.value = e.response?.data?.detail || 'Error al cargar pagos'
    } finally {
      cargando.value = false
    }
  }

  async function cargarPendientes() {
    cargando.value = true
    try {
      const { data } = await conciliacionService.pendientes()
      pendientesConciliacion.value = data
    } catch (e) {
      error.value = e.response?.data?.detail || 'Error al cargar pendientes'
    } finally {
      cargando.value = false
    }
  }

  async function reportarPago(formData) {
    const { data } = await pagosService.reportar(formData)
    misPagos.value.unshift(data)
    return data
  }

  async function aprobar(pagoId) {
    const { data } = await conciliacionService.aprobar(pagoId)
    pendientesConciliacion.value = pendientesConciliacion.value.filter(p => p.id !== pagoId)
    return data
  }

  async function rechazar(pagoId, motivo) {
    const { data } = await conciliacionService.rechazar(pagoId, motivo)
    pendientesConciliacion.value = pendientesConciliacion.value.filter(p => p.id !== pagoId)
    return data
  }

  return {
    misPagos,
    pendientesConciliacion,
    cargando,
    error,
    cargarMisPagos,
    cargarPendientes,
    reportarPago,
    aprobar,
    rechazar,
  }
})
