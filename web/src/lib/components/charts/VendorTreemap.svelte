<script lang="ts">
	import { onMount } from 'svelte';
	import { treemap, hierarchy, treemapSquarify } from 'd3-hierarchy';
	import type { TopVendor } from '$lib/data/types';
	import { partyColor } from '$lib/utils/colors';
	import { formatDollars, formatCategory } from '$lib/utils/formatters';

	interface Props {
		vendors: TopVendor[];
		visible?: boolean;
	}

	let { vendors, visible = true }: Props = $props();

	let container: HTMLDivElement;
	let width = $state(600);
	let height = $state(400);
	let hoveredVendor = $state<TopVendor | null>(null);
	let mouseX = $state(0);
	let mouseY = $state(0);

	const top20 = $derived(vendors.slice(0, 20));

	const root = $derived.by(() => {
		const h = hierarchy({ children: top20 } as any)
			.sum((d: any) => d.total_spend ?? 0);

		treemap<any>()
			.tile(treemapSquarify)
			.size([width, height])
			.padding(2)
			.round(true)(h);

		return h;
	});

	const leaves = $derived(root.leaves());

	const totalSpend = $derived(
		top20.reduce((sum, v) => sum + v.total_spend, 0)
	);

	onMount(() => {
		const observer = new ResizeObserver((entries) => {
			for (const entry of entries) {
				width = entry.contentRect.width;
				height = Math.max(300, entry.contentRect.width * 0.6);
			}
		});
		observer.observe(container);
		return () => observer.disconnect();
	});

	function handleMouseMove(e: MouseEvent) {
		const rect = container.getBoundingClientRect();
		mouseX = e.clientX - rect.left;
		mouseY = e.clientY - rect.top;
	}
</script>

<div
	class="treemap-wrapper"
	class:visible
	bind:this={container}
	onmousemove={handleMouseMove}
	role="img"
	aria-label="Treemap showing top 20 political vendors by total spend"
>
	<svg {width} {height}>
		{#each leaves as leaf}
			{@const d = leaf.data as TopVendor}
			{@const w = (leaf as any).x1 - (leaf as any).x0}
			{@const h = (leaf as any).y1 - (leaf as any).y0}
			{@const party = d.dem_pct > d.rep_pct ? 'DEM' : 'REP'}
			<!-- svelte-ignore a11y_no_static_element_interactions -->
			<g
				transform="translate({(leaf as any).x0},{(leaf as any).y0})"
				onmouseenter={() => hoveredVendor = d}
				onmouseleave={() => hoveredVendor = null}
			>
				<rect
					width={w}
					height={h}
					fill={partyColor(party)}
					opacity={hoveredVendor === d ? 1 : 0.75}
					rx="2"
					class="treemap-cell"
				/>
				{#if w > 60 && h > 30}
					<text
						x={6}
						y={18}
						class="cell-name"
						clip-path="inset(0 {Math.max(0, w - 8)}px 0 0)"
					>
						{d.canonical_name.length > Math.floor(w / 7)
							? d.canonical_name.slice(0, Math.floor(w / 7)) + '...'
							: d.canonical_name}
					</text>
				{/if}
				{#if w > 50 && h > 48}
					<text x={6} y={34} class="cell-amount">
						{formatDollars(d.total_spend)}
					</text>
				{/if}
			</g>
		{/each}
	</svg>

	{#if hoveredVendor}
		<div
			class="treemap-tooltip"
			style:left="{Math.min(mouseX + 12, width - 200)}px"
			style:top="{mouseY - 10}px"
		>
			<div class="tt-name">{hoveredVendor.canonical_name}</div>
			<div class="tt-amount">{formatDollars(hoveredVendor.total_spend)}</div>
			<div class="tt-pct">
				{((hoveredVendor.total_spend / totalSpend) * 100).toFixed(1)}% of top 20
			</div>
			<div class="tt-detail">{formatCategory(hoveredVendor.category)}</div>
			<div class="tt-location">{hoveredVendor.city}, {hoveredVendor.state}</div>
		</div>
	{/if}
</div>

<style>
	.treemap-wrapper {
		width: 100%;
		position: relative;
		opacity: 0;
		transition: opacity 0.6s ease;
	}

	.treemap-wrapper.visible {
		opacity: 1;
	}

	svg {
		display: block;
	}

	.treemap-cell {
		cursor: pointer;
		transition: opacity var(--transition-fast);
	}

	.cell-name {
		font-family: var(--font-sans);
		font-size: 11px;
		font-weight: 600;
		fill: var(--color-bg);
		pointer-events: none;
	}

	.cell-amount {
		font-family: var(--font-mono);
		font-size: 10px;
		fill: color-mix(in srgb, var(--color-bg) 80%, transparent);
		pointer-events: none;
	}

	.treemap-tooltip {
		position: absolute;
		background: var(--color-surface-raised);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-md);
		padding: 10px 14px;
		pointer-events: none;
		z-index: 10;
		min-width: 180px;
	}

	.tt-name {
		font-weight: 600;
		font-size: var(--font-size-sm);
		color: var(--color-text);
		margin-bottom: 4px;
	}

	.tt-amount {
		font-family: var(--font-mono);
		font-size: var(--font-size-lg);
		font-weight: 600;
		color: var(--color-accent);
	}

	.tt-pct {
		font-family: var(--font-mono);
		font-size: var(--font-size-xs);
		color: var(--color-text-secondary);
		margin-bottom: 6px;
	}

	.tt-detail, .tt-location {
		font-size: var(--font-size-xs);
		color: var(--color-muted);
	}

	@media (max-width: 600px) {
		.treemap-tooltip {
			min-width: 140px;
			max-width: calc(100vw - 40px);
		}
	}
</style>
