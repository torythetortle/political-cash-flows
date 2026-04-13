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

<Progress />
<Header />
<main>
	{@render children()}
</main>
<Footer />

<style>
	main {
		min-height: 100vh;
	}
</style>
