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

  crearIndividual: (data) =>
    api.post('/recibos/crear-individual', data),

  aprobarPago: (id) =>
    api.post(`/recibos/${id}/aprobar`),

  rechazarPago: (id, motivo) =>
    api.post(`/recibos/${id}/rechazar`, null, { params: { motivo } }),

  eliminar: (id) =>
    api.delete(`/recibos/${id}`),
}
