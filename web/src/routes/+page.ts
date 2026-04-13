import type { PageLoad } from './$types';
import type { VendorFeatureCollection, StateSpendMap, TopVendor, VendorCycleData, VendorDetailsMap } from '$lib/data/types';
import { base } from '$app/paths';

export const load: PageLoad = async ({ fetch }) => {
	const [vendorsRes, stateSpendRes, topVendorsRes, vendorCyclesRes] = await Promise.all([
		fetch(`${base}/data/vendors_map.geojson`),
		fetch(`${base}/data/state_spend.json`),
		fetch(`${base}/data/top_vendors.json`),
		fetch(`${base}/data/vendor_cycles.json`),
	]);

	const vendors: VendorFeatureCollection = await vendorsRes.json();
	const stateSpend: StateSpendMap = await stateSpendRes.json();
	const topVendors: TopVendor[] = await topVendorsRes.json();
	const vendorCycles: VendorCycleData[] = await vendorCyclesRes.json();

	let vendorDetails: VendorDetailsMap = {};
	try {
		const detailsRes = await fetch(`${base}/data/vendor_details.json`);
		if (detailsRes.ok) {
			vendorDetails = await detailsRes.json();
		}
	} catch {
		// vendor_details.json not available yet
	}

	const totalSpend = Object.values(stateSpend).reduce((sum, s) => sum + s.total_spend, 0);
	const phillySpend = vendors.features
		.filter((f) => f.properties.city.toUpperCase() === 'PHILADELPHIA')
		.reduce((sum, f) => sum + f.properties.total_spend, 0);

	return {
		vendors,
		stateSpend,
		topVendors,
		vendorCycles,
		vendorDetails,
		totalSpend,
		phillySpend,
	};
};
