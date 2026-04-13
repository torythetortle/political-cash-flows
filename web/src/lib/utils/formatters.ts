export function formatDollars(value: number): string {
	if (value >= 1_000_000_000) {
		return `$${(value / 1_000_000_000).toFixed(1)}B`;
	}
	if (value >= 1_000_000) {
		return `$${(value / 1_000_000).toFixed(1)}M`;
	}
	if (value >= 1_000) {
		return `$${(value / 1_000).toFixed(0)}K`;
	}
	return `$${value.toLocaleString()}`;
}

export function formatDollarsLong(value: number): string {
	return `$${value.toLocaleString('en-US', { maximumFractionDigits: 0 })}`;
}

export function formatPercent(value: number): string {
	return `${value.toFixed(1)}%`;
}

export function formatCategory(category: string): string {
	return category
		.replace(/_/g, ' ')
		.toLowerCase()
		.replace(/\b\w/g, (c) => c.toUpperCase());
}
