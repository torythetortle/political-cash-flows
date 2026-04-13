<script lang="ts">
	import { selectedCity, CITY_PRESETS } from '$lib/stores/explorerStore';

	interface Props {
		onFlyTo: (center: [number, number], zoom: number) => void;
	}

	let { onFlyTo }: Props = $props();

	function handleSelect(city: typeof CITY_PRESETS[number]) {
		selectedCity.set(city.name === 'National View' ? null : city.name);
		onFlyTo(city.center as [number, number], city.zoom);
	}
</script>

<div class="city-selector">
	<h3>Jump to City</h3>
	<div class="city-grid">
		{#each CITY_PRESETS as city}
			<button
				class="city-btn"
				class:active={$selectedCity === city.name || ($selectedCity === null && city.name === 'National View')}
				onclick={() => handleSelect(city)}
			>
				{city.name}
			</button>
		{/each}
	</div>
</div>

<style>
	.city-selector {
		display: flex;
		flex-direction: column;
		gap: var(--space-sm);
	}

	h3 {
		font-size: var(--font-size-xs);
		font-weight: 600;
		color: var(--color-text);
		text-transform: uppercase;
		letter-spacing: 0.06em;
	}

	.city-grid {
		display: flex;
		flex-wrap: wrap;
		gap: 4px;
	}

	.city-btn {
		padding: 5px 10px;
		border: 1px solid var(--color-border);
		border-radius: var(--radius-sm);
		background: transparent;
		color: var(--color-text-secondary);
		font-family: var(--font-sans);
		font-size: var(--font-size-xs);
		cursor: pointer;
		transition: all var(--transition-fast);
		white-space: nowrap;
	}

	.city-btn:hover {
		border-color: var(--color-accent-dim);
		color: var(--color-text);
	}

	.city-btn.active {
		background: var(--color-accent);
		border-color: var(--color-accent);
		color: var(--color-bg);
		font-weight: 600;
	}
</style>
