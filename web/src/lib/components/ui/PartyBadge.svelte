<script lang="ts">
	import { partyColor } from '$lib/utils/colors';

	interface Props {
		party: 'DEM' | 'REP';
		size?: 'sm' | 'md';
	}

	let { party, size = 'sm' }: Props = $props();
	let label = $derived(party === 'DEM' ? 'Democrat' : 'Republican');
</script>

<span class="badge {size}" style:--party-color={partyColor(party)}>
	{label}
</span>

<style>
	.badge {
		display: inline-flex;
		align-items: center;
		font-family: var(--font-mono);
		font-weight: 500;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		background: color-mix(in srgb, var(--party-color) 15%, transparent);
		color: var(--party-color);
		border: 1px solid color-mix(in srgb, var(--party-color) 30%, transparent);
		border-radius: var(--radius-sm);
	}

	.sm {
		font-size: var(--font-size-xs);
		padding: 2px 6px;
	}

	.md {
		font-size: var(--font-size-sm);
		padding: 4px 10px;
	}
</style>
