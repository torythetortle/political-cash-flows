<script lang="ts">
	import type { VendorFeature } from '$lib/data/types';
	import { selectedVendor } from '$lib/stores/explorerStore';
	import { formatDollars } from '$lib/utils/formatters';
	import { partyColor } from '$lib/utils/colors';

	interface Props {
		vendors: VendorFeature[];
		onFlyToVendor: (vendor: VendorFeature) => void;
	}

	let { vendors, onFlyToVendor }: Props = $props();

	let sorted = $derived(
		[...vendors]
			.sort((a, b) => b.properties.total_spend - a.properties.total_spend)
			.slice(0, 5)
	);

	function handleClick(vendor: VendorFeature) {
		selectedVendor.set(vendor);
		onFlyToVendor(vendor);
	}
</script>

<div class="vendor-list">
	<div class="list-header">
		<h3>Top in View</h3>
		<span class="count">{vendors.length.toLocaleString()} in view</span>
	</div>

	<div class="list-scroll">
		{#each sorted as vendor, i (vendor.properties.vendor_id + '-' + i)}
			{@const p = vendor.properties}
			<button
				class="vendor-row"
				class:selected={$selectedVendor?.properties.vendor_id === p.vendor_id}
				onclick={() => handleClick(vendor)}
			>
				<span
					class="party-dot"
					style:background={partyColor(p.dominant_party)}
				></span>
				<div class="vendor-info">
					<span class="vendor-name">{p.canonical_name}</span>
					<span class="vendor-loc">{p.city}, {p.state}</span>
				</div>
				<span class="vendor-spend">{formatDollars(p.total_spend)}</span>
			</button>
		{/each}

		{#if vendors.length > 5}
			<p class="more-note">{vendors.length.toLocaleString()} vendors in view</p>
		{/if}

		{#if vendors.length === 0}
			<p class="no-results">No vendors match your filters</p>
		{/if}
	</div>
</div>

<style>
	.vendor-list {
		display: flex;
		flex-direction: column;
		flex: 1;
		min-height: 0;
	}

	.list-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: var(--space-sm);
		flex-shrink: 0;
	}

	h3 {
		font-size: var(--font-size-xs);
		font-weight: 600;
		color: var(--color-text);
		text-transform: uppercase;
		letter-spacing: 0.06em;
	}

	.count {
		font-family: var(--font-mono);
		font-size: 10px;
		color: var(--color-muted);
	}

	.list-scroll {
		flex: 1;
		overflow-y: auto;
		display: flex;
		flex-direction: column;
		gap: 2px;
	}

	.vendor-row {
		display: flex;
		align-items: center;
		gap: 8px;
		padding: 8px 10px;
		border: 1px solid transparent;
		border-radius: var(--radius-sm);
		background: transparent;
		cursor: pointer;
		text-align: left;
		transition: all var(--transition-fast);
		flex-shrink: 0;
	}

	.vendor-row:hover {
		background: var(--color-surface-raised);
		border-color: var(--color-border);
	}

	.vendor-row.selected {
		background: var(--color-surface-raised);
		border-color: var(--color-accent-dim);
	}

	.party-dot {
		width: 8px;
		height: 8px;
		border-radius: 50%;
		flex-shrink: 0;
	}

	.vendor-info {
		flex: 1;
		min-width: 0;
		display: flex;
		flex-direction: column;
	}

	.vendor-name {
		font-size: var(--font-size-sm);
		color: var(--color-text);
		font-weight: 500;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}

	.vendor-loc {
		font-size: 10px;
		color: var(--color-muted);
	}

	.vendor-spend {
		font-family: var(--font-mono);
		font-size: var(--font-size-xs);
		color: var(--color-accent);
		white-space: nowrap;
		flex-shrink: 0;
	}

	.more-note, .no-results {
		text-align: center;
		font-size: var(--font-size-xs);
		color: var(--color-muted);
		padding: var(--space-md);
	}
</style>
