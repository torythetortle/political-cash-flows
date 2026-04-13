<script lang="ts">
	import { onMount } from 'svelte';
	import { geoAlbersUsa, geoPath } from 'd3-geo';
	import { scaleSequential } from 'd3-scale';
	import { interpolateYlOrRd } from 'd3-scale-chromatic';
	import { format } from 'd3-format';
	import * as topojson from 'topojson-client';
	import type { StateSpendMap } from '$lib/data/types';
	import { formatDollars } from '$lib/utils/formatters';

	interface Props {
		stateSpend: StateSpendMap;
		highlightStates?: string[];
		visible?: boolean;
	}

	let { stateSpend, highlightStates = [], visible = true }: Props = $props();

	let container: HTMLDivElement;
	let width = $state(800);
	let height = $state(500);
	let us: any = $state(null);
	let hoveredState = $state<string | null>(null);
	let mouseX = $state(0);
	let mouseY = $state(0);

	// State FIPS → abbreviation mapping
	const FIPS_TO_STATE: Record<string, string> = {
		'01': 'AL', '02': 'AK', '04': 'AZ', '05': 'AR', '06': 'CA',
		'08': 'CO', '09': 'CT', '10': 'DE', '11': 'DC', '12': 'FL',
		'13': 'GA', '15': 'HI', '16': 'ID', '17': 'IL', '18': 'IN',
		'19': 'IA', '20': 'KS', '21': 'KY', '22': 'LA', '23': 'ME',
		'24': 'MD', '25': 'MA', '26': 'MI', '27': 'MN', '28': 'MS',
		'29': 'MO', '30': 'MT', '31': 'NE', '32': 'NV', '33': 'NH',
		'34': 'NJ', '35': 'NM', '36': 'NY', '37': 'NC', '38': 'ND',
		'39': 'OH', '40': 'OK', '41': 'OR', '42': 'PA', '44': 'RI',
		'45': 'SC', '46': 'SD', '47': 'TN', '48': 'TX', '49': 'UT',
		'50': 'VT', '51': 'VA', '53': 'WA', '54': 'WV', '55': 'WI',
		'56': 'WY',
	};

	const maxSpend = $derived(
		Math.max(...Object.values(stateSpend).map((s) => s.total_spend))
	);

	const colorScale = $derived(
		scaleSequential(interpolateYlOrRd).domain([0, maxSpend])
	);

	const projection = $derived(
		geoAlbersUsa().fitSize([width, height], us ? topojson.feature(us, us.objects.states) as any : { type: 'Sphere' })
	);

	const pathGen = $derived(geoPath().projection(projection));

	onMount(async () => {
		const res = await fetch('https://cdn.jsdelivr.net/npm/us-atlas@3/states-10m.json');
		us = await res.json();

		const observer = new ResizeObserver((entries) => {
			for (const entry of entries) {
				width = entry.contentRect.width;
				height = entry.contentRect.height;
			}
		});
		observer.observe(container);

		return () => observer.disconnect();
	});

	function stateAbbr(id: string): string {
		return FIPS_TO_STATE[id.padStart(2, '0')] ?? '';
	}

	function getFill(id: string): string {
		const abbr = stateAbbr(id);
		const spend = stateSpend[abbr];
		if (!spend) return '#E4E4DE';

		if (highlightStates.length > 0 && !highlightStates.includes(abbr)) {
			return '#E4E4DE';
		}

		return colorScale(spend.total_spend);
	}

	function getOpacity(id: string): number {
		if (!visible) return 0;
		const abbr = stateAbbr(id);
		if (highlightStates.length > 0 && !highlightStates.includes(abbr)) {
			return 0.2;
		}
		return 1;
	}

	function handleMouseMove(e: MouseEvent) {
		const rect = container.getBoundingClientRect();
		mouseX = e.clientX - rect.left;
		mouseY = e.clientY - rect.top;
	}
</script>

