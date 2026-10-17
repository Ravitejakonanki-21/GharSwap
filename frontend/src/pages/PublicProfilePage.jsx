import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import api, { getErrorMessage } from '../api'
import { useAuth } from '../AuthContext'
import { Empty, ErrorBanner, Loading } from '../components/Status'

export default function PublicProfilePage() {
  const { userId } = useParams()
  const { user } = useAuth()
  const [profile, setProfile] = useState(null)
  const [reviews, setReviews] = useState([])
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [loading, setLoading] = useState(true)
  const [report, setReport] = useState({ reason: '', details: '' })

  useEffect(() => {
    async function load() {
      setLoading(true)
      setError('')
      try {
        const [{ data: person }, { data: reviewData }] = await Promise.all([
          api.get(`/profiles/${userId}/`),
          api.get(`/users/${userId}/reviews/`),
        ])
        setProfile(person)
        setReviews(reviewData.results || [])
      } catch (err) {
        setError(getErrorMessage(err))
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [userId])

  async function blockUser() {
    try {
      await api.post('/blocks/', { blocked_user: Number(userId) })
      setNotice('User blocked')
    } catch (err) {
      setError(getErrorMessage(err))
    }
  }

  async function sendReport(event) {
    event.preventDefault()
    try {
      await api.post('/reports/', { reported_user: Number(userId), ...report })
      setNotice('Report submitted')
      setReport({ reason: '', details: '' })
    } catch (err) {
      setError(getErrorMessage(err))
    }
  }

  if (loading) return <Loading />
  if (error && !profile) return <ErrorBanner message={error} />

  return (
    <section className="split">
      <div className="card">
        <h1>{profile.display_name}</h1>
        <p>
          {profile.city || 'City not set'} {profile.id_verified ? '· ID verified' : ''}
        </p>
        <p>{profile.bio || 'No bio yet.'}</p>
        <p>Languages: {(profile.languages || []).join(', ') || '—'}</p>
        <ErrorBanner message={error} />
        {notice && <p className="status success">{notice}</p>}
        {user && user.id !== Number(userId) && (
          <button className="btn secondary" onClick={blockUser}>
            Block
          </button>
        )}
      </div>
      <div>
        <div className="card">
          <h2>Reviews</h2>
          {reviews.length === 0 ? (
            <Empty>No reviews yet.</Empty>
          ) : (
            reviews.map((review) => (
              <article key={review.id}>
                <strong>{review.rating}/5</strong>
                <p>{review.comment}</p>
              </article>
            ))
          )}
        </div>
        {user && user.id !== Number(userId) && (
          <form className="card form" onSubmit={sendReport}>
            <h2>Report</h2>
            <label>
              Reason
              <input
                value={report.reason}
                onChange={(e) => setReport({ ...report, reason: e.target.value })}
                required
              />
            </label>
            <label>
              Details
              <textarea
                rows="3"
                value={report.details}
                onChange={(e) => setReport({ ...report, details: e.target.value })}
              />
            </label>
            <button className="btn secondary">Submit report</button>
          </form>
        )}
      </div>
    </section>
  )
}
