import api from './api'

export const configuracionService = {
  getDatosBancarios: () => api.get('/configuracion/datos-bancarios'),
  guardarDatosBancarios: (data) => api.post('/configuracion/datos-bancarios', data),
}
