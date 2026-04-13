<script lang="ts">
	import { selectedVendor, clusterVendors } from '$lib/stores/explorerStore';
	import { formatDollars, formatDollarsLong, formatCategory } from '$lib/utils/formatters';
	import { partyColor } from '$lib/utils/colors';
	import PartyBadge from '$lib/components/ui/PartyBadge.svelte';
	import type { VendorFeature, VendorDetailsMap } from '$lib/data/types';

	interface Props {
		vendorDetails?: VendorDetailsMap;
	}

	let { vendorDetails = {} }: Props = $props();

	let vendor = $derived($selectedVendor);
	let cluster = $derived($clusterVendors);
	let vProps = $derived(vendor?.properties ?? null);
	let detail = $derived(vProps ? vendorDetails[vProps.vendor_id] ?? null : null);

	let clusterTotal = $derived(
		cluster.reduce((sum, v) => sum + v.properties.total_spend, 0)
	);

	// Build sparkline path from timeline data
	let sparklinePath = $derived.by(() => {
		if (!detail?.timeline) return '';
		const entries = Object.entries(detail.timeline).sort(([a], [b]) => a.localeCompare(b));
		if (entries.length < 2) return '';
		const maxVal = Math.max(...entries.map(([, v]) => v));
		if (maxVal === 0) return '';
		const w = 280;
		const h = 40;
		const points = entries.map(([, v], i) => {
			const x = (i / (entries.length - 1)) * w;
			const y = h - (v / maxVal) * h;
			return `${x},${y}`;
		});
		return `M${points.join('L')}`;
	});

	// Top purpose categories as sorted array
	let purposeEntries = $derived.by(() => {
		if (!detail?.purpose) return [];
		return Object.entries(detail.purpose)
			.sort(([, a], [, b]) => b - a)
			.slice(0, 5);
	});

	let purposeTotal = $derived(
		purposeEntries.reduce((sum, [, v]) => sum + v, 0)
	);

	function close() {
		selectedVendor.set(null);
		clusterVendors.set([]);
	}

	function selectFromCluster(v: VendorFeature) {
		clusterVendors.set([]);
		selectedVendor.set(v);
	}

	function spendBarWidth(dem: number, rep: number): string {
		const total = dem + rep;
		if (total === 0) return '50%';
		return `${(dem / total) * 100}%`;
	}
</script>

