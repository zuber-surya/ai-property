/**
 * Admin portal shell.
 *
 * NOT tenant-branded (ADR-0010) — it carries the PropVista brand.
 * Colours come from token classes only; a hex literal here fails check_drift.
 */
export default function App() {
  return (
    <main className="min-h-screen p-10">
      <h1 className="text-headline-lg text-on-surface">PropVista Admin</h1>
      <p className="mt-3 text-body-md text-on-surface-variant">
        Scaffold is running. Sprint 0.
      </p>
      <span className="chip chip-success mt-6 inline-block">Published</span>
      <span className="chip chip-info mt-6 ml-2 inline-block">Contacted</span>
      <span className="chip chip-neutral mt-6 ml-2 inline-block">New</span>
    </main>
  );
}
