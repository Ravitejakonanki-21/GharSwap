import { useEffect, useState } from 'react'
import { Link, Navigate } from 'react-router-dom'
import api, { getErrorMessage } from '../api'
import { useAuth } from '../AuthContext'
import { Empty, ErrorBanner, Loading } from '../components/Status'

export default function RequestsPage() {
  const { user, loading } = useAuth()
  const [tab, setTab] = useState('guest')
  const [items, setItems] = useState([])
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(true)

  async function load(role = tab) {
    setBusy(true)
    setError('')
    try {
      const { data } = await api.get('/stay-requests/', { params: { role } })
      setItems(data.results || [])
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setBusy(false)
    }
  }

  useEffect(() => {
    if (user) load(tab)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user, tab])

  async function act(id, action) {
    setError('')
    try {
      await api.post(`/stay-requests/${id}/${action}/`)
      await load(tab)
    } catch (err) {
      setError(getErrorMessage(err))
    }
  }

  if (loading) return <Loading />
  if (!user) return <Navigate to="/login" replace />

  return (
    <section>
      <h1>Requests</h1>
      <div className="tabs">
        <button className={tab === 'guest' ? 'tab on' : 'tab'} onClick={() => setTab('guest')}>
          As guest
        </button>
        <button className={tab === 'host' ? 'tab on' : 'tab'} onClick={() => setTab('host')}>
          As host
        </button>
      </div>
      <ErrorBanner message={error} />
      {busy ? (
        <Loading />
      ) : items.length === 0 ? (
        <Empty>No requests in this inbox.</Empty>
      ) : (
        <div className="stack">
          {items.map((item) => (
            <article key={item.id} className="card">
              <h2>
                <Link to={`/listings/${item.listing}`}>{item.listing_detail?.title}</Link>
              </h2>
              <p>
                {item.check_in} → {item.check_out} · {item.guests_count} guests · {item.guest_nights}{' '}
                credits
              </p>
              <p>Status: {item.status}</p>
              {item.message && <p>{item.message}</p>}
              <div className="row">
                {tab === 'host' && item.status === 'pending' && (
                  <>
                    <button className="btn" onClick={() => act(item.id, 'accept')}>
                      Accept
                    </button>
                    <button className="btn secondary" onClick={() => act(item.id, 'decline')}>
                      Decline
                    </button>
                  </>
                )}
                {['pending', 'accepted'].includes(item.status) && (
                  <button className="btn secondary" onClick={() => act(item.id, 'cancel')}>
                    Cancel
                  </button>
                )}
                {item.status === 'accepted' && (
                  <button className="btn" onClick={() => act(item.id, 'complete')}>
                    Mark completed
                  </button>
                )}
              </div>
            </article>
          ))}
        </div>
      )}
    </section>
  )
}
