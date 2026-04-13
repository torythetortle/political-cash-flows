<script lang="ts">
	import { onMount } from 'svelte';
	import { selectedVendor, clusterVendors } from '$lib/stores/explorerStore';
	import type { VendorFeatureCollection, VendorFeature } from '$lib/data/types';
	import { COLORS } from '$lib/utils/colors';

	interface Props {
		vendors: VendorFeatureCollection;
		filteredVendors: VendorFeature[];
		onVisibleChange?: (vendors: VendorFeature[]) => void;
	}

	let { vendors, filteredVendors, onVisibleChange }: Props = $props();

	let mapContainer: HTMLDivElement;
	let map: any = $state(null);
	let mapLoaded = $state(false);
	let mapError = $state('');

	export function flyTo(center: [number, number], zoom: number) {
		if (map && mapLoaded) {
			map.flyTo({ center, zoom, duration: 1500, essential: true });
		}
	}

	export function flyToVendor(vendor: VendorFeature) {
		if (map && mapLoaded) {
			map.flyTo({
				center: vendor.geometry.coordinates,
				zoom: 14,
				duration: 1200,
				essential: true,
			});
		}
	}

	async function addStateBoundaries() {
		const topoRes = await fetch('https://cdn.jsdelivr.net/npm/us-atlas@3/states-10m.json');
		const us = await topoRes.json();
		const topojson = await import('topojson-client');
		const states = topojson.feature(us, us.objects.states);

		map.addSource('states', {
			type: 'geojson',
			data: states,
		});

		map.addLayer({
			id: 'state-borders',
			type: 'line',
			source: 'states',
			paint: {
				'line-color': '#999999',
				'line-width': 0.8,
				'line-opacity': 0.5,
			},
		});

		map.addLayer({
			id: 'state-fills',
			type: 'fill',
			source: 'states',
			paint: {
				'fill-color': 'transparent',
				'fill-outline-color': 'transparent',
			},
		});
	}

	function addLayers() {
		map.addSource('vendors', {
			type: 'geojson',
			data: { type: 'FeatureCollection', features: filteredVendors },
			cluster: true,
			clusterMaxZoom: 12,
			clusterRadius: 45,
		});

		map.addLayer({
			id: 'clusters',
			type: 'circle',
			source: 'vendors',
			filter: ['has', 'point_count'],
			paint: {
				'circle-color': COLORS.cluster,
				'circle-opacity': 0.7,
				'circle-radius': ['step', ['get', 'point_count'], 14, 10, 20, 30, 28, 50, 36],
				'circle-stroke-width': 1,
				'circle-stroke-color': COLORS.bg,
			},
		});

		map.addLayer({
			id: 'cluster-count',
			type: 'symbol',
			source: 'vendors',
			filter: ['has', 'point_count'],
			layout: {
				'text-field': ['get', 'point_count_abbreviated'],
				'text-size': 11,
			},
			paint: { 'text-color': COLORS.bg },
		});

		map.addLayer({
			id: 'vendor-points',
			type: 'circle',
			source: 'vendors',
			filter: ['!', ['has', 'point_count']],
			paint: {
				'circle-radius': [
					'interpolate', ['linear'], ['get', 'total_spend'],
					1000, 3, 100000, 6, 1000000, 12, 10000000, 20,
				],
				'circle-color': [
					'match', ['get', 'dominant_party'],
					'DEM', COLORS.dem, 'REP', COLORS.rep, COLORS.muted,
				],
				'circle-opacity': 0.8,
				'circle-stroke-width': 1,
				'circle-stroke-color': COLORS.bg,
			},
		});

		map.on('click', 'vendor-points', (e: any) => {
			if (!e.features?.length) return;
			const feat = e.features[0];
			const props = { ...feat.properties };
			if (typeof props.cycles === 'string') {
				try { props.cycles = JSON.parse(props.cycles); } catch { props.cycles = [2024]; }
			}
			clusterVendors.set([]);
			selectedVendor.set({
				type: 'Feature',
				geometry: feat.geometry,
				properties: props,
			} as VendorFeature);
		});

		map.on('click', 'clusters', async (e: any) => {
			const features = map.queryRenderedFeatures(e.point, { layers: ['clusters'] });
			if (!features.length) return;
			const clusterId = features[0].properties.cluster_id;
			const pointCount = features[0].properties.point_count;
			const source = map.getSource('vendors') as any;

			try {
				const leaves = await source.getClusterLeaves(clusterId, Math.min(pointCount, 200), 0);
				if (!leaves?.length) return;
				const parsed: VendorFeature[] = leaves.map((f: any) => {
					const p = { ...f.properties };
					if (typeof p.cycles === 'string') {
						try { p.cycles = JSON.parse(p.cycles); } catch { p.cycles = [2024]; }
					}
					return { type: 'Feature', geometry: f.geometry, properties: p } as VendorFeature;
				});
				parsed.sort((a, b) => b.properties.total_spend - a.properties.total_spend);
				selectedVendor.set(null);
				clusterVendors.set(parsed);
			} catch (err) {
				console.error('Cluster leaves error:', err);
			}
		});

		map.on('mouseenter', 'vendor-points', () => { map.getCanvas().style.cursor = 'pointer'; });
		map.on('mouseleave', 'vendor-points', () => { map.getCanvas().style.cursor = ''; });
		map.on('mouseenter', 'clusters', () => { map.getCanvas().style.cursor = 'pointer'; });
		map.on('mouseleave', 'clusters', () => { map.getCanvas().style.cursor = ''; });

		// Emit visible vendors on map move
		function emitVisible() {
			if (!onVisibleChange) return;
			const bounds = map.getBounds();
			const visible = filteredVendors.filter((f) => {
				const [lng, lat] = f.geometry.coordinates;
				return bounds.contains([lng, lat]);
			});
			onVisibleChange(visible);
		}

		map.on('moveend', emitVisible);
		// Initial emit after load
		setTimeout(emitVisible, 100);

		mapLoaded = true;
	}

	onMount(() => {
		let destroyed = false;
		let mapInstance: any = null;

		(async () => {
			try {
				const maplibreModule = await import('maplibre-gl');
				const ml = maplibreModule.default ?? maplibreModule;
				if (destroyed) return;

				mapInstance = new ml.Map({
					container: mapContainer,
					style: `https://basemaps.cartocdn.com/gl/positron-nolabels-gl-style/style.json`,
					center: [-98.58, 39.83],
					zoom: 3.8,
					minZoom: 2,
					maxZoom: 18,
					attributionControl: false,
				});

				map = mapInstance;

				map.on('load', async () => {
					if (destroyed) return;
					await addStateBoundaries();
					addLayers();
				});

				map.on('error', (e: any) => {
					console.error('Map error:', e);
				});
			} catch (e: any) {
				mapError = e.message ?? 'Failed to load map';
				console.error('Map init error:', e);
			}
		})();

		return () => {
			destroyed = true;
			mapInstance?.remove();
		};
	});

	// Update map data when filters change
	$effect(() => {
		if (map && mapLoaded) {
			const source = map.getSource('vendors');
			if (source) {
				source.setData({ type: 'FeatureCollection', features: filteredVendors });
			}
		}
	});
