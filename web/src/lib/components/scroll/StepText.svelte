<script lang="ts">
	import type { Snippet } from 'svelte';
	import type { StoryStep } from '$lib/data/types';
	import { inView } from '$lib/actions/inView';

	interface Props {
		step: StoryStep;
		onActivate?: (step: StoryStep) => void;
		children: Snippet;
	}

	let { step, onActivate, children }: Props = $props();
	let isActive = $state(false);

	function handleEnter() {
		isActive = true;
		onActivate?.(step);
	}

	function handleLeave() {
		isActive = false;
	}
</script>

<div
	class="step-text"
	class:active={isActive}
	use:inView={{ threshold: 0.6, rootMargin: '-10% 0px' }}
	oninview_enter={handleEnter}
	oninview_leave={handleLeave}
	data-step={step}
>
	{@render children()}
</div>

<style>
	.step-text {
		min-height: 60vh;
		display: flex;
		flex-direction: column;
		justify-content: center;
		padding: var(--space-xl) var(--space-lg);
		margin-bottom: var(--space-xl);
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-lg);
		opacity: 0.3;
		transition: opacity var(--transition-slow), border-color var(--transition-slow);
	}

	.step-text.active {
		opacity: 1;
		border-color: var(--color-accent-dim);
	}

	.step-text :global(h2) {
		font-size: var(--font-size-2xl);
		margin-bottom: var(--space-lg);
		color: var(--color-text);
	}

	.step-text :global(h3) {
		font-size: var(--font-size-xl);
		margin-bottom: var(--space-md);
		color: var(--color-text);
	}

	.step-text :global(p) {
		font-size: var(--font-size-base);
		line-height: var(--line-height-relaxed);
		color: var(--color-text-secondary);
		margin-bottom: var(--space-md);
	}

	.step-text :global(p:last-child) {
		margin-bottom: 0;
	}

	@media (max-width: 768px) {
		.step-text {
			min-height: 40vh;
			padding: var(--space-lg) var(--space-md);
		}
	}
</style>
