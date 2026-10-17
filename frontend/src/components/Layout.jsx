import { Link, NavLink, Outlet } from 'react-router-dom'
import { useAuth } from '../AuthContext'

export default function Layout() {
  const { user, profile, logout } = useAuth()

  return (
    <div className="app">
      <header className="nav">
        <Link to="/" className="brand">
          GharSwap
        </Link>
        <nav>
          <NavLink to="/search">Search</NavLink>
          {user ? (
            <>
              <NavLink to="/listings/mine">My listings</NavLink>
              <NavLink to="/requests">Requests</NavLink>
              <NavLink to="/credits">Credits</NavLink>
              <NavLink to="/profile">{profile?.display_name || 'Profile'}</NavLink>
              <button type="button" className="linkish" onClick={logout}>
                Log out
              </button>
            </>
          ) : (
            <>
              <NavLink to="/login">Log in</NavLink>
              <NavLink to="/register" className="btn btn-small">
                Join
              </NavLink>
            </>
          )}
        </nav>
      </header>
      <main className="main">
        <Outlet />
      </main>
      <footer className="footer">
        Reciprocal home stays. Pay with guest-night credits, not cash.
      </footer>
    </div>
  )
}
