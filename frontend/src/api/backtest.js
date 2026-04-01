import request from './index'

export const backtestApi = {
  list(params) {
    return request.get('/backtests', { params })
  },

  get(id) {
    return request.get(`/backtests/${id}`)
  },

  create(data) {
    return request.post('/backtests', data)
  },

  delete(id) {
    return request.delete(`/backtests/${id}`)
  },

  getResults(id) {
    return request.get(`/backtests/${id}/results`)
  },

  getLogs(id) {
    return request.get(`/backtests/${id}/logs`)
  }
}
