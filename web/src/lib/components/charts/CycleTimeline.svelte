<script lang="ts">
	import { onMount } from 'svelte';
	import { scaleLinear, scaleBand } from 'd3-scale';
	import type { VendorCycleData } from '$lib/data/types';
	import { partyColor } from '$lib/utils/colors';
	import { formatDollars } from '$lib/utils/formatters';

	interface Props {
		vendorCycles: VendorCycleData[];
		visible?: boolean;
	}

	let { vendorCycles, visible = true }: Props = $props();

	let container: HTMLDivElement;
	let width = $state(600);
	let hoveredCell = $state<{ vendor: string; cycle: string; spend: number } | null>(null);

	const top15 = $derived(vendorCycles.slice(0, 15));
	const cycles = ['2016', '2018', '2020', '2022', '2024'];

	const maxSpend = $derived(
		Math.max(
			...top15.flatMap((v) =>
				Object.values(v.cycles).filter((s) => s > 0)
			)
		)
	);

	const ROW_HEIGHT = 36;
	const HEADER_HEIGHT = 30;
	const LEFT_MARGIN = 180;
	const RIGHT_MARGIN = 20;

	const chartWidth = $derived(width - LEFT_MARGIN - RIGHT_MARGIN);
	const chartHeight = $derived(top15.length * ROW_HEIGHT + HEADER_HEIGHT);

	const xScale = $derived(
		scaleBand<string>()
			.domain(cycles)
			.range([0, chartWidth])
			.padding(0.15)
	);

	const radiusScale = $derived(
		scaleLinear()
			.domain([0, maxSpend])
			.range([0, Math.min(xScale.bandwidth() / 2, ROW_HEIGHT / 2 - 2)])
	);

	onMount(() => {
		const observer = new ResizeObserver((entries) => {
			for (const entry of entries) {
				width = entry.contentRect.width;
			}
		});
		observer.observe(container);
		return () => observer.disconnect();
	});
</script>

<div
	class="cycle-timeline"
	class:visible
	bind:this={container}
	role="img"
	aria-label="Timeline showing vendor spending across election cycles"
>
	<svg width={width} height={chartHeight}>
		<!-- Column headers -->
		{#each cycles as cycle}
			<text
				x={LEFT_MARGIN + (xScale(cycle) ?? 0) + xScale.bandwidth() / 2}
				y={18}
				text-anchor="middle"
				class="cycle-header"
			>
				{cycle}
			</text>
		{/each}

		<!-- Grid lines -->
		{#each top15 as _, i}
			<line
				x1={LEFT_MARGIN}
				x2={width - RIGHT_MARGIN}
				y1={HEADER_HEIGHT + i * ROW_HEIGHT + ROW_HEIGHT / 2}
				y2={HEADER_HEIGHT + i * ROW_HEIGHT + ROW_HEIGHT / 2}
				class="grid-line"
			/>
		{/each}

		<!-- Vendor rows -->
		{#each top15 as vendor, i}
			<!-- Vendor name -->
			<text
				x={LEFT_MARGIN - 10}
				y={HEADER_HEIGHT + i * ROW_HEIGHT + ROW_HEIGHT / 2 + 4}
				text-anchor="end"
				class="vendor-name"
			>
				{vendor.canonical_name.length > 20
					? vendor.canonical_name.slice(0, 20) + '...'
					: vendor.canonical_name}
			</text>

			<!-- Spend circles per cycle -->
			{#each cycles as cycle}
				{@const spend = vendor.cycles[cycle] ?? 0}
				{@const cx = LEFT_MARGIN + (xScale(cycle) ?? 0) + xScale.bandwidth() / 2}
				{@const cy = HEADER_HEIGHT + i * ROW_HEIGHT + ROW_HEIGHT / 2}
				{#if spend > 0}
					<!-- svelte-ignore a11y_no_static_element_interactions -->
					<circle
						{cx}
						{cy}
						r={radiusScale(spend)}
						fill={partyColor(vendor.dominant_party)}
						opacity={hoveredCell?.vendor === vendor.vendor_id && hoveredCell?.cycle === cycle ? 1 : 0.7}
						class="spend-circle"
						onmouseenter={() => hoveredCell = { vendor: vendor.vendor_id, cycle, spend }}
						onmouseleave={() => hoveredCell = null}
					/>
				{:else}
					<circle
						{cx}
						{cy}
						r={2}
						fill="var(--color-border)"
						opacity={0.4}
					/>
				{/if}
			{/each}
		{/each}
	</svg>

	{#if hoveredCell}
		{@const vendor = top15.find((v) => v.vendor_id === hoveredCell?.vendor)}
		{#if vendor && hoveredCell}
			<div class="cycle-tooltip">
				<strong>{vendor.canonical_name}</strong><br />
				{hoveredCell.cycle}: {formatDollars(hoveredCell.spend)}
			</div>
		{/if}
	{/if}
</div>

<style>
	.cycle-timeline {
		width: 100%;
		position: relative;
		opacity: 0;
		transition: opacity 0.6s ease;
		overflow-x: auto;
	}

	.cycle-timeline.visible {
		opacity: 1;
	}

	svg {
		display: block;
		min-width: 500px;
	}

	.cycle-header {
		font-family: var(--font-mono);
		font-size: 11px;
		font-weight: 600;
		fill: var(--color-text-secondary);
	}

	.vendor-name {
		font-family: var(--font-sans);
		font-size: 11px;
		fill: var(--color-text-secondary);
	}

	.grid-line {
		stroke: var(--color-border);
		stroke-width: 0.5;
		stroke-dasharray: 2 4;
	}

	.spend-circle {
		cursor: pointer;
		transition: opacity var(--transition-fast), r var(--transition-fast);
	}

	.spend-circle:hover {
		opacity: 1;
	}

	.cycle-tooltip {
		position: fixed;
		bottom: var(--space-xl);
		right: var(--space-xl);
		background: var(--color-surface-raised);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-md);
		padding: 8px 12px;
		font-size: var(--font-size-xs);
		color: var(--color-text);
		pointer-events: none;
		z-index: 10;
		font-family: var(--font-mono);
	}

	@media (max-width: 600px) {
		svg {
			min-width: 350px;
		}

		.vendor-name {
			font-size: 9px;
		}

		.cycle-header {
			font-size: 9px;
		}
	}
</style>
