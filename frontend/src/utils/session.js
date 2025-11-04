export function getQueryParam(name) {
  try {
    const params = new URLSearchParams(window.location.search)
    return params.get(name)
  } catch {
    return null
  }
}

const USER_KEY = 'demo_user_id'
const CITY_KEY = 'preferred_city'

export function getCurrentUserId() {
  const fromUrl = getQueryParam('user')
  if (fromUrl) {
    localStorage.setItem(USER_KEY, String(fromUrl))
    return parseInt(fromUrl, 10) || 1
  }
  const saved = localStorage.getItem(USER_KEY)
  return saved ? parseInt(saved, 10) : 1
}

export function getCurrentCity() {
  const fromUrl = getQueryParam('city')
  if (fromUrl) {
    localStorage.setItem(CITY_KEY, String(fromUrl))
    return fromUrl
  }
  return localStorage.getItem(CITY_KEY) || 'shanghai'
}

export function setCurrentUserId(id) {
  localStorage.setItem(USER_KEY, String(id))
}

export function setCurrentCity(city) {
  localStorage.setItem(CITY_KEY, String(city))
}
