<script lang="ts">
	import { base } from '$app/paths';
	let scrollY = $state(0);
	let showBg = $derived(scrollY > 80);
</script>

<svelte:window bind:scrollY />

<header class:scrolled={showBg}>
	<div class="header-inner">
		<span class="wordmark">
			<span class="accent">$</span> Political Cash Flows
		</span>
		<nav aria-label="Site navigation">
			<a href="{base}/methodology">Methodology</a>
		</nav>
	</div>
</header>

<style>
	header {
		position: fixed;
		top: 0;
		left: 0;
		right: 0;
		z-index: 100;
		padding: var(--space-md) var(--space-xl);
		transition: background var(--transition-base), border-color var(--transition-base);
		border-bottom: 1px solid transparent;
	}

	header.scrolled {
		background: color-mix(in srgb, var(--color-bg) 92%, transparent);
		backdrop-filter: blur(12px);
		-webkit-backdrop-filter: blur(12px);
		border-bottom-color: var(--color-border);
	}

	.header-inner {
		max-width: var(--max-width);
		margin: 0 auto;
		display: flex;
		align-items: center;
		justify-content: space-between;
	}

	.wordmark {
		font-family: var(--font-mono);
		font-size: var(--font-size-sm);
		font-weight: 500;
		color: var(--color-text-secondary);
		letter-spacing: 0.02em;
	}

	.accent {
		color: var(--color-accent);
	}

	nav a {
		font-size: var(--font-size-xs);
		color: var(--color-muted);
		text-transform: uppercase;
		letter-spacing: 0.1em;
		font-weight: 500;
	}

	nav a:hover {
		color: var(--color-text);
	}

	@media (max-width: 768px) {
		header {
			padding: var(--space-sm) var(--space-md);
		}
	}
</style>
