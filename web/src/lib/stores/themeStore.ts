import { writable } from 'svelte/store';
import { browser } from '$app/environment';

function getInitialTheme(): 'dark' | 'light' {
	if (!browser) return 'dark';
	const stored = localStorage.getItem('theme');
	if (stored === 'light' || stored === 'dark') return stored;
	return 'dark';
}

export const theme = writable<'dark' | 'light'>(getInitialTheme());

if (browser) {
	theme.subscribe((value) => {
		localStorage.setItem('theme', value);
		document.documentElement.setAttribute('data-theme', value);
	});
}
