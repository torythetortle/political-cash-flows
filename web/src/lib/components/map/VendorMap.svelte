<script lang="ts">
	import { onMount } from 'svelte';
	import { mapFlyTarget, activeVendor, partyFilter } from '$lib/stores/mapStore';
	import type { VendorFeatureCollection, VendorProperties } from '$lib/data/types';
	import { COLORS } from '$lib/utils/colors';

	interface Props {
		vendors: VendorFeatureCollection;
		visible?: boolean;
		interactive?: boolean;
	}

	let { vendors, visible = true, interactive = false }: Props = $props();

	let mapContainer: HTMLDivElement;
	let map: any = $state(null);
	let mapLoaded = $state(false);

	onMount(() => {
		let destroyed = false;

		(async () => {
		const maplibreModule = await import('maplibre-gl');
		const maplibregl = maplibreModule.default ?? maplibreModule;
		if (destroyed) return;

		map = new maplibregl.Map({
			container: mapContainer,
			style: 'https://basemaps.cartocdn.com/gl/positron-nolabels-gl-style/style.json',
			center: [-98.58, 39.83],
			zoom: 3.8,
			minZoom: 2,
			maxZoom: 18,
			attributionControl: false,
		});

		map.on('load', () => {
			map.addSource('vendors', {
				type: 'geojson',
				data: vendors,
				cluster: true,
				clusterMaxZoom: 11,
				clusterRadius: 40,
			});

			// Cluster circles
			map.addLayer({
				id: 'clusters',
				type: 'circle',
				source: 'vendors',
				filter: ['has', 'point_count'],
				paint: {
					'circle-color': COLORS.accent,
					'circle-opacity': 0.7,
					'circle-radius': [
						'step',
						['get', 'point_count'],
						14, 10,
						20, 30,
						28, 50,
						36,
					],
					'circle-stroke-width': 1,
					'circle-stroke-color': COLORS.bg,
				},
			});

			// Cluster count labels
			map.addLayer({
				id: 'cluster-count',
				type: 'symbol',
				source: 'vendors',
				filter: ['has', 'point_count'],
				layout: {
					'text-field': '{point_count_abbreviated}',
					'text-size': 11,
					'text-font': ['Open Sans Semibold'],
				},
				paint: {
					'text-color': COLORS.bg,
				},
			});

			// Individual vendor circles
			map.addLayer({
				id: 'vendor-points',
				type: 'circle',
				source: 'vendors',
				filter: ['!', ['has', 'point_count']],
				paint: {
					'circle-radius': [
						'interpolate',
						['linear'],
						['get', 'total_spend'],
						10000, 4,
						500000, 8,
						2000000, 14,
						10000000, 22,
					],
					'circle-color': [
						'match',
						['get', 'dominant_party'],
						'DEM', COLORS.dem,
						'REP', COLORS.rep,
						COLORS.muted,
					],
					'circle-opacity': 0.8,
					'circle-stroke-width': 1,
					'circle-stroke-color': COLORS.bg,
				},
			});

			// Click handler for vendor points
			map.on('click', 'vendor-points', (e: any) => {
				if (!interactive || !e.features?.length) return;
				const props = e.features[0].properties;
				// Parse cycles back from string if needed
				if (typeof props.cycles === 'string') {
					props.cycles = JSON.parse(props.cycles);
				}
				activeVendor.set(props as VendorProperties);
			});

			// Click clusters to zoom in
			map.on('click', 'clusters', async (e: any) => {
				const features = map.queryRenderedFeatures(e.point, { layers: ['clusters'] });
				if (!features.length) return;
				const clusterId = features[0].properties.cluster_id;
				try {
					const zoom = await (map.getSource('vendors') as any).getClusterExpansionZoom(clusterId);
					map.easeTo({ center: features[0].geometry.coordinates, zoom });
				} catch {}
			});

			// Cursor changes
			map.on('mouseenter', 'vendor-points', () => {
				map.getCanvas().style.cursor = 'pointer';
			});
			map.on('mouseleave', 'vendor-points', () => {
				map.getCanvas().style.cursor = '';
			});
			map.on('mouseenter', 'clusters', () => {
				map.getCanvas().style.cursor = 'pointer';
			});
			map.on('mouseleave', 'clusters', () => {
				map.getCanvas().style.cursor = '';
			});

			mapLoaded = true;
		});

		})();

		return () => {
			destroyed = true;
			map?.remove();
		};
	});

	// React to fly targets from scroll
	$effect(() => {
		const target = $mapFlyTarget;
		if (map && mapLoaded && target) {
			map.flyTo({
				center: target.center,
				zoom: target.zoom,
				duration: 2000,
				essential: true,
			});
		}
	});

	// React to party filter changes
	$effect(() => {
		const filter = $partyFilter;
		if (map && mapLoaded) {
			if (filter === 'ALL') {
				map.setFilter('vendor-points', ['!', ['has', 'point_count']]);
			} else {
				map.setFilter('vendor-points', [
					'all',
					['!', ['has', 'point_count']],
					['==', ['get', 'dominant_party'], filter],
				]);
			}
		}
	});
</script>

<div class="vendor-map" class:visible>
	<div class="map-container" bind:this={mapContainer}></div>
	{#if !mapLoaded}
		<div class="map-loading">
			<span class="spinner"></span>
			Loading map...
		</div>
	{/if}
</div>

<style>
	.vendor-map {
		width: 100%;
		height: 100%;
		position: relative;
		opacity: 0;
		transition: opacity 0.6s ease;
	}

	.vendor-map.visible {
		opacity: 1;
	}

	.map-container {
		width: 100%;
		height: 100%;
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
	}

	.spinner {
		width: 16px;
		height: 16px;
		border: 2px solid var(--color-border);
		border-top-color: var(--color-accent);
		border-radius: 50%;
		animation: spin 0.8s linear infinite;
	}

	@keyframes spin {
		to { transform: rotate(360deg); }
	}
</style>
