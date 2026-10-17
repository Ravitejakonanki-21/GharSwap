import { createContext, useContext, useEffect, useMemo, useState } from 'react'
import api from './api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(true)

  async function loadMe() {
    const token = localStorage.getItem('access')
    if (!token) {
      setUser(null)
      setProfile(null)
      setLoading(false)
      return
    }
    try {
      const [{ data: me }, { data: mine }] = await Promise.all([
        api.get('/auth/me/'),
        api.get('/profiles/me/'),
      ])
      setUser(me)
      setProfile(mine)
    } catch {
      setUser(null)
      setProfile(null)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadMe()
  }, [])

  async function login(email, password) {
    const { data } = await api.post('/auth/login/', { email, password })
    localStorage.setItem('access', data.access)
    localStorage.setItem('refresh', data.refresh)
    await loadMe()
  }

  async function register(payload) {
    await api.post('/auth/register/', payload)
    await login(payload.email, payload.password)
  }

  function logout() {
    localStorage.removeItem('access')
    localStorage.removeItem('refresh')
    setUser(null)
    setProfile(null)
  }

  const value = useMemo(
    () => ({ user, profile, loading, login, register, logout, reload: loadMe }),
    [user, profile, loading],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  return useContext(AuthContext)
}
