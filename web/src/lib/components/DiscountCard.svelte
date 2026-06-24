<script>
	import BankBadge from './BankBadge.svelte';
	import { CANONICAL_CATEGORIES } from '../utils/taxonomy.js';

	let { discount } = $props();

	const category = $derived(CANONICAL_CATEGORIES[discount.canonical_category] || { name: 'Otro', emoji: '🏷️' });
	const initial = $derived(discount.store_name ? discount.store_name.charAt(0).toUpperCase() : '?');

	// Highlighted badge details
	const hasDiscount = $derived(discount.discount_pct > 0);
	const hasInstallments = $derived(discount.installments > 0);

	// Bank-specific hover glow colors
	const glowColor = $derived(discount.bank === 'bbva' ? 'rgba(0, 74, 151, 0.25)' : 'rgba(236, 0, 0, 0.25)');
	const hoverBorderColor = $derived(discount.bank === 'bbva' ? '#004A97' : '#EC0000');
</script>

<a href="/descuento/{discount.bank}/{discount.id}" class="discount-card" style="--hover-glow: {glowColor}; --hover-border: {hoverBorderColor}">
	<div class="card-image-container">
		{#if discount.image_url}
			<img src={discount.image_url} alt={discount.store_name} class="card-image" loading="lazy" />
		{:else}
			<div class="card-image-placeholder">
				<span class="placeholder-emoji">{category.emoji}</span>
				<span class="placeholder-initial">{initial}</span>
			</div>
		{/if}
		<div class="bank-badge-overlay">
			<BankBadge bank={discount.bank} />
		</div>
	</div>

	<div class="card-content">
		<div class="card-meta">
			<span class="card-category">
				{category.emoji} {category.name}
			</span>
		</div>
		
		<h3 class="card-store">{discount.store_name}</h3>
		
		<div class="benefit-badges">
			{#if hasDiscount}
				<span class="badge-pct">{discount.discount_pct}% OFF</span>
			{/if}
			{#if hasInstallments}
				<span class="badge-installments">{discount.installments} Cuotas</span>
			{/if}
		</div>

		<h4 class="card-title">{discount.title}</h4>
		<p class="card-description">{discount.description}</p>
	</div>
</a>

<style>
	.discount-card {
		display: flex;
		flex-direction: column;
		background: #1a1a1a;
		border: 1px solid rgba(255, 255, 255, 0.05);
		border-radius: 12px;
		overflow: hidden;
		text-decoration: none;
		color: #f0f0f0;
		transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
		height: 100%;
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
	}

	.discount-card:hover {
		transform: translateY(-4px);
		border-color: var(--hover-border);
		box-shadow: 0 12px 24px rgba(0, 0, 0, 0.3), 0 0 16px var(--hover-glow);
	}

	.discount-card:focus-visible {
		outline: 2px solid var(--hover-border);
		outline-offset: 2px;
	}

	.card-image-container {
		position: relative;
		height: 140px;
		background: #121212;
		display: flex;
		align-items: center;
		justify-content: center;
		overflow: hidden;
		border-bottom: 1px solid rgba(255, 255, 255, 0.03);
	}

	.card-image {
		width: 100%;
		height: 100%;
		object-fit: contain;
		padding: 12px;
		transition: transform 0.2s ease;
	}

	.discount-card:hover .card-image {
		transform: scale(1.04);
	}

	.card-image-placeholder {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		width: 100%;
		height: 100%;
		background: linear-gradient(135deg, #1f1f1f 0%, #121212 100%);
		opacity: 0.85;
	}

	.placeholder-emoji {
		font-size: 2rem;
		margin-bottom: 4px;
	}

	.placeholder-initial {
		font-size: 1.1rem;
		font-weight: 700;
		color: #888888;
		letter-spacing: 0.05em;
	}

	.bank-badge-overlay {
		position: absolute;
		top: 10px;
		right: 10px;
		z-index: 2;
	}

	.card-content {
		display: flex;
		flex-direction: column;
		padding: 16px;
		flex-grow: 1;
	}

	.card-meta {
		display: flex;
		align-items: center;
		margin-bottom: 8px;
	}

	.card-category {
		font-size: 0.75rem;
		color: #aaaaaa;
		font-weight: 500;
	}

	.card-store {
		font-size: 1.15rem;
		font-weight: 700;
		color: #ffffff;
		margin: 0 0 8px 0;
		line-height: 1.2;
	}

	.benefit-badges {
		display: flex;
		gap: 6px;
		flex-wrap: wrap;
		margin-bottom: 10px;
	}

	.badge-pct, .badge-installments {
		font-size: 0.7rem;
		font-weight: 700;
		padding: 3px 8px;
		border-radius: 4px;
		text-transform: uppercase;
	}

	.badge-pct {
		background: rgba(39, 174, 96, 0.15);
		color: #2ecc71;
		border: 1px solid rgba(46, 204, 113, 0.2);
	}

	.badge-installments {
		background: rgba(155, 89, 182, 0.15);
		color: #9b59b6;
		border: 1px solid rgba(155, 89, 182, 0.2);
	}

	.card-title {
		font-size: 0.9rem;
		font-weight: 600;
		color: #e0e0e0;
		margin: 0 0 6px 0;
		line-height: 1.3;
	}

	.card-description {
		font-size: 0.8rem;
		color: #999999;
		margin: 0;
		line-height: 1.4;
		display: -webkit-box;
		-webkit-line-clamp: 2;
		-webkit-box-orient: vertical;
		overflow: hidden;
		text-overflow: ellipsis;
	}
</style>
