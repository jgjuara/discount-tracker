import unifiedData from '$lib/data/unified.json';

/** @type {import('./$types').EntryGenerator} */
export function entries() {
	return (unifiedData.discounts || []).map(d => ({
		bank: d.bank.toLowerCase(),
		id: d.id
	}));
}

/** @type {import('./$types').PageLoad} */
export function load({ params }) {
	const discount = (unifiedData.discounts || []).find(
		d => d.bank.toLowerCase() === params.bank.toLowerCase() && d.id === params.id
	);

	return { discount };
}
