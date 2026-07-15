/**
 * Router root. One app, two surfaces (ADR-0020).
 *   /* (public routes)  → the public surface (eager)
 *   /admin/*            → the CRM, LAZY-LOADED as a separate chunk
 *
 * ⚠️ The lazy import is the ADR-0020 mitigation: it keeps admin JavaScript out
 * of the bundle an anonymous buyer downloads. Eager-importing an admin route
 * silently removes that. The security boundary is server-side (require_role,
 * RLS); this is bundle exposure.
 */
import { lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import PublicApp from './routes/public/PublicApp';

const AdminApp = lazy(() => import('./routes/admin/AdminApp'));

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/admin/*"
          element={
            <Suspense fallback={<div className="p-10 text-on-surface-variant">Loading…</div>}>
              <AdminApp />
            </Suspense>
          }
        />
        <Route path="/*" element={<PublicApp />} />
      </Routes>
    </BrowserRouter>
  );
}
