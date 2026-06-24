<script>
	import { onMount } from 'svelte';
	import SearchBar from '$lib/components/SearchBar.svelte';
	import FilterPanel from '$lib/components/FilterPanel.svelte';
	import DiscountGrid from '$lib/components/DiscountGrid.svelte';
	import { filterDiscounts } from '$lib/utils/search.js';

	let { data } = $props();

	// Reactive filter states
	let searchQuery = $state('');
	let selectedCategory = $state('');
	let selectedBank = $state('');
	let selectedDay = $state('');
	let selectedCard = $state('');

	// Compute filtered list
	let filteredDiscounts = $derived(
		filterDiscounts(data.discounts, {
			query: searchQuery,
			category: selectedCategory,
			bank: selectedBank,
			day: selectedDay,
			card: selectedCard
		})
	);

	// Outdated state detection
	let showWarning = $state(false);
	const scrapedTime = $derived(new Date(data.scraped_at));
	const formattedScrapedAt = $derived(scrapedTime.toLocaleString('es-AR', {
		day: '2-digit',
		month: '2-digit',
		year: 'numeric',
		hour: '2-digit',
		minute: '2-digit',
		timeZone: 'America/Argentina/Buenos_Aires'
	}));

	onMount(() => {
		const parsed = new Date(data.scraped_at);
		const diffMs = Date.now() - parsed.getTime();
		const diffHours = diffMs / (1000 * 60 * 60);
		if (diffHours > 25) {
			showWarning = true;
		}
	});
</script>

<div class="dashboard-container">
	{#if showWarning}
		<div class="warning-banner" role="alert">
			<span class="warning-icon">⚠️</span>
			<div class="warning-text">
				<strong>Atención:</strong> Los datos de descuentos no se actualizan desde el <span>{formattedScrapedAt}</span> (hace más de 25 horas).
			</div>
		</div>
	{/if}

	<header class="dashboard-header">
		<h1 class="brand-title">Ahorro<span class="highlight">AR</span></h1>
		<p class="brand-subtitle">Busca y consolida los mejores descuentos de BBVA y Santander en Argentina</p>
		<p class="scraped-meta">Última actualización: {formattedScrapedAt}</p>
	</header>

	<section class="search-section">
		<SearchBar bind:value={searchQuery} />
	</section>

	<section class="filters-section">
		<FilterPanel 
			bind:selectedCategory 
			bind:selectedBank 
			bind:selectedDay 
			bind:selectedCard 
		/>
	</section>

	<main class="results-section">
		<div class="results-meta">
			<h2>Beneficios Disponibles</h2>
			<span class="results-count">{filteredDiscounts.length} {filteredDiscounts.length === 1 ? 'descuento' : 'descuentos'}</span>
		</div>

		<DiscountGrid discounts={filteredDiscounts} />
	</main>
</div>

<style>
	.dashboard-container {
		max-width: 1200px;
		margin: 0 auto;
		padding: 24px 16px 60px 16px;
		display: flex;
		flex-direction: column;
		gap: 32px;
	}

	/* Warning Banner */
	.warning-banner {
		display: flex;
		align-items: center;
		gap: 12px;
		background: rgba(243, 156, 18, 0.15);
		border: 1px solid rgba(243, 156, 18, 0.3);
		border-radius: 8px;
		padding: 12px 16px;
		color: #f39c12;
		font-size: 0.9rem;
		box-shadow: 0 4px 12px rgba(243, 156, 18, 0.05);
		animation: fadeIn 0.3s ease;
	}

	@keyframes fadeIn {
		from { opacity: 0; transform: translateY(-10px); }
		to { opacity: 1; transform: translateY(0); }
	}

	.warning-icon {
		font-size: 1.2rem;
		flex-shrink: 0;
	}

	.warning-text span {
		text-decoration: underline;
		font-weight: 600;
	}

	/* Header */
	.dashboard-header {
		text-align: center;
		margin-top: 20px;
	}

	.brand-title {
		font-size: 3rem;
		font-weight: 800;
		color: #ffffff;
		margin: 0 0 8px 0;
		letter-spacing: -0.02em;
	}

	.brand-title .highlight {
		color: #3498db;
		background: linear-gradient(120deg, #3498db, #2ecc71);
		-webkit-background-clip: text;
		-webkit-text-fill-color: transparent;
	}

	.brand-subtitle {
		font-size: 1.1rem;
		color: #aaaaaa;
		margin: 0 auto 12px auto;
		max-width: 600px;
		line-height: 1.5;
	}

	.scraped-meta {
		font-size: 0.8rem;
		color: #555555;
		margin: 0;
	}

	/* Search and filter sections */
	.search-section {
		width: 100%;
	}

	.filters-section {
		width: 100%;
	}

	/* Results section */
	.results-section {
		display: flex;
		flex-direction: column;
		gap: 20px;
	}

	.results-meta {
		display: flex;
		justify-content: space-between;
		align-items: flex-end;
		border-bottom: 1px solid rgba(255, 255, 255, 0.05);
		padding-bottom: 10px;
	}

	.results-meta h2 {
		font-size: 1.25rem;
		font-weight: 700;
		color: #ffffff;
		margin: 0;
	}

	.results-count {
		font-size: 0.85rem;
		color: #888888;
		font-weight: 500;
		background: rgba(255, 255, 255, 0.03);
		padding: 4px 10px;
		border-radius: 6px;
		border: 1px solid rgba(255, 255, 255, 0.05);
	}
</style>
