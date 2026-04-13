<script lang="ts">
	interface Props {
		value: string;
		label: string;
		color?: string;
	}

	let { value, label, color = 'var(--color-accent)' }: Props = $props();
</script>

<div class="data-callout">
	<span class="value" style:color>{value}</span>
	<span class="label">{label}</span>
</div>

<style>
	.data-callout {
		display: flex;
		flex-direction: column;
		gap: var(--space-xs);
	}

	.value {
		font-family: var(--font-mono);
		font-size: var(--font-size-display);
		font-weight: 700;
		line-height: 1;
		letter-spacing: -0.03em;
	}

	.label {
		font-size: var(--font-size-sm);
		color: var(--color-text-secondary);
		text-transform: uppercase;
		letter-spacing: 0.08em;
		font-weight: 500;
	}
</style>
