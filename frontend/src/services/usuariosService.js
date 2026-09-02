import api from './api'

export const usuariosService = {
  listar: (params = {}) =>
    api.get('/usuarios/', { params }),

  obtener: (id) =>
    api.get(`/usuarios/${id}`),

  crear: (data) =>
    api.post('/usuarios/', data),

  actualizar: (id, data) =>
    api.put(`/usuarios/${id}`, data),

  eliminar: (id) =>
    api.delete(`/usuarios/${id}`),
}
