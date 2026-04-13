<script lang="ts">
	import { base } from '$app/paths';
</script>

<article class="methodology">
	<header class="meth-header">
		<a href="{base}/" class="back-link">&larr; Back to story</a>
		<h1>Methodology</h1>
		<p class="subtitle">
			How I collected, cleaned, and mapped FEC disbursement data
			to trace the last mile of political money.
		</p>
	</header>

	<section>
		<h2>Overview</h2>
		<p>
			This project traces political spending from its source &mdash; committees registered
			with the Federal Election Commission &mdash; to its destination: the specific vendors
			that receive the money. Most campaign finance reporting focuses on contributions (who
			gives). This project focuses on disbursements (who gets paid, and where they are).
		</p>
		<p>
			The analysis covers three complete election cycles: <strong>2020, 2022, and 2024</strong>,
			comprising approximately <strong>4.8 million itemized expenditure records</strong>
			filed by political committees of both major parties.
		</p>
	</section>

	<section>
		<h2>Data Sources</h2>
		<p>
			All financial data comes from the Federal Election Commission's bulk data downloads,
			which are pipe-delimited flat files updated nightly and available for public download
			at <a href="https://www.fec.gov/data/browse-data/?tab=bulk-data">fec.gov/data</a>.
		</p>

		<h3>Files used</h3>
		<dl>
			<dt>Operating Expenditures (oppexp)</dt>
			<dd>
				The primary dataset. Each record represents an itemized payment from a political
				committee to a vendor, including the payee name, city, state, ZIP code, dollar amount,
				date, and a free-text purpose description. Files used:
				<span class="mono">oppexp20.zip</span>,
				<span class="mono">oppexp22.zip</span>,
				<span class="mono">oppexp24.zip</span>
			</dd>

			<dt>Committee Master File (cm)</dt>
			<dd>
				Links each committee ID to a committee name, party affiliation, and connected
				candidate ID (if applicable). This is how we determine whether a payment came from
				a Democratic or Republican committee, and which candidate it supports.
				<span class="mono">cm20.zip</span>,
				<span class="mono">cm22.zip</span>,
				<span class="mono">cm24.zip</span>
			</dd>

			<dt>Candidate Master File (cn)</dt>
			<dd>
				Maps candidate IDs to candidate names, office sought (House, Senate, or President),
				state, and district. This allows us to link vendor payments through committees
				to specific races.
				<span class="mono">cn20.zip</span>,
				<span class="mono">cn22.zip</span>,
				<span class="mono">cn24.zip</span>
			</dd>
		</dl>

		<h3>What's not included</h3>
		<p>
			This analysis does not currently include independent expenditures (super PAC spending)
			or individual contributions. Independent expenditures are filed separately and use a
			different schema. Adding them is a planned future enhancement.
		</p>
	</section>

	<section>
		<h2>Data Pipeline</h2>
		<p>
			The raw FEC files go through a five-step pipeline before they reach the frontend.
			The full pipeline is written in Python and is available in the project repository.
		</p>

		<h3>Step 1: Download</h3>
		<p>
			Bulk files are downloaded programmatically from the FEC's S3-hosted archive using
			<code>httpx</code> with streaming and progress bars. Files that already exist locally
			are skipped. Total download size across three cycles is approximately 200MB compressed.
		</p>

		<h3>Step 2: Parse &amp; Merge</h3>
		<p>
			FEC bulk files are pipe-delimited with no headers. Column positions are mapped using
			the FEC's published data dictionaries. After parsing, each expenditure record is
			merged with the committee master file to attach party affiliation and candidate ID,
			then with the candidate master file to attach candidate name and office.
		</p>
		<p>
			Records are filtered to the two major parties (DEM/DFL and REP). Negative amounts
			(refunds) and records with missing vendor names or addresses are dropped.
		</p>
		<p>
			Each record also gets a <strong>purpose category</strong> derived from the free-text
			purpose field. We map keywords like "MEDIA", "DIRECT MAIL", "CONSULTING", "POLLING",
			"TRAVEL", etc. to standardized categories. Records that don't match any keyword are
			categorized as "Other".
		</p>

		<h3>Step 3: Vendor Name Deduplication</h3>
		<p>
			The same vendor frequently appears under multiple name variations in FEC filings.
			For example:
		</p>
		<div class="example-box">
			<code>GMMB INC</code>
			<code>GMMB, INC.</code>
			<code>GMMB</code>
			<code>GMMB INC.</code>
		</div>
		<p>
			We use a two-phase approach:
		</p>
		<ol>
			<li>
				<strong>Normalization:</strong> Strip common suffixes (INC, LLC, CORP),
				remove punctuation, collapse whitespace, and uppercase everything.
			</li>
			<li>
				<strong>Blocking + fuzzy matching:</strong> Rather than comparing all ~290,000
				unique vendor names against each other (O(n&sup2;)), we group names by the first
				five characters of their first significant word, then fuzzy-match only within
				each block. We use <code>rapidfuzz</code>'s <code>token_sort_ratio</code> scorer,
				which handles word reordering ("SMITH CONSULTING" vs "CONSULTING SMITH").
				Matches above 85% similarity are automatically merged. The canonical name is the
				variant with the highest total spend.
			</li>
		</ol>
		<p>
			Across three cycles, this process merged approximately 40,000 name variants
			into ~250,000 unique vendor identities. The blocking strategy reduced the
			deduplication runtime from over an hour to under 10 seconds.
		</p>

		<h3>Step 4: Geocoding</h3>
		<p>
			FEC expenditure records include the vendor's city, state, and ZIP code, but not
			a street address. We geocode vendor locations using <strong>ZIP code centroids</strong>
			from a public dataset of U.S. ZIP code coordinates. Each vendor is placed at the
			centroid of its ZIP code, with small random jitter applied to prevent exact overlaps.
		</p>
		<p>
			This provides city-level accuracy, which is sufficient for the clustering analysis
			this project presents. Approximately <strong>87% of records</strong> are successfully
			geocoded; the remaining 13% have invalid or non-standard ZIP codes and are excluded
			from the map but included in aggregate spending totals.
		</p>

		<h3>Step 5: Aggregation &amp; Export</h3>
		<p>
			The geocoded data is aggregated into several output files consumed by the frontend:
		</p>
		<ul>
			<li><strong>Vendor map (GeoJSON):</strong> One point per unique vendor, with total spend,
				party split, purpose category, and active cycles. Vendors below $1,000 total spend
				are excluded to keep the file manageable (~155,000 features).</li>
			<li><strong>State spend (JSON):</strong> Total DEM/REP spending per state.</li>
			<li><strong>Top vendors (JSON):</strong> Top 50 vendors ranked by total spend with
				enriched metadata.</li>
			<li><strong>Vendor cycles (JSON):</strong> Cycle-over-cycle spending for the top 30
				repeat vendors.</li>
			<li><strong>Vendor details (JSON):</strong> For the top 500 vendors: monthly spending
				timeline, purpose breakdown, top 10 paying committees, and linked candidates.</li>
		</ul>
	</section>

	<section>
		<h2>Frontend</h2>
		<p>
			The interactive is built with <strong>SvelteKit</strong> using the static adapter,
			meaning the final output is a fully self-contained static site with no backend server.
			All data is loaded from pre-built JSON and GeoJSON files at page load.
		</p>
		<ul>
			<li><strong>Maps:</strong> MapLibre GL JS with CARTO Positron tiles (no API key required)</li>
			<li><strong>Charts:</strong> D3.js for the choropleth, treemap, and cycle timeline</li>
			<li><strong>Scroll:</strong> Custom Intersection Observer action (no Scrollama dependency)</li>
			<li><strong>Clustering:</strong> MapLibre's built-in GeoJSON clustering for performant
				rendering of 155K+ vendor points</li>
		</ul>
	</section>

	<section>
		<h2>Limitations &amp; Caveats</h2>
		<ul class="limitations">
			<li>
				<strong>Address ≠ work location.</strong> Vendor locations reflect mailing addresses
				(derived from ZIP codes), not where the work is performed. A D.C.-based consulting
				firm may produce ads that run in swing states. The map shows where the money is
				<em>sent</em>, not necessarily where its effects are <em>felt</em>.
			</li>
			<li>
				<strong>ZIP centroid accuracy.</strong> Vendors are placed at the centroid of their
				ZIP code, not at their actual street address. In dense urban areas, this is accurate
				within a few blocks. In rural areas, it may be off by miles.
			</li>
			<li>
				<strong>Name matching is imperfect.</strong> Fuzzy deduplication may over-merge
				distinct vendors with similar names (e.g., two different "Smith Consulting" firms)
				or fail to merge vendors with very different naming conventions. We use a conservative
				85% threshold to minimize false merges.
			</li>
			<li>
				<strong>Party attribution is by committee, not vendor.</strong> A vendor coded as
				"DEM" received money from Democratic-affiliated committees. Many vendors work for
				both parties, and their dot color reflects whichever party paid them more.
			</li>
			<li>
				<strong>Purpose categorization is keyword-based.</strong> The FEC purpose field is
				free text entered by filers with no controlled vocabulary. Our keyword mapping
				captures common patterns but may miscategorize atypical descriptions. Records that
				don't match any keyword default to "Other."
			</li>
			<li>
				<strong>No independent expenditures.</strong> This analysis currently covers only
				operating expenditures (direct committee spending). Super PAC independent expenditures,
				which represent a significant share of total political spending, are not yet included.
			</li>
		</ul>
	</section>

	<section>
		<h2>Tools &amp; Technologies</h2>
		<div class="tech-grid">
			<div class="tech-item">
				<span class="tech-label">Data pipeline</span>
				<span class="tech-value">Python 3.11+, pandas, rapidfuzz, httpx, pyarrow</span>
			</div>
			<div class="tech-item">
				<span class="tech-label">Frontend</span>
				<span class="tech-value">SvelteKit 2, Svelte 5, TypeScript</span>
			</div>
			<div class="tech-item">
				<span class="tech-label">Visualization</span>
				<span class="tech-value">D3.js v7, MapLibre GL JS v5</span>
			</div>
			<div class="tech-item">
				<span class="tech-label">Map tiles</span>
				<span class="tech-value">CARTO Positron (no-labels)</span>
			</div>
			<div class="tech-item">
				<span class="tech-label">Geocoding</span>
				<span class="tech-value">ZIP code centroids (U.S. Census)</span>
			</div>
			<div class="tech-item">
				<span class="tech-label">Boundary data</span>
				<span class="tech-value">US Atlas TopoJSON</span>
			</div>
		</div>
	</section>

	<section>
		<h2>Reproducibility</h2>
		<p>
			The full data pipeline is open source. To reproduce from scratch:
		</p>
		<pre><code>git clone [repo-url]
