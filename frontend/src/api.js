const UNSAFE_METHODS = ['POST', 'PUT', 'PATCH', 'DELETE']

function getCookie(name) {
  const parts = document.cookie.split('; ')
  for (const part of parts) {
    const [key, ...rest] = part.split('=')
    if (key === name) {
      return decodeURIComponent(rest.join('='))
    }
  }
  return null
}

async function ensureCsrfToken() {
  let token = getCookie('csrftoken')
  if (!token) {
    await getCsrf()
    token = getCookie('csrftoken')
  }
  return token
}

async function request(url, method = 'GET', body) {
  const headers = {}

  if (body !== undefined) {
    headers['Content-Type'] = 'application/json'
  }

  if (UNSAFE_METHODS.includes(method)) {
    const token = await ensureCsrfToken()
    if (token) {
      headers['X-CSRFToken'] = token
    }
  }

  const response = await fetch(url, {
    method,
    headers,
    credentials: 'include',
    body: body !== undefined ? JSON.stringify(body) : undefined,
  })

  let data = null
  if (response.status !== 204) {
    const text = await response.text()
    if (text) {
      try {
        data = JSON.parse(text)
      } catch {
        data = text
      }
    }
  }

  if (!response.ok) {
    const error = new Error(`Request failed with status ${response.status}`)
    error.status = response.status
    error.data = data
    throw error
  }

  return data
}

export async function getCsrf() {
  await fetch('/api/auth/csrf/', { credentials: 'include' })
}

// data: { username, email, nickname, password, password_confirm }
export function register(data) {
  return request('/api/auth/register/', 'POST', data)
}

export async function login(username, password) {
  const user = await request('/api/auth/login/', 'POST', { username, password })
  // Django rotates the CSRF token on login, so get the new one
  await getCsrf()
  return user
}

export function logout() {
  return request('/api/auth/logout/', 'POST')
}

export function getMe() {
  return request('/api/auth/me/')
}

export function updateMe(data) {
  return request('/api/auth/me/', 'PATCH', data)
}
