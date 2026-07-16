/**
 * Public listings — the buyer's side. Shows PUBLISHED properties only (the API
 * enforces that; drafts never reach here). The other half of "an admin
 * publishes, a buyer sees it".
 */
import { useEffect, useState } from 'react';
import { browseProperties, type Property } from '../../api/properties';

const inr = (v: string | null) =>
  v == null ? 'Price on request' : `₹${Number(v).toLocaleString('en-IN')}`;

export default function Listings() {
  const [rows, setRows] = useState<Property[] | null>(null);

  useEffect(() => {
    browseProperties()
      .then((p) => setRows(p.items))
      .catch(() => setRows([]));
  }, []);

  return (
    <main className="min-h-screen p-10">
      <h1 className="text-display-lg text-on-surface">Find your home</h1>
      <p className="mt-2 text-body-lg text-on-surface-variant">Published listings.</p>

      {rows === null ? (
        <p className="mt-8 text-on-surface-variant">Loading…</p>
      ) : rows.length === 0 ? (
        <div className="mt-8 rounded-xl border border-outline-variant bg-surface-container-lowest p-8 text-center">
          <p className="text-body-lg text-on-surface">No listings yet.</p>
          <p className="mt-1 text-body-md text-on-surface-variant">
            Nothing has been published. Check back soon.
          </p>
        </div>
      ) : (
        <div className="mt-8 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {rows.map((r) => (
            <article
              key={r.id}
              className="rounded-xl border border-outline-variant bg-surface-container-lowest p-6 shadow-soft"
            >
              <div className="aspect-video rounded-lg bg-surface-container" />
              <h2 className="mt-4 text-headline-md text-on-surface">{inr(r.price)}</h2>
              <p className="mt-1 text-body-md text-on-surface">{r.title}</p>
              <p className="text-body-md text-on-surface-variant">{r.locality ?? ''}</p>
            </article>
          ))}
        </div>
      )}
    </main>
  );
}