cd political-cash-flows/pipeline
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m pipeline.src.run_pipeline</code></pre>
		<p>
			This will download all FEC bulk files (~200MB compressed), parse ~4.8M records,
			deduplicate vendor names, geocode locations, and export the final datasets.
			The full pipeline takes approximately 5&ndash;10 minutes depending on your
			internet connection.
		</p>
	</section>

	<section>
		<h2>How to Cite</h2>
		<p>
			If you reference this project in your own reporting, research, or analysis,
			please cite it as:
		</p>
		<div class="cite-box">
			<p class="cite-text">
				Lysik, Tory. "The Last Mile of Political Money." 2026.
				<span class="mono">torythetortle.github.io/political-cash-flows</span>
			</p>
		</div>
		<p>
			BibTeX:
		</p>
		<pre><code>@misc{'{'} lysik2026lastmile,
  author = {'{'} Lysik, Tory {'}'},
  title = {'{'} The Last Mile of Political Money {'}'},
  year = {'{'} 2026 {'}'},
  url = {'{'} https://torythetortle.github.io/political-cash-flows {'}'}
{'}'}</code></pre>
	</section>

	<section>
		<h2>License</h2>
		<p>
			The code for this project is released under the
			<a href="https://github.com/torythetortle/political-cash-flows/blob/main/LICENSE">MIT License</a>.
			The underlying data is public, sourced from the Federal Election Commission.
		</p>
	</section>

	<section class="contact-section">
		<h2>Get the Data</h2>
		<p>
			The processed datasets used in this project are available for journalistic
			and research purposes. If you're a reporter, researcher, or newsroom that
			would like access to the full dataset &mdash; including the geocoded vendor
			database, deduplication mapping, and committee-candidate linkage tables &mdash;
			please get in touch.
		</p>
		<div class="contact-box">
			<p class="contact-label">For data requests or questions about this project:</p>
			<a href="mailto:lysiktory@gmail.com" class="contact-link">lysiktory@gmail.com</a>
			<p class="contact-note">
				Please include your name, affiliation, and a brief description of
				how you plan to use the data.
			</p>
		</div>
	</section>
