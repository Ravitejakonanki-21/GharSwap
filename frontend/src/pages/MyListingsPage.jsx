import { useEffect, useState } from 'react'
import { Link, Navigate, useNavigate, useParams } from 'react-router-dom'
import api, { getErrorMessage } from '../api'
import { useAuth } from '../AuthContext'
import { Empty, ErrorBanner, Loading } from '../components/Status'

const emptyForm = {
  title: '',
  description: '',
  city: '',
  address_area: '',
  max_guests: 2,
  house_rules: '',
  is_active: true,
}

export function MyListingsPage() {
  const { user, loading } = useAuth()
  const [listings, setListings] = useState([])
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(true)

  useEffect(() => {
    if (!user) return
    async function load() {
      setBusy(true)
      try {
        const { data } = await api.get('/listings/mine/')
        setListings(data.results || data)
      } catch (err) {
        setError(getErrorMessage(err))
      } finally {
        setBusy(false)
      }
    }
    load()
  }, [user])

  if (loading) return <Loading />
  if (!user) return <Navigate to="/login" replace />

  return (
    <section>
      <div className="row">
        <h1>My listings</h1>
        <Link className="btn" to="/listings/new">
          Add listing
        </Link>
      </div>
      <ErrorBanner message={error} />
      {busy ? (
        <Loading />
      ) : listings.length === 0 ? (
        <Empty>You have not listed a home yet.</Empty>
      ) : (
        <div className="grid">
          {listings.map((listing) => (
            <article key={listing.id} className="card">
              <h2>{listing.title}</h2>
              <p>
                {listing.city} · {listing.address_area}
              </p>
              <p>{listing.is_active ? 'Active' : 'Inactive'}</p>
              <Link to={`/listings/${listing.id}/edit`}>Edit</Link>
            </article>
          ))}
        </div>
      )}
    </section>
  )
}

export function ListingFormPage() {
  const { user, loading } = useAuth()
  const { id } = useParams()
  const navigate = useNavigate()
  const [form, setForm] = useState(emptyForm)
  const [availability, setAvailability] = useState({ start_date: '', end_date: '' })
  const [windows, setWindows] = useState([])
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(Boolean(id))
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    if (!id) return
    async function load() {
      setBusy(true)
      try {
        const { data } = await api.get(`/listings/${id}/`)
        setForm({
          title: data.title,
          description: data.description,
          city: data.city,
          address_area: data.address_area,
          max_guests: data.max_guests,
          house_rules: data.house_rules,
          is_active: data.is_active,
        })
        setWindows(data.availabilities || [])
      } catch (err) {
        setError(getErrorMessage(err))
      } finally {
        setBusy(false)
      }
    }
    load()
  }, [id])

  if (loading || busy) return <Loading />
  if (!user) return <Navigate to="/login" replace />

  function update(key, value) {
    setForm((current) => ({ ...current, [key]: value }))
  }

  async function onSubmit(event) {
    event.preventDefault()
    setSubmitting(true)
    setError('')
    try {
      const payload = { ...form, max_guests: Number(form.max_guests) }
      if (id) {
        await api.patch(`/listings/${id}/`, payload)
        navigate('/listings/mine')
      } else {
        const { data } = await api.post('/listings/', payload)
        navigate(`/listings/${data.id}/edit`)
      }
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setSubmitting(false)
    }
  }

  async function addAvailability(event) {
    event.preventDefault()
    try {
      const { data } = await api.post(`/listings/${id}/availability/`, availability)
      setWindows((current) => [...current, data])
      setAvailability({ start_date: '', end_date: '' })
    } catch (err) {
      setError(getErrorMessage(err))
    }
  }

  return (
    <section className="split">
      <form className="card form" onSubmit={onSubmit}>
        <h1>{id ? 'Edit listing' : 'New listing'}</h1>
        <ErrorBanner message={error} />
        <label>
          Title
          <input value={form.title} onChange={(e) => update('title', e.target.value)} required />
        </label>
        <label>
          City
          <input value={form.city} onChange={(e) => update('city', e.target.value)} required />
        </label>
        <label>
          Area (not exact address)
          <input
            value={form.address_area}
            onChange={(e) => update('address_area', e.target.value)}
            required
          />
        </label>
        <label>
          Max guests
          <input
            type="number"
            min="1"
            value={form.max_guests}
            onChange={(e) => update('max_guests', e.target.value)}
          />
        </label>
        <label>
          Description
          <textarea
            rows="4"
            value={form.description}
            onChange={(e) => update('description', e.target.value)}
            required
          />
        </label>
        <label>
          House rules
          <textarea
            rows="3"
            value={form.house_rules}
            onChange={(e) => update('house_rules', e.target.value)}
          />
        </label>
        <label className="checkbox">
          <input
            type="checkbox"
            checked={form.is_active}
            onChange={(e) => update('is_active', e.target.checked)}
          />
          Active
        </label>
        <button className="btn" disabled={submitting}>
          {submitting ? 'Saving…' : 'Save listing'}
        </button>
      </form>
      {id && (
        <form className="card form" onSubmit={addAvailability}>
          <h2>Availability</h2>
          {windows.map((window) => (
            <p key={window.id}>
              {window.start_date} → {window.end_date}
            </p>
          ))}
          <label>
            Start
            <input
              type="date"
              value={availability.start_date}
              onChange={(e) => setAvailability({ ...availability, start_date: e.target.value })}
              required
            />
          </label>
          <label>
            End
            <input
              type="date"
              value={availability.end_date}
              onChange={(e) => setAvailability({ ...availability, end_date: e.target.value })}
              required
            />
          </label>
          <button className="btn secondary">Add window</button>
        </form>
      )}
    </section>
  )
}
