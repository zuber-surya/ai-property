import { Routes, Route, Link } from 'react-router-dom';
import Listings from './Listings';

function Home() {
  return (
    <main className="min-h-screen p-10">
      <h1 className="text-display-lg text-on-surface">PropVista</h1>
      <p className="mt-3 text-body-lg text-on-surface-variant">
        One app, route-based. Public site + customer portal.
      </p>
      <div className="mt-6 flex gap-4">
        <Link to="/search" className="focus-ring text-primary underline">
          Browse listings →
        </Link>
        <Link to="/admin/properties" className="focus-ring text-on-surface-variant underline">
          Admin portal
        </Link>
      </div>
    </main>
  );
}

export default function PublicApp() {
  return (
    <Routes>
      <Route index element={<Home />} />
      <Route path="search" element={<Listings />} />
    </Routes>
  );
}
