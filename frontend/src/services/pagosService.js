import api from './api'

export const pagosService = {
  misPagos: () =>
    api.get('/pagos/mis-pagos'),

  reportar: (formData) =>
    api.post('/pagos/reportar', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
}