</script>

<div class="explorer-map" role="application" aria-label="Interactive map of political vendor locations. Use mouse or touch to pan and zoom.">
	<div class="map-container" bind:this={mapContainer}></div>
	{#if !mapLoaded}
		<div class="map-loading" class:behind={map}>
			{#if mapError}
				<span>{mapError}</span>
			{:else}
				<span class="spinner"></span>
				Loading map...
			{/if}
		</div>
	{/if}
</div>

<style>
	.explorer-map {
		width: 100%;
		height: 100%;
		position: relative;
	}

	.map-container {
		position: absolute;
		inset: 0;
	}

	.map-container :global(.maplibregl-ctrl-bottom-left),
	.map-container :global(.maplibregl-ctrl-bottom-right) {
		display: none;
	}

	.map-loading {
		position: absolute;
		inset: 0;
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 10px;
		color: var(--color-muted);
		font-family: var(--font-mono);
		font-size: var(--font-size-sm);
		background: var(--color-surface);
		z-index: 2;
		pointer-events: none;
	}

	.map-loading.behind {
		background: transparent;
	}

	.spinner {
		width: 16px;
		height: 16px;
		border: 2px solid var(--color-border);
		border-top-color: var(--color-accent);
		border-radius: 50%;
		animation: spin 0.8s linear infinite;
	}

	@keyframes spin { to { transform: rotate(360deg); } }
</style>
