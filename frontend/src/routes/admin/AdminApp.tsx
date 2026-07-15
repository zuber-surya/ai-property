/**
 * The admin CRM, mounted under /admin/* and reached only through App.tsx's lazy
 * boundary. NOT tenant-branded (ADR-0010) — carries the PropVista brand.
 *
 * Its own nested <Routes> live here so the admin route tree stays inside this
 * lazy chunk.
 */
import { Routes, Route } from 'react-router-dom';

function AdminDashboard() {
  return (
    <main className="min-h-screen p-10">
      <h1 className="text-headline-lg text-on-surface">PropVista Admin</h1>
      <p className="mt-3 text-body-md text-on-surface-variant">
        Admin portal. Lazy-loaded chunk · Sprint 0.
      </p>
      <div className="mt-6 flex gap-2">
        <span className="chip chip-status-published inline-block">Published</span>
        <span className="chip chip-stage-contacted inline-block">Contacted</span>
        <span className="chip chip-stage-new inline-block">New</span>
      </div>
    </main>
  );
}

export default function AdminApp() {
  return (
    <Routes>
      <Route index element={<AdminDashboard />} />
      <Route path="dashboard" element={<AdminDashboard />} />
    </Routes>
  );
}
