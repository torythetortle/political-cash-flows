<script lang="ts">
	import type { StoryStep } from '$lib/data/types';
	import { mapFlyTarget } from '$lib/stores/mapStore';
	import { activeSection } from '$lib/stores/scrollStore';
	import { formatDollars } from '$lib/utils/formatters';

	import ScrollyContainer from '$lib/components/scroll/ScrollyContainer.svelte';
	import StepText from '$lib/components/scroll/StepText.svelte';
	import ChoroplethMap from '$lib/components/charts/ChoroplethMap.svelte';
	import VendorMap from '$lib/components/map/VendorMap.svelte';
	import VendorPopup from '$lib/components/map/VendorPopup.svelte';
	import MapLegend from '$lib/components/map/MapLegend.svelte';
	import VendorTreemap from '$lib/components/charts/VendorTreemap.svelte';
	import CycleTimeline from '$lib/components/charts/CycleTimeline.svelte';
	import DataCallout from '$lib/components/ui/DataCallout.svelte';
	import Explorer from '$lib/components/explorer/Explorer.svelte';

	let { data } = $props();

	let activeStep = $state<StoryStep>('intro');

	const SWING_STATES = ['PA', 'MI', 'WI', 'AZ', 'NV', 'GA'];

	let showChoropleth = $derived(
		['national-spend', 'swing-states'].includes(activeStep)
	);
	let showMap = $derived(
		['zoom-philadelphia', 'vendor-clusters', 'explore'].includes(activeStep)
	);
	let showTreemap = $derived(activeStep === 'concentration');
	let showTimeline = $derived(activeStep === 'repeat-players');
	let highlightStates = $derived(
		activeStep === 'swing-states' ? SWING_STATES : []
	);
	let mapInteractive = $derived(activeStep === 'explore');

	function handleStep(step: StoryStep) {
		activeStep = step;
		activeSection.set(step);

		if (step === 'zoom-philadelphia' || step === 'vendor-clusters' || step === 'explore') {
			mapFlyTarget.set({ center: [-75.1652, 39.9526], zoom: 12.5 });
		}
	}
</script>

<!-- Hero -->
<section class="hero">
	<div class="hero-inner">
		<h1>The Last Mile of<br /> Political Money</h1>
		<p class="hero-dek">
			We know where campaign money comes from. But what does it actually
			buy at the street level? This is an attempt to find out.
		</p>
		<nav class="hero-nav">
			<a href="#story-start" class="nav-btn nav-story">
				<span class="nav-icon">&darr;</span>
				Read the story
			</a>
			<a href="#explore" class="nav-btn nav-explore">
				<span class="nav-icon">&rarr;</span>
				Explore the data
			</a>
		</nav>
	</div>
</section>

<!-- Intro prose -->
<section class="prose-section" id="story-start">
	<div class="prose-inner">
		<p>
			FEC disbursement data tells you not just that a super PAC spent millions in Philadelphia
			&mdash; it tells you the vendor, the vendor's address, and the expenditure type.
		</p>
		<p>
			That means you can map the actual physical footprint of a political campaign in a city:
			which production studios cut the ads, which direct mail houses printed the flyers,
			which local TV stations cashed the checks, which data firms in which office parks
			modeled the voter files.
		</p>
	</div>
</section>

