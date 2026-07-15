/**
 * Public surface landing. Anonymous-first (ADR-0015). Not tenant-branded in the
 * MVP — one fixed palette from DESIGN.md via token classes.
 */
export default function PublicHome() {
  return (
    <main className="min-h-screen p-10">
      <h1 className="text-display-lg text-on-surface">PropVista</h1>
      <p className="mt-3 text-body-lg text-on-surface-variant">
        Public site. Scaffold running · one app, route-based.
      </p>
      <a href="/admin" className="focus-ring mt-6 inline-block text-primary underline">
        Go to the admin portal →
      </a>
    </main>
  );
}
