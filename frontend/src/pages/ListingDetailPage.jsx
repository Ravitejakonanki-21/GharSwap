import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import api, { getErrorMessage } from '../api'
import { useAuth } from '../AuthContext'
import { ErrorBanner, Loading } from '../components/Status'

export default function ListingDetailPage() {
  const { id } = useParams()
  const { user } = useAuth()
  const navigate = useNavigate()
  const [listing, setListing] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [form, setForm] = useState({
    check_in: '',
    check_out: '',
    guests_count: 1,
    message: '',
  })
  const [submitting, setSubmitting] = useState(false)
  const [notice, setNotice] = useState('')

  useEffect(() => {
    async function load() {
      setLoading(true)
      setError('')
      try {
        const { data } = await api.get(`/listings/${id}/`)
        setListing(data)
      } catch (err) {
        setError(getErrorMessage(err))
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [id])

  async function requestStay(event) {
    event.preventDefault()
    if (!user) {
      navigate('/login')
      return
    }
    setSubmitting(true)
    setError('')
    setNotice('')
    try {
      await api.post('/stay-requests/', {
        listing: Number(id),
        ...form,
        guests_count: Number(form.guests_count),
      })
      setNotice('Request sent. You can track it in Requests.')
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) return <Loading />
  if (error && !listing) return <ErrorBanner message={error} />
  if (!listing) return null

  const isOwner = user && listing.host_id === user.id

  return (
    <article className="split">
      <div className="card">
        <h1>{listing.title}</h1>
        <p>
          {listing.city} · {listing.address_area}
        </p>
        <p>{listing.description}</p>
        <p>Max guests: {listing.max_guests}</p>
        {listing.house_rules && (
          <>
            <h2>House rules</h2>
            <p>{listing.house_rules}</p>
          </>
        )}
        <h2>Availability</h2>
        {listing.availabilities?.length ? (
          <ul>
            {listing.availabilities.map((window) => (
              <li key={window.id}>
                {window.start_date} → {window.end_date}
              </li>
            ))}
          </ul>
        ) : (
          <p className="muted">No availability windows yet.</p>
        )}
        <p>
          Host:{' '}
          <Link to={`/users/${listing.host_id}`}>{listing.host_name}</Link>
        </p>
      </div>
      <div className="card">
        {isOwner ? (
          <p>
            This is your listing.{' '}
            <Link to={`/listings/${listing.id}/edit`}>Edit it</Link>
          </p>
        ) : (
          <form className="form" onSubmit={requestStay}>
            <h2>Request stay</h2>
            <ErrorBanner message={error} />
            {notice && <p className="status success">{notice}</p>}
            <label>
              Check in
              <input
                type="date"
                required
                value={form.check_in}
                onChange={(e) => setForm({ ...form, check_in: e.target.value })}
              />
            </label>
            <label>
              Check out
              <input
                type="date"
                required
                value={form.check_out}
                onChange={(e) => setForm({ ...form, check_out: e.target.value })}
              />
            </label>
            <label>
              Guests
              <input
                type="number"
                min="1"
                max={listing.max_guests}
                value={form.guests_count}
                onChange={(e) => setForm({ ...form, guests_count: e.target.value })}
              />
            </label>
            <label>
              Message
              <textarea
                rows="3"
                value={form.message}
                onChange={(e) => setForm({ ...form, message: e.target.value })}
              />
            </label>
            <button className="btn" disabled={submitting}>
              {submitting ? 'Sending…' : 'Request stay'}
            </button>
          </form>
        )}
      </div>
    </article>
  )
}
