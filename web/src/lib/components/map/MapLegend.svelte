<script lang="ts">
	import { partyFilter } from '$lib/stores/mapStore';

	const filters: Array<{ value: 'ALL' | 'DEM' | 'REP'; label: string }> = [
		{ value: 'ALL', label: 'All' },
		{ value: 'DEM', label: 'DEM' },
		{ value: 'REP', label: 'REP' },
	];
</script>

<div class="legend">
	<div class="legend-section">
		<span class="legend-title">Party</span>
		<div class="filter-pills">
			{#each filters as f}
				<button
					class="pill"
					class:active={$partyFilter === f.value}
					onclick={() => partyFilter.set(f.value)}
				>
					{#if f.value !== 'ALL'}
						<span class="dot" class:dem={f.value === 'DEM'} class:rep={f.value === 'REP'}></span>
					{/if}
					{f.label}
				</button>
			{/each}
		</div>
	</div>

	<div class="legend-section">
		<span class="legend-title">Size = Total Spend</span>
		<div class="size-legend">
			<div class="size-item">
				<span class="size-circle sm"></span>
				<span>$10K</span>
			</div>
			<div class="size-item">
				<span class="size-circle md"></span>
				<span>$500K</span>
			</div>
			<div class="size-item">
				<span class="size-circle lg"></span>
				<span>$10M+</span>
			</div>
		</div>
	</div>
</div>

<style>
	.legend {
		position: absolute;
		top: var(--space-lg);
		right: var(--space-lg);
		background: color-mix(in srgb, var(--color-surface-raised) 90%, transparent);
		backdrop-filter: blur(8px);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-md);
		padding: var(--space-md);
		z-index: 10;
		display: flex;
		flex-direction: column;
		gap: var(--space-md);
		min-width: 150px;
	}

	.legend-title {
		font-size: var(--font-size-xs);
		color: var(--color-muted);
		text-transform: uppercase;
		letter-spacing: 0.08em;
		font-weight: 500;
	}

	.legend-section {
		display: flex;
		flex-direction: column;
		gap: 6px;
	}

	.filter-pills {
		display: flex;
		gap: 4px;
	}

	.pill {
		display: flex;
		align-items: center;
		gap: 4px;
		padding: 3px 8px;
		border: 1px solid var(--color-border);
		border-radius: var(--radius-sm);
		background: transparent;
		color: var(--color-text-secondary);
		font-family: var(--font-mono);
		font-size: var(--font-size-xs);
		cursor: pointer;
		transition: all var(--transition-fast);
	}

	.pill:hover {
		border-color: var(--color-accent-dim);
	}

	.pill.active {
		background: var(--color-surface);
		border-color: var(--color-accent);
		color: var(--color-text);
	}

	.dot {
		width: 7px;
		height: 7px;
		border-radius: 50%;
	}

	.dot.dem { background: var(--color-dem); }
	.dot.rep { background: var(--color-rep); }

	.size-legend {
		display: flex;
		align-items: flex-end;
		gap: var(--space-md);
	}

	.size-item {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 3px;
		font-family: var(--font-mono);
		font-size: 9px;
		color: var(--color-muted);
	}

	.size-circle {
		border-radius: 50%;
		background: var(--color-accent);
		opacity: 0.6;
	}

	.size-circle.sm { width: 8px; height: 8px; }
	.size-circle.md { width: 16px; height: 16px; }
	.size-circle.lg { width: 28px; height: 28px; }

	@media (max-width: 768px) {
		.legend {
			top: auto;
			bottom: var(--space-lg);
			right: var(--space-md);
			left: var(--space-md);
			flex-direction: row;
			justify-content: space-between;
		}
	}
</style>
