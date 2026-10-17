import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

export default function Landing() {
  const navigate = useNavigate()
  const [city, setCity] = useState('Goa')
  const [checkIn, setCheckIn] = useState('')
  const [checkOut, setCheckOut] = useState('')
  const [guests, setGuests] = useState(1)

  function onSubmit(event) {
    event.preventDefault()
    const params = new URLSearchParams({ city, guests: String(guests) })
    if (checkIn) params.set('check_in', checkIn)
    if (checkOut) params.set('check_out', checkOut)
    navigate(`/search?${params.toString()}`)
  }

  return (
    <section className="hero">
      <p className="eyebrow">Goa · Pondicherry · then anywhere</p>
      <h1>Swap homes. Spend nights, not money.</h1>
      <p className="lede">
        GharSwap is a free, reciprocal home-stay network. Host someone for two guest nights and
        you earn two credits to stay elsewhere.
      </p>
      <form className="search-bar" onSubmit={onSubmit}>
        <label>
          City
          <input value={city} onChange={(e) => setCity(e.target.value)} placeholder="Goa" />
        </label>
        <label>
          Check in
          <input type="date" value={checkIn} onChange={(e) => setCheckIn(e.target.value)} />
        </label>
        <label>
          Check out
          <input type="date" value={checkOut} onChange={(e) => setCheckOut(e.target.value)} />
        </label>
        <label>
          Guests
          <input
            type="number"
            min="1"
            value={guests}
            onChange={(e) => setGuests(e.target.value)}
          />
        </label>
        <button className="btn" type="submit">
          Find a stay
        </button>
      </form>
    </section>
  )
}