<!-- Scrollytelling -->
<ScrollyContainer>
	{#snippet graphic()}
		<div class="graphic-stack">
			{#if showChoropleth}
				<div class="graphic-layer" class:active={showChoropleth}>
					<ChoroplethMap
						stateSpend={data.stateSpend}
						{highlightStates}
						visible={showChoropleth}
					/>
				</div>
			{/if}

			{#if showMap}
				<div class="graphic-layer" class:active={showMap}>
					<VendorMap
						vendors={data.vendors}
						visible={showMap}
						interactive={mapInteractive}
					/>
					{#if showMap}
						<MapLegend />
					{/if}
				</div>
			{/if}

			{#if showTreemap}
				<div class="graphic-layer treemap-layer" class:active={showTreemap}>
					<div class="chart-pad">
						<h3 class="graphic-title">Top 20 Vendors by Total Spend</h3>
						<VendorTreemap vendors={data.topVendors} visible={showTreemap} />
					</div>
				</div>
			{/if}

			{#if showTimeline}
				<div class="graphic-layer timeline-layer" class:active={showTimeline}>
					<div class="chart-pad">
						<h3 class="graphic-title">Repeat Players: Same Vendors, Every Cycle</h3>
						<CycleTimeline vendorCycles={data.vendorCycles} visible={showTimeline} />
					</div>
				</div>
			{/if}

			{#if activeStep === 'philadelphia-intro'}
				<div class="graphic-layer callout-layer" class:active={true}>
					<div class="big-callout">
						<DataCallout
							value={formatDollars(data.phillySpend)}
							label="spent through Philadelphia vendors, 2024 cycle"
						/>
					</div>
				</div>
			{/if}

			{#if activeStep === 'intro' || activeStep === 'methodology'}
				<div class="graphic-layer intro-layer" class:active={true}>
					<div class="intro-graphic">
						<span class="dollar-sign">$</span>
					</div>
				</div>
			{/if}
		</div>
	{/snippet}

	{#snippet steps()}
		<StepText step="intro" onActivate={handleStep}>
			<h2>Follow the money. All the way down.</h2>
			<p>
				In the 2024 election cycle, political committees reported
				<strong class="text-accent">{formatDollars(data.totalSpend)}</strong>
				in spending to the Federal Election Commission.
			</p>
			<p>
				We traced every dollar to the vendor that received it &mdash; and mapped where
				those vendors actually sit.
			</p>
		</StepText>

		<StepText step="national-spend" onActivate={handleStep}>
			<h2>The national picture</h2>
			<p>
				Political spending is not evenly distributed. Some states attract enormous
				sums while others are virtually ignored. The map shows total disbursements
				by state &mdash; a combination of Democratic and Republican spending.
			</p>
			<p>
				Hover over any state to see the breakdown.
			</p>
		</StepText>

		<StepText step="swing-states" onActivate={handleStep}>
			<h2>Battleground concentration</h2>
			<p>
				Six states dominate: <strong>Pennsylvania, Michigan, Wisconsin,
				Arizona, Nevada,</strong> and <strong>Georgia</strong>. These battlegrounds
				absorb a disproportionate share of the national spending total.
			</p>
			<p>
				But this map still only tells you <em>where money goes</em>.
				It doesn't tell you <em>who catches it</em>.
			</p>
		</StepText>

		<StepText step="philadelphia-intro" onActivate={handleStep}>
			<h2>Philadelphia: A case study</h2>
			<p>
				Philadelphia is one of the most intensely targeted cities in American politics.
				Let's see exactly where the money lands.
			</p>
		</StepText>

		<StepText step="zoom-philadelphia" onActivate={handleStep}>
			<h2>Street-level view</h2>
			<p>
				Each dot on this map is a political vendor &mdash; a firm that received money
				from a political committee. The size of the dot reflects how much they received.
				The color shows which party's committees paid them.
			</p>
			<p class="text-dem">Blue = Democratic spending</p>
			<p class="text-rep">Red = Republican spending</p>
		</StepText>

		<StepText step="vendor-clusters" onActivate={handleStep}>
			<h2>The clustering is not random</h2>
			<p>
				Notice how the dots cluster tightly. A significant share of all political
				spending in this city flows to vendors within a few blocks of each other.
			</p>
			<p>
				These are the media buyers, direct mail houses, consulting firms, and data
				analytics operations that form the backbone of modern campaigns.
			</p>
		</StepText>

		<StepText step="explore" onActivate={handleStep}>
			<h3>Explore the vendors</h3>
			<p>
				Click any dot on the map to see who they are, how much they received,
				and which party's money they handle. Use the filters in the legend to
				isolate Democratic or Republican vendors.
			</p>
		</StepText>

		<StepText step="concentration" onActivate={handleStep}>
			<h2>Market concentration</h2>
			<p>
				The political vendor ecosystem is remarkably concentrated. The top 20
				firms capture an outsized share of all spending. Each block in this
				treemap is sized by total dollars received.
			</p>
			<p>
				A handful of firms &mdash; many of them based in Washington, D.C. &mdash;
				quietly process enormous volumes of campaign spending.
			</p>
		</StepText>

		<StepText step="repeat-players" onActivate={handleStep}>
			<h2>The repeat players</h2>
			<p>
				The same vendors appear cycle after cycle. This timeline shows spending for
				the top recurring vendors across the last five election cycles. Larger circles
				mean more money.
			</p>
			<p>
				The political-industrial complex is not just large &mdash; it's stable.
				The same firms profit from every election, regardless of which party wins.
			</p>
		</StepText>

		<StepText step="methodology" onActivate={handleStep}>
			<h2>Explore it yourself</h2>
			<p>
				Below this story is a full interactive explorer. Search for any vendor,
				filter by party or state, jump to any city, and click into individual
				vendor profiles.
			</p>
			<p>
				<a href="#explore">Jump to explorer &darr;</a>
				&nbsp;&middot;&nbsp;
				<a href="/methodology">Read the methodology &rarr;</a>
			</p>
		</StepText>
	{/snippet}
</ScrollyContainer>

<VendorPopup />

<!-- Interactive Explorer -->
<Explorer vendors={data.vendors} stateSpend={data.stateSpend} vendorDetails={data.vendorDetails} />

<style>
	.hero {
		min-height: 100vh;
		display: flex;
		align-items: center;
		justify-content: center;
		padding: var(--space-xl);
		position: relative;
	}

	.hero-inner {
		max-width: var(--text-width);
		text-align: center;
	}


	.hero h1 {
		margin-bottom: var(--space-xl);
		background: linear-gradient(
			135deg,
			var(--color-text) 0%,
			var(--color-text-secondary) 100%
		);
		-webkit-background-clip: text;
		-webkit-text-fill-color: transparent;
		background-clip: text;
	}

	.hero-dek {
		font-size: var(--font-size-lg);
		color: var(--color-text-secondary);
		line-height: var(--line-height-relaxed);
		max-width: 520px;
		margin: 0 auto;
	}

	.hero-nav {
		display: flex;
		gap: var(--space-md);
		margin-top: var(--space-2xl);
		justify-content: center;
	}

	.nav-btn {
		display: inline-flex;
		align-items: center;
		gap: var(--space-sm);
		padding: 12px 24px;
		border: 1px solid var(--color-border);
		border-radius: var(--radius-md);
		font-family: var(--font-mono);
		font-size: var(--font-size-sm);
		font-weight: 500;
		text-decoration: none;
		transition: all var(--transition-base);
		letter-spacing: 0.02em;
	}

	.nav-story {
		color: var(--color-text-secondary);
		background: transparent;
	}

	.nav-story:hover {
		color: var(--color-text);
		border-color: var(--color-text-secondary);
	}

	.nav-explore {
		color: var(--color-bg);
		background: var(--color-accent);
		border-color: var(--color-accent);
	}

	.nav-explore:hover {
		background: var(--color-text);
		border-color: var(--color-text);
	}

	.nav-icon {
		font-size: var(--font-size-base);
		line-height: 1;
	}

	.prose-section {
		padding: var(--space-4xl) var(--space-xl);
		display: flex;
		justify-content: center;
	}

	.prose-inner {
		max-width: var(--text-width);
	}

	.prose-inner p {
		font-size: var(--font-size-lg);
		color: var(--color-text-secondary);
		line-height: var(--line-height-relaxed);
		margin-bottom: var(--space-lg);
	}

	.graphic-stack {
		width: 100%;
		height: 100%;
		position: relative;
	}

	.graphic-layer {
		position: absolute;
		inset: 0;
		opacity: 0;
		transition: opacity 0.5s ease;
		pointer-events: none;
	}

	.graphic-layer.active {
		opacity: 1;
		pointer-events: auto;
	}

	.treemap-layer,
	.timeline-layer {
		display: flex;
		align-items: center;
		justify-content: center;
		background: var(--color-bg);
	}

	.chart-pad {
		width: 90%;
		max-width: 700px;
	}

	.graphic-title {
		font-size: var(--font-size-lg);
		color: var(--color-text);
		margin-bottom: var(--space-lg);
		font-weight: 600;
	}

	.callout-layer {
		display: flex;
		align-items: center;
		justify-content: center;
		background: var(--color-bg);
	}

	.big-callout {
		text-align: center;
	}

	.intro-layer {
		display: flex;
		align-items: center;
		justify-content: center;
		background: var(--color-bg);
	}

	.intro-graphic {
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.dollar-sign {
		font-family: var(--font-mono);
		font-size: clamp(8rem, 20vw, 16rem);
		font-weight: 700;
		color: var(--color-accent);
		opacity: 0.08;
		user-select: none;
	}

	@media (max-width: 768px) {
		.hero {
			min-height: 80vh;
			padding: var(--space-lg);
		}

		.hero h1 {
			font-size: var(--font-size-3xl);
		}

		.hero-nav {
			flex-direction: column;
			gap: var(--space-sm);
		}

		.nav-btn {
			width: 100%;
			justify-content: center;
		}

		.prose-section {
			padding: var(--space-2xl) var(--space-lg);
		}
	}
</style>