<!-- svelte-ignore a11y_no_static_element_interactions -->
<div class="choropleth" bind:this={container} onmousemove={handleMouseMove}>
	{#if us}
		<svg {width} {height} role="img" aria-label="Map of political spending by state">
			<g class="states">
				{#each topojson.feature(us, us.objects.states).features as state}
					{@const abbr = stateAbbr(String(state.id))}
					{@const spend = stateSpend[abbr]}
					<!-- svelte-ignore a11y_no_static_element_interactions -->
					<path
						d={pathGen(state) ?? ''}
						fill={getFill(String(state.id))}
						opacity={getOpacity(String(state.id))}
						stroke="var(--color-bg)"
						stroke-width="0.8"
						class="state-path"
						class:highlighted={highlightStates.includes(abbr)}
						onmouseenter={() => (hoveredState = abbr)}
						onmouseleave={() => (hoveredState = null)}
					/>
				{/each}
			</g>

			{#if highlightStates.length > 0}
				<g class="state-labels">
					{#each topojson.feature(us, us.objects.states).features as state}
						{@const abbr = stateAbbr(String(state.id))}
						{#if highlightStates.includes(abbr)}
							{@const centroid = pathGen.centroid(state)}
							{#if centroid[0] && centroid[1]}
								<text
									x={centroid[0]}
									y={centroid[1]}
									text-anchor="middle"
									dominant-baseline="middle"
									class="state-label"
								>
									{abbr}
								</text>
							{/if}
						{/if}
					{/each}
				</g>
			{/if}
		</svg>

		{#if hoveredState && stateSpend[hoveredState]}
			{@const spend = stateSpend[hoveredState]}
			<div class="tooltip" style:left="{mouseX + 12}px" style:top="{mouseY - 10}px">
				<div class="tooltip-state">{hoveredState}</div>
				<div class="tooltip-row">
					<span class="dem-dot"></span>
					DEM: {formatDollars(spend.dem_spend)}
				</div>
				<div class="tooltip-row">
					<span class="rep-dot"></span>
					REP: {formatDollars(spend.rep_spend)}
				</div>
				<div class="tooltip-total">
					Total: {formatDollars(spend.total_spend)}
				</div>
			</div>
		{/if}
	{:else}
		<div class="loading">Loading map...</div>
	{/if}
</div>

<style>
	.choropleth {
		width: 100%;
		height: 100%;
		position: relative;
	}

	svg {
		display: block;
	}

	.state-path {
		cursor: pointer;
		transition: opacity 0.4s ease, fill 0.4s ease;
	}

	.state-path:hover {
		stroke: var(--color-accent);
		stroke-width: 1.5;
	}

	.state-path.highlighted {
		stroke: var(--color-accent);
		stroke-width: 1.5;
	}

	.state-label {
		font-family: var(--font-mono);
		font-size: 10px;
		font-weight: 600;
		fill: var(--color-bg);
		pointer-events: none;
	}

	.tooltip {
		position: absolute;
		background: var(--color-surface-raised);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-md);
		padding: 10px 14px;
		font-size: var(--font-size-xs);
		pointer-events: none;
		z-index: 10;
		min-width: 140px;
	}

	.tooltip-state {
		font-family: var(--font-mono);
		font-weight: 600;
		font-size: var(--font-size-sm);
		margin-bottom: 6px;
		color: var(--color-text);
	}

	.tooltip-row {
		display: flex;
		align-items: center;
		gap: 6px;
		color: var(--color-text-secondary);
		margin-bottom: 2px;
		font-family: var(--font-mono);
	}

	.dem-dot, .rep-dot {
		display: inline-block;
		width: 8px;
		height: 8px;
		border-radius: 50%;
	}

	.dem-dot { background: var(--color-dem); }
	.rep-dot { background: var(--color-rep); }

	.tooltip-total {
		margin-top: 4px;
		padding-top: 4px;
		border-top: 1px solid var(--color-border);
		font-family: var(--font-mono);
		font-weight: 600;
		color: var(--color-text);
	}

	.loading {
		display: flex;
		align-items: center;
		justify-content: center;
		height: 100%;
		color: var(--color-muted);
		font-family: var(--font-mono);
		font-size: var(--font-size-sm);
	}

	@media (max-width: 600px) {
		.tooltip {
			min-width: 110px;
			padding: 8px 10px;
			font-size: 10px;
			max-width: calc(100vw - 40px);
		}

		.state-label {
			font-size: 8px;
		}
	}
</style>
