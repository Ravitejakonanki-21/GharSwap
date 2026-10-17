import { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import api, { getErrorMessage } from '../api'
import { Empty, ErrorBanner, Loading } from '../components/Status'

export default function SearchPage() {
  const [params, setParams] = useSearchParams()
  const [filters, setFilters] = useState({
    city: params.get('city') || '',
    check_in: params.get('check_in') || '',
    check_out: params.get('check_out') || '',
    guests: params.get('guests') || '1',
  })
  const [results, setResults] = useState([])
  const [count, setCount] = useState(0)
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  function update(key, value) {
    setFilters((current) => ({ ...current, [key]: value }))
  }

  async function load(nextPage = 1, source = filters) {
    setLoading(true)
    setError('')
    try {
      const query = { page: nextPage }
      Object.entries(source).forEach(([key, value]) => {
        if (value) query[key] = value
      })
      const { data } = await api.get('/listings/', { params: query })
      setResults(data.results || [])
      setCount(data.count || 0)
      setPage(nextPage)
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load(1, {
      city: params.get('city') || '',
      check_in: params.get('check_in') || '',
      check_out: params.get('check_out') || '',
      guests: params.get('guests') || '1',
    })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [params.toString()])

  function onSubmit(event) {
    event.preventDefault()
    const next = new URLSearchParams()
    Object.entries(filters).forEach(([key, value]) => {
      if (value) next.set(key, value)
    })
    setParams(next)
  }

  return (
    <section>
      <h1>Search homes</h1>
      <form className="search-bar" onSubmit={onSubmit}>
        <label>
          City
          <input value={filters.city} onChange={(e) => update('city', e.target.value)} />
        </label>
        <label>
          Check in
          <input
            type="date"
            value={filters.check_in}
            onChange={(e) => update('check_in', e.target.value)}
          />
        </label>
        <label>
          Check out
          <input
            type="date"
            value={filters.check_out}
            onChange={(e) => update('check_out', e.target.value)}
          />
        </label>
        <label>
          Guests
          <input
            type="number"
            min="1"
            value={filters.guests}
            onChange={(e) => update('guests', e.target.value)}
          />
        </label>
        <button className="btn" type="submit">
          Filter
        </button>
      </form>
      <ErrorBanner message={error} />
      {loading ? (
        <Loading />
      ) : results.length === 0 ? (
        <Empty>No listings match those filters.</Empty>
      ) : (
        <>
          <p className="muted">{count} homes</p>
          <div className="grid">
            {results.map((listing) => (
              <Link key={listing.id} to={`/listings/${listing.id}`} className="card listing-card">
                <h2>{listing.title}</h2>
                <p>
                  {listing.city} · {listing.address_area}
                </p>
                <p>Up to {listing.max_guests} guests · Hosted by {listing.host_name}</p>
              </Link>
            ))}
          </div>
          <div className="pager">
            <button className="btn secondary" disabled={page <= 1} onClick={() => load(page - 1)}>
              Previous
            </button>
            <button
              className="btn secondary"
              disabled={page * 12 >= count}
              onClick={() => load(page + 1)}
            >
              Next
            </button>
          </div>
        </>
      )}
    </section>
  )
}
