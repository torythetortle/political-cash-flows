<script lang="ts">
	import '../app.css';
	import favicon from '$lib/assets/favicon.svg';
	import Header from '$lib/components/layout/Header.svelte';
	import Progress from '$lib/components/layout/Progress.svelte';
	import Footer from '$lib/components/layout/Footer.svelte';
	let { children } = $props();
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
	<title>The Last Mile of Political Money</title>
	<meta name="description" content="Where political dollars actually land at the street level. An investigation using FEC disbursement data." />
</svelte:head>

<a href="#main-content" class="skip-link">Skip to content</a>
<Progress />
<Header />
<main id="main-content">
	{@render children()}
</main>
<Footer />

<style>
	main {
		min-height: 100vh;
	}

	.skip-link {
		position: absolute;
		top: -100%;
		left: 0;
		background: var(--color-accent);
		color: var(--color-bg);
		padding: 8px 16px;
		font-family: var(--font-mono);
		font-size: var(--font-size-sm);
		z-index: 200;
		text-decoration: none;
	}

	.skip-link:focus {
		top: 0;
	}
</style>
