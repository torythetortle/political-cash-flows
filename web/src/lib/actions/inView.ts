export interface InViewParams {
	threshold?: number;
	rootMargin?: string;
	once?: boolean;
}

export function inView(node: HTMLElement, params: InViewParams = {}) {
	const { threshold = 0.5, rootMargin = '0px', once = false } = params;
	let hasEntered = false;

	const observer = new IntersectionObserver(
		(entries) => {
			for (const entry of entries) {
				if (entry.isIntersecting) {
					if (once && hasEntered) return;
					hasEntered = true;
					node.dispatchEvent(new CustomEvent('inview_enter', { detail: entry }));
				} else {
					node.dispatchEvent(new CustomEvent('inview_leave', { detail: entry }));
				}
			}
		},
		{ threshold, rootMargin }
	);

	observer.observe(node);

	return {
		destroy() {
			observer.disconnect();
		},
		update(newParams: InViewParams) {
			observer.disconnect();
			const obs = new IntersectionObserver(
				(entries) => {
					for (const entry of entries) {
						if (entry.isIntersecting) {
							node.dispatchEvent(new CustomEvent('inview_enter', { detail: entry }));
						} else {
							node.dispatchEvent(new CustomEvent('inview_leave', { detail: entry }));
						}
					}
				},
				{
					threshold: newParams.threshold ?? threshold,
					rootMargin: newParams.rootMargin ?? rootMargin
				}
			);
			obs.observe(node);
		}
	};
}
