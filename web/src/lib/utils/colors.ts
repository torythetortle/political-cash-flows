export const COLORS = {
	dem: '#1B6ABF',
	demLight: '#4A8FD4',
	demDark: '#0F4A80',
	rep: '#C0392B',
	repLight: '#D4685B',
	repDark: '#8A2A1F',
	bg: '#F7F6F3',
	surface: '#FFFFFF',
	text: '#1A1A1A',
	muted: '#7A7A75',
	accent: '#8B6914',
	border: '#D4D4CE',
} as const;

export function partyColor(party: 'DEM' | 'REP' | string): string {
	if (party === 'DEM') return COLORS.dem;
	if (party === 'REP') return COLORS.rep;
	return COLORS.muted;
}

export function partyColorLight(party: 'DEM' | 'REP' | string): string {
	if (party === 'DEM') return COLORS.demLight;
	if (party === 'REP') return COLORS.repLight;
	return COLORS.muted;
}
