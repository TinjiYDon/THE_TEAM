import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 10000,
})

api.interceptors.response.use(
  (response) => {
    // 如果响应有 data 字段，直接返回 data，否则返回整个响应
    return response.data?.data !== undefined ? response.data : response.data
  },
  (error) => {
    console.error('API Error:', error)
    if (error.response) {
      // 服务器返回了错误响应
      return Promise.reject(error.response.data || error.message)
    } else if (error.request) {
      // 请求已发出但没有收到响应
      return Promise.reject({ message: '网络错误，请检查后端服务是否启动' })
    } else {
      // 其他错误
      return Promise.reject({ message: error.message || '未知错误' })
    }
  }
)

export default api

