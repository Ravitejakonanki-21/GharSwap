import { useEffect, useState } from 'react'
import { Navigate } from 'react-router-dom'
import api, { getErrorMessage } from '../api'
import { useAuth } from '../AuthContext'
import { Empty, ErrorBanner, Loading } from '../components/Status'

export default function CreditsPage() {
  const { user, loading } = useAuth()
  const [balance, setBalance] = useState(null)
  const [ledger, setLedger] = useState([])
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(true)

  useEffect(() => {
    if (!user) return
    async function load() {
      setBusy(true)
      try {
        const [{ data: credits }, { data: history }] = await Promise.all([
          api.get('/credits/'),
          api.get('/credits/ledger/'),
        ])
        setBalance(credits)
        setLedger(history)
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
  if (busy) return <Loading />

  return (
    <section>
      <h1>Credits</h1>
      <ErrorBanner message={error} />
      {balance && (
        <div className="stats">
          <article className="card">
            <p className="muted">Ledger balance</p>
            <strong>{balance.balance}</strong>
          </article>
          <article className="card">
            <p className="muted">Reserved</p>
            <strong>{balance.reserved}</strong>
          </article>
          <article className="card">
            <p className="muted">Available</p>
            <strong>{balance.available}</strong>
          </article>
        </div>
      )}
      <h2>History</h2>
      {ledger.length === 0 ? (
        <Empty>No ledger entries yet.</Empty>
      ) : (
        <ul className="ledger">
          {ledger.map((entry) => (
            <li key={entry.id}>
              <span>{entry.reason}</span>
              <span>
                {entry.amount > 0 ? '+' : ''}
                {entry.amount}
              </span>
              <span className="muted">{new Date(entry.created_at).toLocaleString()}</span>
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}
