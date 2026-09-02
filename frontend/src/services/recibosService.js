import api from './api'

export const recibosService = {
  listar: (params = {}) =>
    api.get('/recibos/', { params }),

  misRecibos: () =>
    api.get('/recibos/mis-recibos'),

  obtener: (id) =>
    api.get(`/recibos/${id}`),

  emitirMasivo: (data) =>
    api.post('/recibos/emitir-masivo', data),
}
