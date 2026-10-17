import { useEffect, useState } from 'react'
import { Navigate } from 'react-router-dom'
import api, { getErrorMessage } from '../api'
import { useAuth } from '../AuthContext'
import { ErrorBanner, Loading } from '../components/Status'

export default function ProfilePage() {
  const { user, profile, loading, reload } = useAuth()
  const [form, setForm] = useState({
    display_name: '',
    bio: '',
    city: '',
    languages: '',
  })
  const [error, setError] = useState('')
  const [saved, setSaved] = useState('')
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    if (profile) {
      setForm({
        display_name: profile.display_name || '',
        bio: profile.bio || '',
        city: profile.city || '',
        languages: (profile.languages || []).join(', '),
      })
    }
  }, [profile])

  if (loading) return <Loading />
  if (!user) return <Navigate to="/login" replace />

  function update(key, value) {
    setForm((current) => ({ ...current, [key]: value }))
  }

  async function onSubmit(event) {
    event.preventDefault()
    setError('')
    setSaved('')
    setSubmitting(true)
    try {
      const payload = {
        display_name: form.display_name,
        bio: form.bio,
        city: form.city,
        languages: form.languages
          .split(',')
          .map((item) => item.trim())
          .filter(Boolean),
      }
      await api.patch('/profiles/me/', payload)
      await reload()
      setSaved('Profile saved')
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <form className="card form" onSubmit={onSubmit}>
      <h1>Your profile</h1>
      <ErrorBanner message={error} />
      {saved && <p className="status success">{saved}</p>}
      <label>
        Display name
        <input value={form.display_name} onChange={(e) => update('display_name', e.target.value)} />
      </label>
      <label>
        City
        <input value={form.city} onChange={(e) => update('city', e.target.value)} />
      </label>
      <label>
        Languages (comma separated)
        <input value={form.languages} onChange={(e) => update('languages', e.target.value)} />
      </label>
      <label>
        Bio
        <textarea rows="4" value={form.bio} onChange={(e) => update('bio', e.target.value)} />
      </label>
      <button className="btn" disabled={submitting}>
        {submitting ? 'Saving…' : 'Save profile'}
      </button>
    </form>
  )
}
