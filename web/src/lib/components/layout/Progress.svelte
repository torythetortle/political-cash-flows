<script lang="ts">
	let scrollY = $state(0);
	let docHeight = $state(1);
	let winHeight = $state(1);

	let progress = $derived(
		Math.min(1, Math.max(0, scrollY / (docHeight - winHeight)))
	);

	function updateHeight() {
		docHeight = document.documentElement.scrollHeight;
		winHeight = window.innerHeight;
	}
</script>

<svelte:window bind:scrollY bind:innerHeight={winHeight} onresize={updateHeight} onload={updateHeight} />

<div class="progress-bar" style:--progress={progress}>
	<div class="progress-fill"></div>
</div>

<style>
	.progress-bar {
		position: fixed;
		top: 0;
		left: 0;
		right: 0;
		height: 3px;
		z-index: 101;
		background: transparent;
	}

	.progress-fill {
		height: 100%;
		width: calc(var(--progress) * 100%);
		background: linear-gradient(90deg, var(--color-dem), var(--color-accent), var(--color-rep));
		transition: width 50ms linear;
	}
</style>