</article>

<style>
	.methodology {
		max-width: var(--text-width);
		margin: 0 auto;
		padding: var(--space-4xl) var(--space-xl) var(--space-3xl);
	}

	.meth-header {
		margin-bottom: var(--space-3xl);
	}

	.back-link {
		font-family: var(--font-mono);
		font-size: var(--font-size-xs);
		color: var(--color-muted);
		text-transform: uppercase;
		letter-spacing: 0.08em;
		display: inline-block;
		margin-bottom: var(--space-lg);
	}

	.back-link:hover {
		color: var(--color-accent);
	}

	.meth-header h1 {
		font-size: var(--font-size-3xl);
		margin-bottom: var(--space-lg);
	}

	.subtitle {
		font-size: var(--font-size-lg);
		color: var(--color-text-secondary);
		line-height: var(--line-height-relaxed);
	}

	section {
		margin-bottom: var(--space-3xl);
	}

	h2 {
		font-size: var(--font-size-xl);
		margin-bottom: var(--space-lg);
		padding-bottom: var(--space-sm);
		border-bottom: 1px solid var(--color-border);
	}

	h3 {
		font-size: var(--font-size-base);
		font-weight: 600;
		margin-top: var(--space-xl);
		margin-bottom: var(--space-sm);
		color: var(--color-text);
	}

	p {
		color: var(--color-text-secondary);
		line-height: var(--line-height-relaxed);
		margin-bottom: var(--space-md);
	}

	dl {
		margin: var(--space-lg) 0;
	}

	dt {
		font-weight: 600;
		color: var(--color-text);
		margin-top: var(--space-md);
	}

	dd {
		color: var(--color-text-secondary);
		margin-left: 0;
		padding-left: var(--space-lg);
		border-left: 2px solid var(--color-border);
		margin-top: var(--space-xs);
		margin-bottom: var(--space-md);
		line-height: var(--line-height-relaxed);
	}

	ol, ul {
		padding-left: var(--space-lg);
		color: var(--color-text-secondary);
		line-height: var(--line-height-relaxed);
	}

	li {
		margin-bottom: var(--space-sm);
	}

	.limitations li {
		margin-bottom: var(--space-md);
	}

	.example-box {
		display: flex;
		flex-wrap: wrap;
		gap: var(--space-sm);
		padding: var(--space-md);
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-md);
		margin: var(--space-md) 0;
	}

	.example-box code {
		padding: 3px 8px;
		background: var(--color-surface-raised);
		border-radius: var(--radius-sm);
		font-size: var(--font-size-sm);
		color: var(--color-accent);
	}

	code {
		font-family: var(--font-mono);
		font-size: var(--font-size-sm);
		color: var(--color-accent);
	}

	pre {
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-md);
		padding: var(--space-lg);
		overflow-x: auto;
		margin: var(--space-md) 0;
	}

	pre code {
		color: var(--color-text);
	}

	.tech-grid {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: var(--space-sm);
		margin-top: var(--space-md);
	}

	.tech-item {
		display: flex;
		flex-direction: column;
		gap: 2px;
		padding: var(--space-md);
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-md);
	}

	.tech-label {
		font-size: var(--font-size-xs);
		color: var(--color-muted);
		text-transform: uppercase;
		letter-spacing: 0.06em;
	}

	.tech-value {
		font-size: var(--font-size-sm);
		color: var(--color-text);
	}

	.cite-box {
		padding: var(--space-lg);
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-md);
		margin: var(--space-md) 0;
	}

	.cite-text {
		font-size: var(--font-size-sm);
		color: var(--color-text);
		line-height: var(--line-height-relaxed);
	}

	.contact-section {
		margin-bottom: var(--space-2xl);
	}

	.contact-box {
		margin-top: var(--space-lg);
		padding: var(--space-xl);
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-lg);
		text-align: center;
	}

	.contact-label {
		font-size: var(--font-size-sm);
		color: var(--color-muted);
		margin-bottom: var(--space-md);
	}

	.contact-link {
		display: inline-block;
		font-family: var(--font-mono);
		font-size: var(--font-size-lg);
		font-weight: 600;
		color: var(--color-accent);
		padding: var(--space-sm) var(--space-xl);
		border: 1px solid var(--color-accent);
		border-radius: var(--radius-md);
		transition: all var(--transition-base);
	}

	.contact-link:hover {
		background: var(--color-accent);
		color: var(--color-bg);
	}

	.contact-note {
		margin-top: var(--space-md);
		font-size: var(--font-size-xs);
		color: var(--color-muted);
		font-style: italic;
	}

	@media (max-width: 768px) {
		.methodology {
			padding: var(--space-2xl) var(--space-lg);
		}

		.tech-grid {
			grid-template-columns: 1fr;
		}
	}
</style>
