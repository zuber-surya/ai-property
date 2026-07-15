import { api } from './client';

export type Property = {
  id: string;
  title: string;
  property_type: string;
  listing_type: string;
  status: string;
  price: string | null;
  bedrooms: number | null;
  locality: string | null;
};
export type Page<T> = { items: T[]; total: number; page: number; page_size: number };

export const listAdminProperties = () => api<Page<Property>>('/admin/properties');
export const browseProperties = () => api<Page<Property>>('/properties');
export const createProperty = (body: {
  title: string;
  property_type: string;
  listing_type: string;
  price?: number;
  bedrooms?: number;
  locality?: string;
}) => api<Property>('/admin/properties', { method: 'POST', body: JSON.stringify(body) });
export const publishProperty = (id: string) =>
  api<Property>(`/admin/properties/${id}/publish`, { method: 'POST' });
