import api from './api'

export const tasaService = {
  actual: () =>
    api.get('/tasa/actual'),

  historial: (limite = 30) =>
    api.get('/tasa/historial', { params: { limite } }),

  sincronizar: () =>
    api.post('/tasa/sincronizar'),
}
