import api from './api'

export const apartamentosService = {
  listar: () =>
    api.get('/apartamentos/'),

  obtener: (id) =>
    api.get(`/apartamentos/${id}`),

  crear: (data) =>
    api.post('/apartamentos/', data),

  actualizar: (id, data) =>
    api.put(`/apartamentos/${id}`, data),

  eliminar: (id) =>
    api.delete(`/apartamentos/${id}`),

  matrizDeudas: () =>
    api.get('/apartamentos/deudas'),

  sumaAlicuotas: () =>
    api.get('/apartamentos/suma-alicuotas'),
}
