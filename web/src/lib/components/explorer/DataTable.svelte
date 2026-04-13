<script lang="ts">
	import type { VendorFeature } from '$lib/data/types';
	import { selectedVendor, clusterVendors } from '$lib/stores/explorerStore';
	import { formatDollars } from '$lib/utils/formatters';
	import { partyColor } from '$lib/utils/colors';

	interface Props {
		vendors: VendorFeature[];
	}

	let { vendors }: Props = $props();

	let sortCol = $state<'spend' | 'name' | 'city' | 'state' | 'party'>('spend');
	let sortAsc = $state(false);
	let page = $state(0);
	const PAGE_SIZE = 50;

	let sorted = $derived.by(() => {
		const arr = [...vendors];
		arr.sort((a, b) => {
			const pa = a.properties;
			const pb = b.properties;
			let cmp = 0;
			switch (sortCol) {
				case 'spend': cmp = pa.total_spend - pb.total_spend; break;
				case 'name': cmp = pa.canonical_name.localeCompare(pb.canonical_name); break;
				case 'city': cmp = pa.city.localeCompare(pb.city); break;
				case 'state': cmp = pa.state.localeCompare(pb.state); break;
				case 'party': cmp = pa.dominant_party.localeCompare(pb.dominant_party); break;
			}
			return sortAsc ? cmp : -cmp;
		});
		return arr;
	});

	let paged = $derived(sorted.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE));
	let totalPages = $derived(Math.ceil(vendors.length / PAGE_SIZE));

	function toggleSort(col: typeof sortCol) {
		if (sortCol === col) {
			sortAsc = !sortAsc;
		} else {
			sortCol = col;
			sortAsc = col === 'name' || col === 'city' || col === 'state';
		}
		page = 0;
	}

	function selectVendor(v: VendorFeature) {
		clusterVendors.set([]);
		selectedVendor.set(v);
	}

	function sortIndicator(col: typeof sortCol): string {
		if (sortCol !== col) return '';
		return sortAsc ? ' \u25B2' : ' \u25BC';
	}
</script>

<div class="data-table-wrapper">
	<div class="table-info">
		<span>{vendors.length.toLocaleString()} vendors</span>
		{#if totalPages > 1}
			<span class="page-info">
				Page {page + 1} of {totalPages}
			</span>
		{/if}
	</div>

	<div class="table-scroll">
		<table>
			<thead>
				<tr>
					<th class="col-name" onclick={() => toggleSort('name')}>
						Vendor{sortIndicator('name')}
					</th>
					<th class="col-city" onclick={() => toggleSort('city')}>
						City{sortIndicator('city')}
					</th>
					<th class="col-state" onclick={() => toggleSort('state')}>
						State{sortIndicator('state')}
					</th>
					<th class="col-party" onclick={() => toggleSort('party')}>
						Party{sortIndicator('party')}
					</th>
					<th class="col-spend" onclick={() => toggleSort('spend')}>
						Total Spend{sortIndicator('spend')}
					</th>
					<th class="col-category">Category</th>
					<th class="col-cycles">Cycles</th>
				</tr>
			</thead>
			<tbody>
				{#each paged as vendor, i (vendor.properties.vendor_id + '-' + (page * PAGE_SIZE + i))}
					{@const p = vendor.properties}
					<tr onclick={() => selectVendor(vendor)} class:selected={$selectedVendor?.properties.vendor_id === p.vendor_id}>
						<td class="col-name">{p.canonical_name}</td>
						<td class="col-city">{p.city}</td>
						<td class="col-state">{p.state}</td>
						<td class="col-party">
							<span class="party-dot" style:background={partyColor(p.dominant_party)}></span>
							{p.dominant_party}
						</td>
						<td class="col-spend mono">{formatDollars(p.total_spend)}</td>
						<td class="col-category">{p.category}</td>
						<td class="col-cycles mono">{p.cycles.join(', ')}</td>
					</tr>
				{/each}
			</tbody>
		</table>
	</div>

	{#if totalPages > 1}
		<div class="pagination">
			<button disabled={page === 0} onclick={() => page--}>Prev</button>
			<span class="page-num">{page + 1} / {totalPages}</span>
			<button disabled={page >= totalPages - 1} onclick={() => page++}>Next</button>
		</div>
	{/if}
</div>

<style>
	.data-table-wrapper {
		display: flex;
		flex-direction: column;
		height: 100%;
	}

	.table-info {
		display: flex;
		justify-content: space-between;
		padding: var(--space-sm) var(--space-md);
		font-size: var(--font-size-xs);
		color: var(--color-muted);
		font-family: var(--font-mono);
		border-bottom: 1px solid var(--color-border);
		flex-shrink: 0;
	}

	.table-scroll {
		flex: 1;
		overflow: auto;
	}

	table {
		width: 100%;
		border-collapse: collapse;
		font-size: var(--font-size-xs);
	}

	thead {
		position: sticky;
		top: 0;
		z-index: 1;
	}

	th {
		background: var(--color-surface-raised);
		padding: 8px 10px;
		text-align: left;
		font-weight: 600;
		color: var(--color-text-secondary);
		text-transform: uppercase;
		letter-spacing: 0.04em;
		font-size: 10px;
		cursor: pointer;
		white-space: nowrap;
		border-bottom: 1px solid var(--color-border);
		user-select: none;
	}

	th:hover {
		color: var(--color-text);
	}

	td {
		padding: 6px 10px;
		color: var(--color-text);
		border-bottom: 1px solid var(--color-border);
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}

	tr {
		cursor: pointer;
		transition: background var(--transition-fast);
	}

	tbody tr:hover {
		background: var(--color-surface-raised);
	}

	tr.selected {
		background: color-mix(in srgb, var(--color-accent) 10%, transparent);
	}

	.col-name { max-width: 220px; }
	.col-city { max-width: 120px; }
	.col-state { width: 50px; }
	.col-party { width: 70px; }
	.col-spend { width: 90px; text-align: right; }
	.col-category { max-width: 140px; }
	.col-cycles { width: 100px; }

	th.col-spend { text-align: right; }

	.party-dot {
		display: inline-block;
		width: 6px;
		height: 6px;
		border-radius: 50%;
		margin-right: 4px;
	}

	.pagination {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: var(--space-md);
		padding: var(--space-sm);
		border-top: 1px solid var(--color-border);
		flex-shrink: 0;
	}

	.pagination button {
		padding: 4px 12px;
		border: 1px solid var(--color-border);
		border-radius: var(--radius-sm);
		background: transparent;
		color: var(--color-text-secondary);
		font-family: var(--font-mono);
		font-size: 10px;
		cursor: pointer;
	}

	.pagination button:hover:not(:disabled) {
		border-color: var(--color-accent);
		color: var(--color-text);
	}

	.pagination button:disabled {
		opacity: 0.3;
		cursor: default;
	}

	.page-num {
		font-family: var(--font-mono);
		font-size: 10px;
		color: var(--color-muted);
	}

	@media (max-width: 768px) {
		.col-category, .col-cycles, .col-city {
			display: none;
		}

		.col-name { max-width: 140px; }
		.col-spend { width: 70px; }

		th, td {
			padding: 6px 6px;
			font-size: 11px;
		}
	}

	@media (max-width: 480px) {
		.col-state {
			display: none;
		}

		.col-name { max-width: 120px; }
	}
</style>
