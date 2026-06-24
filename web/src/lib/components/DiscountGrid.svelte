<script>
	import DiscountCard from './DiscountCard.svelte';

	let { discounts = [] } = $props();
</script>

{#if discounts.length === 0}
	<div class="empty-state">
		<span class="empty-icon">🔍</span>
		<h3 class="empty-title">No se encontraron descuentos</h3>
		<p class="empty-message">Prueba ajustando los filtros o utilizando otros términos de búsqueda.</p>
	</div>
{:else}
	<div class="discount-grid">
		{#each discounts as discount (discount.id)}
			<div class="grid-item">
				<DiscountCard {discount} />
			</div>
		{/each}
	</div>
{/if}

<style>
	.discount-grid {
		display: grid;
		grid-template-columns: 1fr;
		gap: 24px;
		width: 100%;
	}

	/* Responsive grid scaling */
	@media (min-width: 640px) {
		.discount-grid {
			grid-template-columns: repeat(2, 1fr);
		}
	}

	@media (min-width: 1024px) {
		.discount-grid {
			grid-template-columns: repeat(3, 1fr);
		}
	}

	@media (min-width: 1280px) {
		.discount-grid {
			grid-template-columns: repeat(4, 1fr);
		}
	}

	.grid-item {
		display: flex;
		flex-direction: column;
		height: 100%;
	}

	.empty-state {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		padding: 60px 20px;
		background: #1a1a1a;
		border: 1px dashed rgba(255, 255, 255, 0.1);
		border-radius: 12px;
		text-align: center;
		width: 100%;
		max-width: 600px;
		margin: 40px auto;
		box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
	}

	.empty-icon {
		font-size: 3rem;
		margin-bottom: 16px;
		filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.3));
	}

	.empty-title {
		font-size: 1.25rem;
		font-weight: 700;
		color: #ffffff;
		margin: 0 0 8px 0;
	}

	.empty-message {
		font-size: 0.9rem;
		color: #888888;
		margin: 0;
		max-width: 320px;
		line-height: 1.5;
	}
</style>
