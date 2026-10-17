import { useState } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import { useAuth } from '../AuthContext'
import { getErrorMessage } from '../api'
import { ErrorBanner, Loading } from '../components/Status'

export function LoginPage() {
  const { user, loading, login } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  if (loading) return <Loading />
  if (user) return <Navigate to="/" replace />

  async function onSubmit(event) {
    event.preventDefault()
    setError('')
    setSubmitting(true)
    try {
      await login(email, password)
      navigate('/search')
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <form className="card form" onSubmit={onSubmit}>
      <h1>Welcome back</h1>
      <ErrorBanner message={error} />
      <label>
        Email
        <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
      </label>
      <label>
        Password
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
      </label>
      <button className="btn" disabled={submitting}>
        {submitting ? 'Signing in…' : 'Log in'}
      </button>
      <p>
        New here? <Link to="/register">Create an account</Link>
      </p>
    </form>
  )
}

export function RegisterPage() {
  const { user, loading, register } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({
    email: '',
    password: '',
    display_name: '',
    phone: '',
  })
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  if (loading) return <Loading />
  if (user) return <Navigate to="/" replace />

  function update(key, value) {
    setForm((current) => ({ ...current, [key]: value }))
  }

  async function onSubmit(event) {
    event.preventDefault()
    setError('')
    setSubmitting(true)
    try {
      await register(form)
      navigate('/profile')
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <form className="card form" onSubmit={onSubmit}>
      <h1>Join GharSwap</h1>
      <p className="muted">You start with 2 guest-night credits.</p>
      <ErrorBanner message={error} />
      <label>
        Display name
        <input value={form.display_name} onChange={(e) => update('display_name', e.target.value)} />
      </label>
      <label>
        Email
        <input
          type="email"
          value={form.email}
          onChange={(e) => update('email', e.target.value)}
          required
        />
      </label>
      <label>
        Phone
        <input value={form.phone} onChange={(e) => update('phone', e.target.value)} />
      </label>
      <label>
        Password
        <input
          type="password"
          value={form.password}
          onChange={(e) => update('password', e.target.value)}
          required
          minLength={8}
        />
      </label>
      <button className="btn" disabled={submitting}>
        {submitting ? 'Creating account…' : 'Register'}
      </button>
      <p>
        Already have an account? <Link to="/login">Log in</Link>
      </p>
    </form>
  )
}
