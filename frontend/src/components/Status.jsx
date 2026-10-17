export function Loading({ label = 'Loading…' }) {
  return <p className="status">{label}</p>
}

export function ErrorBanner({ message }) {
  if (!message) return null
  return <p className="status error">{message}</p>
}

export function Empty({ children }) {
  return <p className="status muted">{children}</p>
}
