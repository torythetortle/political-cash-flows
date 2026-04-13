import { writable } from 'svelte/store';
import type { StoryStep } from '$lib/data/types';

export const activeSection = writable<StoryStep>('intro');
export const scrollProgress = writable<number>(0);
