import { writable } from 'svelte/store';
import type { VendorProperties } from '$lib/data/types';

export const activeVendor = writable<VendorProperties | null>(null);
export const mapFlyTarget = writable<{ center: [number, number]; zoom: number } | null>(null);
export const partyFilter = writable<'ALL' | 'DEM' | 'REP'>('ALL');