{#if cluster.length > 0}
	<!-- Cluster list -->
	<div class="vendor-detail">
		<div class="detail-header">
			<div>
				<h2>{cluster.length} vendors in this area</h2>
				<p class="location">{formatDollars(clusterTotal)} total</p>
			</div>
			<button class="close-btn" onclick={close} aria-label="Close">&times;</button>
		</div>
		<div class="cluster-list">
			{#each cluster as v, i (v.properties.vendor_id + '-' + i)}
				{@const p = v.properties}
				<button class="cluster-row" onclick={() => selectFromCluster(v)}>
					<span class="party-dot" style:background={partyColor(p.dominant_party)}></span>
					<div class="cluster-info">
						<span class="cluster-name">{p.canonical_name}</span>
						<span class="cluster-loc">{p.city}, {p.state}</span>
					</div>
					<span class="cluster-spend">{formatDollars(p.total_spend)}</span>
				</button>
			{/each}
		</div>
	</div>
{:else if vProps}
	<!-- Single vendor -->
	<div class="vendor-detail">
		<div class="detail-header">
			<div>
				<h2>{vProps.canonical_name}</h2>
				<p class="location">{vProps.city}, {vProps.state}</p>
			</div>
			<button class="close-btn" onclick={close} aria-label="Close">&times;</button>
		</div>

		<div class="spend-hero">
			<span class="hero-value">{formatDollarsLong(vProps.total_spend)}</span>
			<span class="hero-label">Total received &middot; {vProps.cycles.join(', ')}</span>
		</div>

		<div class="party-split">
			<div class="split-labels">
				<span class="dem-label">DEM {formatDollars(vProps.dem_spend)}</span>
				<span class="rep-label">REP {formatDollars(vProps.rep_spend)}</span>
			</div>
			<div class="split-bar">
				<div class="split-dem" style:width={spendBarWidth(vProps.dem_spend, vProps.rep_spend)}></div>
			</div>
		</div>

		<!-- Spending timeline sparkline -->
		{#if sparklinePath}
			<div class="detail-section">
				<span class="section-label">Spending Over Time</span>
				<svg class="sparkline" viewBox="0 0 280 40" preserveAspectRatio="none">
					<path d={sparklinePath} fill="none" stroke="var(--color-accent)" stroke-width="1.5" />
				</svg>
			</div>
		{/if}

		<!-- Purpose breakdown -->
		{#if purposeEntries.length > 0}
			<div class="detail-section">
				<span class="section-label">Spending by Purpose</span>
				<div class="purpose-list">
					{#each purposeEntries as [category, amount]}
						<div class="purpose-row">
							<div class="purpose-bar-track">
								<div
									class="purpose-bar-fill"
									style:width="{(amount / purposeTotal) * 100}%"
								></div>
							</div>
							<span class="purpose-name">{category}</span>
							<span class="purpose-amt">{formatDollars(amount)}</span>
						</div>
					{/each}
				</div>
			</div>
		{/if}

		<!-- Top committees -->
		{#if detail?.committees?.length}
			<div class="detail-section">
				<span class="section-label">Top Committees</span>
				<div class="committee-list">
					{#each detail.committees.slice(0, 5) as cmte}
						<div class="committee-row">
							<span class="party-dot" style:background={partyColor(cmte.party)}></span>
							<span class="committee-name">{cmte.name}</span>
							<span class="committee-amt">{formatDollars(cmte.spend)}</span>
						</div>
					{/each}
				</div>
			</div>
		{/if}

		<!-- Linked candidates -->
		{#if detail?.candidates?.length}
			<div class="detail-section">
				<span class="section-label">Linked Candidates</span>
				<div class="candidate-list">
					{#each detail.candidates as cand}
						<div class="candidate-row">
							<div class="candidate-info">
								<span class="candidate-name">{cand.name}</span>
								<span class="candidate-office">
									{cand.office === 'H' ? 'House' : cand.office === 'S' ? 'Senate' : cand.office === 'P' ? 'President' : cand.office}
									{cand.state ? ` — ${cand.state}` : ''}
								</span>
							</div>
							<span class="candidate-amt">{formatDollars(cand.spend)}</span>
						</div>
					{/each}
				</div>
			</div>
		{/if}

		<div class="detail-meta">
			<span>{formatCategory(vProps.category)}</span>
			<span class="meta-sep">&middot;</span>
			<PartyBadge party={vProps.dominant_party} size="sm" />
			<span class="meta-sep">&middot;</span>
			<span class="mono">{vProps.vendor_id}</span>
		</div>
	</div>
{:else}
	<div class="empty-state">
		<p>Click a vendor or cluster on the map</p>
	</div>
{/if}

<style>
	.vendor-detail {
		display: flex;
		flex-direction: column;
		gap: var(--space-md);
		animation: fadeIn 0.2s ease;
	}

	@keyframes fadeIn {
		from { opacity: 0; transform: translateY(4px); }
		to { opacity: 1; transform: translateY(0); }
	}

	.detail-header {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		gap: var(--space-sm);
	}

	h2 { font-size: var(--font-size-base); font-weight: 600; color: var(--color-text); line-height: 1.2; }
	.location { font-size: var(--font-size-xs); color: var(--color-text-secondary); margin-top: 2px; }

	.close-btn {
		background: none; border: 1px solid var(--color-border); border-radius: var(--radius-sm);
		color: var(--color-muted); font-size: 18px; width: 28px; height: 28px;
		display: flex; align-items: center; justify-content: center; cursor: pointer; flex-shrink: 0;
	}
	.close-btn:hover { color: var(--color-text); border-color: var(--color-text-secondary); }

	/* Cluster list */
	.cluster-list { display: flex; flex-direction: column; gap: 2px; max-height: 400px; overflow-y: auto; }
	.cluster-row {
		display: flex; align-items: center; gap: 8px; padding: 6px 8px;
		border: 1px solid transparent; border-radius: var(--radius-sm);
		background: transparent; cursor: pointer; text-align: left; transition: all var(--transition-fast);
	}
	.cluster-row:hover { background: var(--color-surface-raised); border-color: var(--color-border); }
	.cluster-info { flex: 1; min-width: 0; display: flex; flex-direction: column; }
	.cluster-name { font-size: var(--font-size-xs); color: var(--color-text); font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
	.cluster-loc { font-size: 10px; color: var(--color-muted); }
	.cluster-spend { font-family: var(--font-mono); font-size: 10px; color: var(--color-accent); white-space: nowrap; }

	/* Spend hero */
	.spend-hero { display: flex; flex-direction: column; gap: 2px; }
	.hero-value { font-family: var(--font-mono); font-size: var(--font-size-xl); font-weight: 700; color: var(--color-accent); line-height: 1; }
	.hero-label { font-size: 10px; color: var(--color-muted); text-transform: uppercase; letter-spacing: 0.06em; }

	/* Party split */
	.party-split { display: flex; flex-direction: column; gap: 4px; }
	.split-labels { display: flex; justify-content: space-between; font-family: var(--font-mono); font-size: 10px; }
	.dem-label { color: var(--color-dem); }
	.rep-label { color: var(--color-rep); }
	.split-bar { height: 6px; border-radius: 3px; background: var(--color-rep); overflow: hidden; }
	.split-dem { height: 100%; background: var(--color-dem); border-radius: 3px 0 0 3px; transition: width var(--transition-base); }

	/* Sections */
	.detail-section { display: flex; flex-direction: column; gap: 6px; padding-top: var(--space-sm); border-top: 1px solid var(--color-border); }
	.section-label { font-size: 10px; color: var(--color-muted); text-transform: uppercase; letter-spacing: 0.06em; font-weight: 500; }

	/* Sparkline */
	.sparkline { width: 100%; height: 40px; }

	/* Purpose */
	.purpose-list { display: flex; flex-direction: column; gap: 4px; }
	.purpose-row { display: flex; align-items: center; gap: 6px; font-size: var(--font-size-xs); }
	.purpose-bar-track { width: 50px; height: 4px; background: var(--color-border); border-radius: 2px; flex-shrink: 0; }
	.purpose-bar-fill { height: 100%; background: var(--color-accent); border-radius: 2px; }
	.purpose-name { flex: 1; color: var(--color-text-secondary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
	.purpose-amt { font-family: var(--font-mono); color: var(--color-text); font-size: 10px; white-space: nowrap; }

	/* Committees */
	.committee-list, .candidate-list { display: flex; flex-direction: column; gap: 4px; }
	.committee-row, .candidate-row { display: flex; align-items: center; gap: 6px; font-size: var(--font-size-xs); }
	.party-dot { width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; }
	.committee-name, .candidate-name { flex: 1; color: var(--color-text); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
	.committee-amt, .candidate-amt { font-family: var(--font-mono); color: var(--color-accent); font-size: 10px; white-space: nowrap; }
	.candidate-info { flex: 1; min-width: 0; display: flex; flex-direction: column; }
	.candidate-office { font-size: 10px; color: var(--color-muted); }

	/* Meta */
	.detail-meta {
		display: flex; align-items: center; gap: 6px; flex-wrap: wrap;
		padding-top: var(--space-sm); border-top: 1px solid var(--color-border);
		font-size: 10px; color: var(--color-muted);
	}
	.meta-sep { opacity: 0.4; }

	.empty-state { display: flex; align-items: center; justify-content: center; min-height: 80px; }
	.empty-state p { font-size: var(--font-size-sm); color: var(--color-muted); text-align: center; }
</style>
