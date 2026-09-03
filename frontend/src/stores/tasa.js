import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/services/api'

export const useTasaStore = defineStore('tasa', () => {
  const tasaActual = ref(null)
  const fecha = ref(null)
  const cargando = ref(false)

  async function cargarTasa() {
    cargando.value = true
    try {
      const hoyLocal = new Date().toLocaleDateString('en-CA')

      // 1. Intentar consultar la API pública en tiempo real de DolarAPI
      try {
        const respuesta = await fetch('https://ve.dolarapi.com/v1/dolares/oficial')
        if (respuesta.ok) {
          const datos = await respuesta.json()
          if (datos && datos.promedio) {
            tasaActual.value = parseFloat(datos.promedio)
            fecha.value = datos.fechaActualizacion?.split('T')[0] || hoyLocal
            cargando.value = false
            return
          }
        }
      } catch (errApi) {
        console.warn('Consulta directa a DolarAPI falló, recurriendo al backend local:', errApi)
      }

      // 2. Si falla la llamada directa, consultar el backend sincronizado
      const { data } = await api.get('/tasa/actual')
      tasaActual.value = parseFloat(data.tasa_usd_ves)
      fecha.value = data.fecha || hoyLocal
    } catch (e) {
      console.error('No se pudo cargar la tasa BCV:', e)
    } finally {
      cargando.value = false
    }
  }

  function convertirUSDaVES(montoUSD) {
    if (!tasaActual.value || !montoUSD) return 0
    return (parseFloat(montoUSD) * parseFloat(tasaActual.value)).toFixed(2)
  }

  return { tasaActual, fecha, cargando, cargarTasa, convertirUSDaVES }
})
