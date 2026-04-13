<script lang="ts">
	import type { Snippet } from 'svelte';

	interface Props {
		graphic: Snippet;
		steps: Snippet;
	}

	let { graphic, steps }: Props = $props();
</script>

<div class="scrolly-container">
	<div class="scrolly-graphic">
		<div class="graphic-inner">
			{@render graphic()}
		</div>
	</div>
	<div class="scrolly-steps">
		{@render steps()}
	</div>
</div>

<style>
	.scrolly-container {
		position: relative;
		display: flex;
		gap: 0;
	}

	.scrolly-graphic {
		position: sticky;
		top: 0;
		left: 0;
		width: 60%;
		height: 100vh;
		flex-shrink: 0;
		z-index: 1;
	}

	.graphic-inner {
		width: 100%;
		height: 100%;
		display: flex;
		align-items: center;
		justify-content: center;
		overflow: hidden;
	}

	.scrolly-steps {
		width: 40%;
		position: relative;
		z-index: 2;
		padding: var(--space-xl);
		padding-top: 50vh;
		padding-bottom: 50vh;
	}

	@media (max-width: 768px) {
		.scrolly-container {
			flex-direction: column;
		}

		.scrolly-graphic {
			width: 100%;
			height: 55vh;
		}

		.scrolly-steps {
			width: 100%;
			padding: var(--space-lg);
			padding-top: var(--space-xl);
			padding-bottom: 40vh;
		}
	}
</style>
