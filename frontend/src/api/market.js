import request from './index'

export const marketApi = {
  getQuote(stockCode) {
    return request.get(`/market/quote/${stockCode}`)
  },

  getQuotes(stockCodes) {
    return request.post('/market/quotes', { codes: stockCodes })
  },

  getKline(stockCode, params) {
    return request.get(`/market/kline/${stockCode}`, { params })
  },

  getTick(stockCode, params) {
    return request.get(`/market/tick/${stockCode}`, { params })
  },

  search(keyword) {
    return request.get('/market/search', { params: { keyword } })
  }
}
