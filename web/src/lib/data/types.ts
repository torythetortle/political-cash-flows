export interface VendorProperties {
	vendor_id: string;
	canonical_name: string;
	total_spend: number;
	dem_spend: number;
	rep_spend: number;
	dominant_party: 'DEM' | 'REP';
	cycles: number[];
	category: string;
	city: string;
	state: string;
}

export interface VendorFeature {
	type: 'Feature';
	geometry: {
		type: 'Point';
		coordinates: [number, number]; // [lng, lat]
	};
	properties: VendorProperties;
}

export interface VendorFeatureCollection {
	type: 'FeatureCollection';
	features: VendorFeature[];
}

export interface StateSpendings {
	dem_spend: number;
	rep_spend: number;
	total_spend: number;
	vendor_count: number;
}

export type StateSpendMap = Record<string, StateSpendings>;

export interface TopVendor {
	vendor_id: string;
	canonical_name: string;
	total_spend: number;
	dem_pct: number;
	rep_pct: number;
	cycles: number[];
	category: string;
	city: string;
	state: string;
}

export interface VendorCycleData {
	vendor_id: string;
	canonical_name: string;
	dominant_party: 'DEM' | 'REP';
	category: string;
	cycles: Record<string, number>;
}

export interface VendorDetail {
	timeline: Record<string, number>; // "2024-01" → dollars
	purpose: Record<string, number>; // "Media & Advertising" → dollars
	committees: Array<{
		name: string;
		party: string;
		spend: number;
	}>;
	candidates: Array<{
		id: string;
		name: string;
		office: string;
		state: string;
		spend: number;
	}>;
}

export type VendorDetailsMap = Record<string, VendorDetail>;

export type StoryStep =
	| 'intro'
	| 'national-spend'
	| 'swing-states'
	| 'philadelphia-intro'
	| 'zoom-philadelphia'
	| 'vendor-clusters'
	| 'explore'
	| 'concentration'
	| 'repeat-players'
	| 'methodology';
