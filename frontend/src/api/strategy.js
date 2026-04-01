import request from './index'

export const strategyApi = {
  list(params) {
    return request.get('/strategies', { params })
  },

  get(id) {
    return request.get(`/strategies/${id}`)
  },

  create(data) {
    return request.post('/strategies', data)
  },

  update(id, data) {
    return request.put(`/strategies/${id}`, data)
  },

  delete(id) {
    return request.delete(`/strategies/${id}`)
  },

  run(id, params) {
    return request.post(`/strategies/${id}/run`, params)
  },

  stop(id) {
    return request.post(`/strategies/${id}/stop`)
  }
}
