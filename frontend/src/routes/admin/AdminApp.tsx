/**
 * The admin CRM under /admin/*, reached only through App.tsx's lazy boundary,
 * so the whole tree stays in a separate chunk (ADR-0020). NOT tenant-branded.
 */
import { Routes, Route, Link } from 'react-router-dom';
import Properties from './Properties';

function Dashboard() {
  return (
    <main className="min-h-screen p-10">
      <h1 className="text-headline-lg text-on-surface">PropVista Admin</h1>
      <p className="mt-3 text-body-md text-on-surface-variant">Lazy-loaded chunk.</p>
      <Link to="/admin/properties" className="focus-ring mt-6 inline-block text-primary underline">
        Manage properties →
      </Link>
    </main>
  );
}

export default function AdminApp() {
  return (
    <Routes>
      <Route index element={<Dashboard />} />
      <Route path="dashboard" element={<Dashboard />} />
      <Route path="properties" element={<Properties />} />
    </Routes>
  );
}
