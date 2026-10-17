import { Navigate, Route, Routes } from 'react-router-dom'
import Layout from './components/Layout'
import { LoginPage, RegisterPage } from './pages/AuthPages'
import CreditsPage from './pages/CreditsPage'
import Landing from './pages/Landing'
import ListingDetailPage from './pages/ListingDetailPage'
import { ListingFormPage, MyListingsPage } from './pages/MyListingsPage'
import ProfilePage from './pages/ProfilePage'
import PublicProfilePage from './pages/PublicProfilePage'
import RequestsPage from './pages/RequestsPage'
import SearchPage from './pages/SearchPage'

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Landing />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/profile" element={<ProfilePage />} />
        <Route path="/search" element={<SearchPage />} />
        <Route path="/listings/mine" element={<MyListingsPage />} />
        <Route path="/listings/new" element={<ListingFormPage />} />
        <Route path="/listings/:id" element={<ListingDetailPage />} />
        <Route path="/listings/:id/edit" element={<ListingFormPage />} />
        <Route path="/requests" element={<RequestsPage />} />
        <Route path="/credits" element={<CreditsPage />} />
        <Route path="/users/:userId" element={<PublicProfilePage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  )
}
