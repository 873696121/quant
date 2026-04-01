import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useMarketStore = defineStore('market', () => {
  const watchlist = ref([])
  const realTimeData = ref({})
  const selectedStock = ref(null)

  function addToWatchlist(stockCode) {
    if (!watchlist.value.includes(stockCode)) {
      watchlist.value.push(stockCode)
    }
  }

  function removeFromWatchlist(stockCode) {
    const index = watchlist.value.indexOf(stockCode)
    if (index > -1) {
      watchlist.value.splice(index, 1)
    }
  }

  function updateRealTimeData(stockCode, data) {
    realTimeData.value[stockCode] = data
  }

  function setSelectedStock(stock) {
    selectedStock.value = stock
  }

  function clearRealTimeData() {
    realTimeData.value = {}
  }

  return {
    watchlist,
    realTimeData,
    selectedStock,
    addToWatchlist,
    removeFromWatchlist,
    updateRealTimeData,
    setSelectedStock,
    clearRealTimeData
  }
})
