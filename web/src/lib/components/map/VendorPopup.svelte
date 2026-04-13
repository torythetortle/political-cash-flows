<script lang="ts">
	import { activeVendor } from '$lib/stores/mapStore';
	import { formatDollars, formatCategory } from '$lib/utils/formatters';
	import PartyBadge from '$lib/components/ui/PartyBadge.svelte';

	let vendor = $derived($activeVendor);

	function close() {
		activeVendor.set(null);
	}
</script>

{#if vendor}
	<div class="popup-overlay" onclick={close} role="presentation"></div>
	<!-- svelte-ignore a11y_no_noninteractive_element_to_interactive_role -->
	<aside class="vendor-popup" role="dialog" aria-label="Vendor details">
		<button class="close-btn" onclick={close} aria-label="Close">&times;</button>

		<div class="popup-header">
			<h3>{vendor.canonical_name}</h3>
			<PartyBadge party={vendor.dominant_party} size="md" />
		</div>

		<div class="popup-stats">
			<div class="stat">
				<span class="stat-value">{formatDollars(vendor.total_spend)}</span>
				<span class="stat-label">Total spend</span>
			</div>
			<div class="stat">
				<span class="stat-value">{vendor.city}, {vendor.state}</span>
				<span class="stat-label">Location</span>
			</div>
		</div>

		<div class="popup-detail">
			<div class="detail-row">
				<span class="detail-label">Category</span>
				<span class="detail-value">{formatCategory(vendor.category)}</span>
			</div>
			<div class="detail-row">
				<span class="detail-label">DEM spend</span>
				<span class="detail-value text-dem">{formatDollars(vendor.dem_spend)}</span>
			</div>
			<div class="detail-row">
				<span class="detail-label">REP spend</span>
				<span class="detail-value text-rep">{formatDollars(vendor.rep_spend)}</span>
			</div>
			<div class="detail-row">
				<span class="detail-label">Active cycles</span>
				<span class="detail-value mono">{vendor.cycles.join(', ')}</span>
			</div>
		</div>

		<div class="spend-bar">
			<div
				class="bar-dem"
				style:width="{(vendor.dem_spend / (vendor.dem_spend + vendor.rep_spend)) * 100}%"
			></div>
			<div class="bar-rep"></div>
		</div>
	</aside>
{/if}

<style>
	.popup-overlay {
		position: fixed;
		inset: 0;
		z-index: 50;
	}

	.vendor-popup {
		position: fixed;
		bottom: var(--space-xl);
		left: var(--space-xl);
		width: 340px;
		background: var(--color-surface-raised);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-lg);
		padding: var(--space-lg);
		z-index: 51;
		animation: slideUp 0.3s ease;
	}

	@keyframes slideUp {
		from {
			opacity: 0;
			transform: translateY(20px);
		}
		to {
			opacity: 1;
			transform: translateY(0);
		}
	}

	.close-btn {
		position: absolute;
		top: var(--space-sm);
		right: var(--space-sm);
		background: none;
		border: none;
		color: var(--color-muted);
		font-size: 24px;
		cursor: pointer;
		padding: 4px 8px;
		line-height: 1;
	}

	.close-btn:hover {
		color: var(--color-text);
	}

	.popup-header {
		display: flex;
		align-items: flex-start;
		justify-content: space-between;
		gap: var(--space-md);
		margin-bottom: var(--space-lg);
	}

	.popup-header h3 {
		font-size: var(--font-size-lg);
		font-weight: 600;
		color: var(--color-text);
		line-height: 1.2;
	}

	.popup-stats {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: var(--space-md);
		margin-bottom: var(--space-lg);
	}

	.stat-value {
		display: block;
		font-family: var(--font-mono);
		font-size: var(--font-size-lg);
		font-weight: 600;
		color: var(--color-accent);
	}

	.stat-label {
		font-size: var(--font-size-xs);
		color: var(--color-muted);
		text-transform: uppercase;
		letter-spacing: 0.08em;
	}

	.popup-detail {
		display: flex;
		flex-direction: column;
		gap: 8px;
		margin-bottom: var(--space-lg);
	}

	.detail-row {
		display: flex;
		justify-content: space-between;
		align-items: center;
		font-size: var(--font-size-sm);
	}

	.detail-label {
		color: var(--color-muted);
	}

	.detail-value {
		color: var(--color-text);
		font-weight: 500;
	}

	.spend-bar {
		height: 6px;
		border-radius: 3px;
		overflow: hidden;
		display: flex;
		background: var(--color-rep);
	}

	.bar-dem {
		height: 100%;
		background: var(--color-dem);
		transition: width var(--transition-base);
	}

	.bar-rep {
		flex: 1;
	}

	@media (max-width: 768px) {
		.vendor-popup {
			left: var(--space-md);
			right: var(--space-md);
			bottom: var(--space-md);
			width: auto;
		}
	}
</style>
