import unifiedData from '$lib/data/unified.json';

/** @type {import('./$types').PageLoad} */
export function load() {
	return {
		scraped_at: unifiedData.scraped_at,
		discounts: unifiedData.discounts || []
	};
}
