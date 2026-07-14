/**
 * Public site shell (public pages + the customer portal).
 *
 * Not tenant-branded in the MVP (ADR-0010) — one fixed palette for every tenant.
 */
export default function App() {
  return (
    <main className="min-h-screen p-10">
      <h1 className="text-display-lg text-on-surface">PropVista</h1>
      <p className="mt-3 text-body-lg text-on-surface-variant">
        Scaffold is running. Sprint 0.
      </p>
    </main>
  );
}
