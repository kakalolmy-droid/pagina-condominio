import api from './api'

export const conciliacionService = {
  pendientes: () =>
    api.get('/conciliacion/pendientes'),

  aprobar: (pagoId) =>
    api.post(`/conciliacion/${pagoId}/aprobar`),

  rechazar: (pagoId, motivo) =>
    api.post(`/conciliacion/${pagoId}/rechazar`, null, {
      params: { motivo },
    }),

  descargarSolvencia: (pagoId) =>
    api.get(`/conciliacion/solvencia/${pagoId}/pdf`, {
      responseType: 'blob',
    }),
}
