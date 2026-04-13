<script lang="ts">
	import type { VendorFeatureCollection, VendorFeature, StateSpendMap, VendorDetailsMap } from '$lib/data/types';
	import {
		searchQuery,
		selectedParty,
		selectedState,
		spendRange,
		selectedVendor,
		clusterVendors,
	} from '$lib/stores/explorerStore';
	import SearchFilter from './SearchFilter.svelte';
	import VendorDetail from './VendorDetail.svelte';
	import VendorList from './VendorList.svelte';
	import ExplorerMap from './ExplorerMap.svelte';
	import DataTable from './DataTable.svelte';

	interface Props {
		vendors: VendorFeatureCollection;
		stateSpend: StateSpendMap;
		vendorDetails: VendorDetailsMap;
	}

	let { vendors, stateSpend, vendorDetails }: Props = $props();

	let explorerMap: ExplorerMap;
	let viewMode = $state<'map' | 'table'>('map');

	// Filter vendors reactively
	let filteredVendors = $derived.by(() => {
		let filtered = vendors.features;

		const query = $searchQuery.toLowerCase();
		if (query) {
			filtered = filtered.filter((f) =>
				f.properties.canonical_name.toLowerCase().includes(query)
			);
		}

		const party = $selectedParty;
		if (party !== 'ALL') {
			filtered = filtered.filter((f) => f.properties.dominant_party === party);
		}

		const state = $selectedState;
		if (state !== 'ALL') {
			filtered = filtered.filter((f) => f.properties.state === state);
		}

		const [min] = $spendRange;
		if (min > 0) {
			filtered = filtered.filter((f) => f.properties.total_spend >= min);
		}

		return filtered;
	});

	let visibleVendors = $state<VendorFeature[]>([]);
	let hasSelection = $derived($selectedVendor !== null || $clusterVendors.length > 0);

	function handleFlyToVendor(vendor: VendorFeature) {
		explorerMap?.flyToVendor(vendor);
	}

	function handleVisibleChange(vendors: VendorFeature[]) {
		visibleVendors = vendors;
	}
</script>

<section class="explorer" id="explore" aria-label="Interactive data explorer">
	<div class="explorer-header">
		<div class="header-row">
			<div>
				<h2>Explore the Data</h2>
				<p>Search, filter, and click into the vendor ecosystem behind American elections.</p>
			</div>
			<div class="view-toggle">
				<button class:active={viewMode === 'map'} onclick={() => viewMode = 'map'}>Map</button>
				<button class:active={viewMode === 'table'} onclick={() => viewMode = 'table'}>Table</button>
			</div>
		</div>
	</div>

	<!-- Top bar: filters + city selector -->
	<div class="explorer-toolbar">
		<div class="toolbar-inner">
			<SearchFilter
				{stateSpend}
				vendorCount={vendors.features.length}
				filteredCount={filteredVendors.length}
			/>
			</div>
	</div>

	<!-- Main area: map/table + results panel -->
	<div class="explorer-body">
		<div class="explorer-main">
			{#if viewMode === 'map'}
				<ExplorerMap
					bind:this={explorerMap}
					{vendors}
					{filteredVendors}
					onVisibleChange={handleVisibleChange}
				/>
			{:else}
				<DataTable vendors={filteredVendors} />
			{/if}
		</div>

		<aside class="results-panel">
			{#if hasSelection}
				<div class="results-detail full">
					<VendorDetail {vendorDetails} />
				</div>
			{:else}
				<div class="results-list">
					<VendorList
						vendors={visibleVendors.length > 0 ? visibleVendors : filteredVendors}
						onFlyToVendor={handleFlyToVendor}
					/>
				</div>
			{/if}
		</aside>
	</div>
</section>

<style>
	.explorer {
		border-top: 1px solid var(--color-border);
		background: var(--color-bg);
	}

	.explorer-header {
		padding: var(--space-3xl) var(--space-xl) var(--space-lg);
		max-width: var(--max-width);
		margin: 0 auto;
	}

	.header-row {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		gap: var(--space-md);
	}

	.explorer-header h2 {
		font-size: var(--font-size-3xl);
		margin-bottom: var(--space-xs);
	}

	.explorer-header p {
		font-size: var(--font-size-base);
		color: var(--color-text-secondary);
	}

	.view-toggle {
		display: flex;
		border: 1px solid var(--color-border);
		border-radius: var(--radius-sm);
		overflow: hidden;
		flex-shrink: 0;
	}

	.view-toggle button {
		padding: 6px 16px;
		border: none;
		background: transparent;
		color: var(--color-text-secondary);
		font-family: var(--font-mono);
		font-size: var(--font-size-xs);
		font-weight: 500;
		cursor: pointer;
		transition: all var(--transition-fast);
	}

	.view-toggle button:first-child {
		border-right: 1px solid var(--color-border);
	}

	.view-toggle button.active {
		background: var(--color-accent);
		color: var(--color-bg);
	}

	/* Toolbar: filters across the top */
	.explorer-toolbar {
		border-top: 1px solid var(--color-border);
		border-bottom: 1px solid var(--color-border);
		background: var(--color-surface);
		padding: var(--space-md) var(--space-xl);
	}

	.toolbar-inner {
		max-width: var(--max-width);
		margin: 0 auto;
		display: flex;
		align-items: flex-start;
		gap: var(--space-xl);
	}

	/* Body: map left, results right */
	.explorer-body {
		display: flex;
		height: 80vh;
		min-height: 550px;
	}

	.explorer-main {
		flex: 1;
		min-width: 0;
	}

	.results-panel {
		width: 340px;
		flex-shrink: 0;
		border-left: 1px solid var(--color-border);
		background: var(--color-surface);
		display: flex;
		flex-direction: column;
		overflow: hidden;
	}

	.results-detail {
		padding: var(--space-md) var(--space-lg);
		flex-shrink: 0;
		max-height: 45%;
		overflow-y: auto;
	}

	.results-detail.full {
		flex: 1;
		max-height: none;
	}

	.results-list {
		flex: 1;
		min-height: 0;
		padding: var(--space-md) var(--space-lg);
		display: flex;
		flex-direction: column;
	}

	@media (max-width: 1100px) {
		.results-panel {
			width: 280px;
		}
	}

	@media (max-width: 900px) {
		.explorer-header {
			padding: var(--space-2xl) var(--space-lg) var(--space-md);
		}

		.explorer-toolbar {
			padding: var(--space-md) var(--space-lg);
		}

		.toolbar-inner {
			flex-direction: column;
			gap: var(--space-md);
		}

		.explorer-body {
			flex-direction: column;
			height: auto;
		}

		.explorer-main {
			height: 50vh;
			min-height: 300px;
		}

		.results-panel {
			width: 100%;
			max-height: 50vh;
			border-left: none;
			border-top: 1px solid var(--color-border);
		}

		.results-detail {
			max-height: 35%;
		}
	}

	@media (max-width: 480px) {
		.explorer-header h2 {
			font-size: var(--font-size-2xl);
		}

		.explorer-main {
			height: 40vh;
			min-height: 250px;
		}

		.results-panel {
			max-height: 60vh;
		}
	}
</style>
