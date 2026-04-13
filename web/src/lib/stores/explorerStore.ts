import { writable, derived } from 'svelte/store';
import type { VendorFeature, VendorFeatureCollection, TopVendor } from '$lib/data/types';

// Filters
export const searchQuery = writable('');
export const selectedParty = writable<'ALL' | 'DEM' | 'REP'>('ALL');
export const selectedCategory = writable<string>('ALL');
export const selectedState = writable<string>('ALL');
export const spendRange = writable<[number, number]>([0, Infinity]);

// Active selections
export const selectedVendor = writable<VendorFeature | null>(null);
export const clusterVendors = writable<VendorFeature[]>([]);
export const selectedCity = writable<string | null>(null);

// City presets for the selector
export const CITY_PRESETS = [
	{ name: 'National View', center: [-98.58, 39.83] as [number, number], zoom: 3.8 },
	{ name: 'Washington DC', center: [-77.0369, 38.9072] as [number, number], zoom: 11 },
	{ name: 'Philadelphia', center: [-75.1652, 39.9526] as [number, number], zoom: 12 },
	{ name: 'Atlanta', center: [-84.3880, 33.7490] as [number, number], zoom: 11.5 },
	{ name: 'Phoenix', center: [-112.0740, 33.4484] as [number, number], zoom: 11 },
	{ name: 'Detroit', center: [-83.0458, 42.3314] as [number, number], zoom: 11.5 },
	{ name: 'Las Vegas', center: [-115.1398, 36.1699] as [number, number], zoom: 11 },
	{ name: 'Milwaukee', center: [-87.9065, 43.0389] as [number, number], zoom: 12 },
	{ name: 'Miami', center: [-80.1918, 25.7617] as [number, number], zoom: 11.5 },
	{ name: 'New York', center: [-74.0060, 40.7128] as [number, number], zoom: 11 },
	{ name: 'Chicago', center: [-87.6298, 41.8781] as [number, number], zoom: 11 },
	{ name: 'Los Angeles', center: [-118.2437, 34.0522] as [number, number], zoom: 10.5 },
	{ name: 'Houston', center: [-95.3698, 29.7604] as [number, number], zoom: 11 },
] as const;

// Vendor categories extracted from data
export const CATEGORIES = [
	'ALL',
	'MEDIA_BUYING',
	'DIRECT_MAIL',
	'CONSULTING',
	'DATA_ANALYTICS',
	'DIGITAL',
	'FIELD_OPERATIONS',
	'LEGAL',
	'PRINTING',
	'EVENT_PRODUCTION',
	'TV_STATIONS',
] as const;
