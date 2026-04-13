<script lang="ts">
	import { base } from '$app/paths';
</script>

<footer>
	<div class="footer-inner">
		<span class="credit">By <strong>Tory Lysik</strong></span>
		<span class="sep">&middot;</span>
		<span class="source">Data: FEC 2024 cycle</span>
		<span class="sep">&middot;</span>
		<a href="{base}/methodology">Methodology</a>
	</div>
</footer>

<style>
	footer {
		border-top: 1px solid var(--color-border);
		padding: var(--space-md) var(--space-xl);
		background: var(--color-surface);
	}

	.footer-inner {
		max-width: var(--max-width);
		margin: 0 auto;
		display: flex;
		align-items: center;
		justify-content: center;
		gap: var(--space-sm);
		flex-wrap: wrap;
		font-size: var(--font-size-xs);
		color: var(--color-muted);
	}

	.sep {
		opacity: 0.4;
	}

	a {
		color: var(--color-muted);
		text-decoration: underline;
		text-underline-offset: 2px;
	}

	a:hover {
		color: var(--color-text);
	}
</style>
