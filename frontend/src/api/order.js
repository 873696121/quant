import request from './index'

export const orderApi = {
  list(params) {
    return request.get('/orders', { params })
  },

  get(id) {
    return request.get(`/orders/${id}`)
  },

  create(data) {
    return request.post('/orders', data)
  },

  cancel(id) {
    return request.post(`/orders/${id}/cancel`)
  },

  getHistory(params) {
    return request.get('/orders/history', { params })
  }
}
