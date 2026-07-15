/**
 * Admin → Properties. The first real feature: list, add, publish.
 * Uses token classes only (a hex here fails check_drift). Renders the states
 * Stitch never draws: loading, error, and — most importantly — empty.
 */
import { useEffect, useState } from 'react';
import {
  listAdminProperties,
  createProperty,
  publishProperty,
  type Property,
} from '../../api/properties';
import { ApiError } from '../../api/client';

const inr = (v: string | null) =>
  v == null ? '—' : `₹${Number(v).toLocaleString('en-IN')}`;

const statusChip: Record<string, string> = {
  draft: 'chip-status-draft',
  published: 'chip-status-published',
  pending_approval: 'chip-status-pending',
  sold: 'chip-status-sold',
};

export default function Properties() {
  const [rows, setRows] = useState<Property[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [title, setTitle] = useState('');
  const [locality, setLocality] = useState('');
  const [busy, setBusy] = useState(false);

  const load = () =>
    listAdminProperties()
      .then((p) => setRows(p.items))
      .catch((e: ApiError) => setError(e.message));

  useEffect(() => {
    void load();
  }, []);

  async function add(e: React.FormEvent) {
    e.preventDefault();
    if (!title.trim()) return;
    setBusy(true);
    setError(null);
    try {
      await createProperty({
        title: title.trim(),
        property_type: 'apartment',
        listing_type: 'buy',
        locality: locality.trim() || undefined,
      });
      setTitle('');
      setLocality('');
      await load();
    } catch (e) {
      setError((e as ApiError).message);
    } finally {
      setBusy(false);
    }
  }

  async function publish(id: string) {
    setError(null);
    try {
      await publishProperty(id);
      await load();
    } catch (e) {
      setError((e as ApiError).message);
    }
  }

  return (
    <main className="min-h-screen p-10">
      <h1 className="text-headline-lg text-on-surface">Properties</h1>

      <form onSubmit={add} className="mt-6 flex flex-wrap items-end gap-3">
        <label className="flex flex-col text-label-md text-on-surface-variant">
          Title
          <input
            className="focus-ring mt-1 rounded-md bg-surface-container-low px-3 py-2 text-body-md text-on-surface"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="e.g. Sunview 3BHK"
          />
        </label>
        <label className="flex flex-col text-label-md text-on-surface-variant">
          Locality
          <input
            className="focus-ring mt-1 rounded-md bg-surface-container-low px-3 py-2 text-body-md text-on-surface"
            value={locality}
            onChange={(e) => setLocality(e.target.value)}
            placeholder="Whitefield"
          />
        </label>
        <button
          type="submit"
          disabled={busy}
          className="focus-ring rounded-md bg-primary px-4 py-2 text-label-md text-on-primary disabled:opacity-40"
        >
          {busy ? 'Adding…' : 'Add property'}
        </button>
      </form>

      {error && (
        <p className="mt-4 rounded-md bg-error-container px-3 py-2 text-body-md text-on-error-container">
          {error}
        </p>
      )}

      <div className="mt-8">
        {rows === null ? (
          <p className="text-on-surface-variant">Loading…</p>
        ) : rows.length === 0 ? (
          <div className="rounded-xl border border-outline-variant bg-surface-container-lowest p-8 text-center">
            <p className="text-body-lg text-on-surface">No properties yet.</p>
            <p className="mt-1 text-body-md text-on-surface-variant">
              Add your first listing above — it starts as a draft.
            </p>
          </div>
        ) : (
          <table className="w-full text-left">
            <thead>
              <tr className="text-label-sm uppercase text-on-surface-variant">
                <th className="py-2">Title</th>
                <th className="py-2">Price</th>
                <th className="py-2">Locality</th>
                <th className="py-2">Status</th>
                <th className="py-2"></th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr key={r.id} className="border-t border-outline-variant">
                  <td className="py-3 text-body-md text-on-surface">{r.title}</td>
                  <td className="py-3 text-body-md text-on-surface">{inr(r.price)}</td>
                  <td className="py-3 text-body-md text-on-surface-variant">
                    {r.locality ?? '—'}
                  </td>
                  <td className="py-3">
                    <span className={`chip ${statusChip[r.status] ?? 'chip-status-draft'}`}>
                      {r.status.replace('_', ' ')}
                    </span>
                  </td>
                  <td className="py-3 text-right">
                    {r.status === 'draft' && (
                      <button
                        onClick={() => publish(r.id)}
                        className="focus-ring rounded-md border border-primary px-3 py-1 text-label-md text-primary"
                      >
                        Publish
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </main>
  );
}
