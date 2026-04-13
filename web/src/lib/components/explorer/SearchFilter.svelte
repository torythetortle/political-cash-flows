<script lang="ts">
	import {
		searchQuery,
		selectedParty,
		selectedState,
		spendRange,
	} from '$lib/stores/explorerStore';
	import type { StateSpendMap } from '$lib/data/types';

	interface Props {
		stateSpend: StateSpendMap;
		vendorCount: number;
		filteredCount: number;
	}

	let { stateSpend, vendorCount, filteredCount }: Props = $props();

	let localSearch = $state('');
	let minSpend = $state('');
	let debounceTimer: ReturnType<typeof setTimeout>;

	let stateOptions = $derived(
		Object.entries(stateSpend)
			.sort(([, a], [, b]) => b.total_spend - a.total_spend)
			.map(([abbr]) => abbr)
	);

	function handleSearchInput() {
		clearTimeout(debounceTimer);
		debounceTimer = setTimeout(() => {
			searchQuery.set(localSearch);
		}, 200);
	}

	function handleMinSpend() {
		const val = parseFloat(minSpend);
		if (!isNaN(val) && val > 0) {
			spendRange.set([val, Infinity]);
		} else {
			spendRange.set([0, Infinity]);
		}
	}

	function clearAll() {
		localSearch = '';
		minSpend = '';
		searchQuery.set('');
		selectedParty.set('ALL');
		selectedState.set('ALL');
		spendRange.set([0, Infinity]);
	}

	let hasFilters = $derived(
		$searchQuery !== '' || $selectedParty !== 'ALL' || $selectedState !== 'ALL' || $spendRange[0] > 0
	);
</script>

<div class="search-filter">
	<div class="filter-row">
		<!-- Search -->
		<div class="filter-group search-group">
			<label for="vendor-search">Search</label>
			<input
				id="vendor-search"
				type="text"
				placeholder="Vendor name..."
				bind:value={localSearch}
				oninput={handleSearchInput}
			/>
		</div>

		<!-- Party -->
		<div class="filter-group">
			<!-- svelte-ignore a11y_label_has_associated_control -->
			<label>Party</label>
			<div class="button-group">
				{#each ['ALL', 'DEM', 'REP'] as party}
					<button
						class="filter-btn"
						class:active={$selectedParty === party}
						class:dem={party === 'DEM'}
						class:rep={party === 'REP'}
						onclick={() => selectedParty.set(party as 'ALL' | 'DEM' | 'REP')}
					>
						{party === 'ALL' ? 'All' : party}
					</button>
				{/each}
			</div>
		</div>

		<!-- State -->
		<div class="filter-group">
			<label for="state-select">State</label>
			<select id="state-select" bind:value={$selectedState}>
				<option value="ALL">All states</option>
				{#each stateOptions as st}
					<option value={st}>{st}</option>
				{/each}
			</select>
		</div>

		<!-- Min spend -->
		<div class="filter-group">
			<label for="min-spend">Min. spend</label>
			<input
				id="min-spend"
				type="number"
				placeholder="$100K"
				bind:value={minSpend}
				oninput={handleMinSpend}
			/>
		</div>

		<!-- Count + clear -->
		<div class="filter-meta">
			<span class="count">{filteredCount.toLocaleString()} / {vendorCount.toLocaleString()}</span>
			{#if hasFilters}
				<button class="clear-btn" onclick={clearAll}>Clear</button>
			{/if}
		</div>
	</div>
</div>

<style>
	.search-filter {
		flex: 1;
	}

	.filter-row {
		display: flex;
		align-items: flex-end;
		gap: var(--space-md);
		flex-wrap: wrap;
	}

	.filter-group {
		display: flex;
		flex-direction: column;
		gap: 3px;
	}

	.search-group {
		flex: 1;
		min-width: 160px;
	}

	label {
		font-size: 10px;
		color: var(--color-muted);
		text-transform: uppercase;
		letter-spacing: 0.06em;
		font-weight: 500;
	}

	input, select {
		background: var(--color-bg);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-sm);
		color: var(--color-text);
		font-family: var(--font-mono);
		font-size: var(--font-size-xs);
		padding: 6px 8px;
		outline: none;
		transition: border-color var(--transition-fast);
		min-width: 0;
	}

	input:focus, select:focus {
		border-color: var(--color-accent);
	}

	input::placeholder {
		color: var(--color-muted);
	}

	select {
		cursor: pointer;
		width: 90px;
	}

	input[type="number"] {
		width: 90px;
	}

	.button-group {
		display: flex;
		gap: 2px;
	}

	.filter-btn {
		padding: 5px 10px;
		border: 1px solid var(--color-border);
		border-radius: var(--radius-sm);
		background: transparent;
		color: var(--color-text-secondary);
		font-family: var(--font-mono);
		font-size: var(--font-size-xs);
		font-weight: 500;
		cursor: pointer;
		transition: all var(--transition-fast);
	}

	.filter-btn:hover {
		border-color: var(--color-accent-dim);
	}

	.filter-btn.active {
		background: var(--color-surface-raised);
		border-color: var(--color-accent);
		color: var(--color-text);
	}

	.filter-btn.active.dem {
		border-color: var(--color-dem);
		color: var(--color-dem);
	}

	.filter-btn.active.rep {
		border-color: var(--color-rep);
		color: var(--color-rep);
	}

	.filter-meta {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
		padding-bottom: 2px;
	}

	.count {
		font-family: var(--font-mono);
		font-size: 10px;
		color: var(--color-muted);
		white-space: nowrap;
	}

	.clear-btn {
		padding: 4px 8px;
		border: 1px solid var(--color-border);
		border-radius: var(--radius-sm);
		background: none;
		color: var(--color-muted);
		font-family: var(--font-mono);
		font-size: 10px;
		cursor: pointer;
	}

	.clear-btn:hover {
		color: var(--color-text);
		border-color: var(--color-text-secondary);
	}
</style>
