import api from './api'

export const reportesService = {
  exportarExcel: (periodo) =>
    api.get('/reportes/excel', {
      params: { periodo },
      responseType: 'blob',
    }),

  enviarMasivoAutomatico: (payload) =>
    api.post('/reportes/whatsapp/enviar-masivo-automatico', payload),
}
