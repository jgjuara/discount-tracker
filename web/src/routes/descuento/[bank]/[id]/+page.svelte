<script>
	import BankBadge from '$lib/components/BankBadge.svelte';
	import { CANONICAL_CATEGORIES } from '$lib/utils/taxonomy.js';

	let { data } = $props();
	const discount = $derived(data.discount);

	const category = $derived(discount ? (CANONICAL_CATEGORIES[discount.canonical_category] || { name: 'Otro', emoji: '🏷️' }) : null);

	const WEEKDAYS = [
		{ value: 1, label: 'Lunes' },
		{ value: 2, label: 'Martes' },
		{ value: 3, label: 'Miércoles' },
		{ value: 4, label: 'Jueves' },
		{ value: 5, label: 'Viernes' },
		{ value: 6, label: 'Sábado' },
		{ value: 0, label: 'Domingo' }
	];

	function isDayActive(dayValue) {
		if (!discount || !discount.days_active) return false;
		return discount.days_active.includes(-1) || discount.days_active.includes(dayValue);
	}

	function formatDate(dateStr) {
		if (!dateStr) return 'No especificada';
		const [year, month, day] = dateStr.split('-');
		return `${day}/${month}/${year}`;
	}

	function formatCardType(card) {
		const mapping = {
			'credito_visa': 'Tarjeta de Crédito Visa',
			'credito_mastercard': 'Tarjeta de Crédito Mastercard',
			'credito_bbva': 'Tarjeta de Crédito BBVA',
			'debito_bbva': 'Tarjeta de Débito BBVA',
			'debito_visa': 'Tarjeta de Débito Visa',
			'mastercard': 'Tarjeta de Crédito Mastercard',
			'amex': 'Tarjeta American Express',
			'visa_recargable': 'Tarjeta Visa Recargable',
			'modo_qr': 'Pago con QR Modo'
		};
		return mapping[card.toLowerCase()] || card;
	}

	const glowColor = $derived(discount?.bank === 'bbva' ? 'rgba(0, 74, 151, 0.2)' : 'rgba(236, 0, 0, 0.2)');
	const themeColor = $derived(discount?.bank === 'bbva' ? '#004A97' : '#EC0000');
</script>

<svelte:head>
	<title>{discount ? `${discount.store_name} - Descuento` : 'Descuento no encontrado'}</title>
</svelte:head>

<div class="detail-container">
	<div class="navigation-row">
		<a href="/" class="back-link">
			<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="back-icon">
				<line x1="19" y1="12" x2="5" y2="12"></line>
				<polyline points="12 19 5 12 12 5"></polyline>
			</svg>
			Volver al inicio
		</a>
	</div>

	{#if !discount}
		<div class="error-view">
			<span class="error-emoji">⚠️</span>
			<h2>Descuento no encontrado</h2>
			<p>El beneficio seleccionado no existe o ya no se encuentra vigente en el sistema.</p>
			<a href="/" class="back-button-fill">Volver al inicio</a>
		</div>
	{:else}
		<div class="detail-card" style="--detail-glow: {glowColor}; --detail-theme: {themeColor}">
			<!-- Header inside card -->
			<div class="detail-card-header">
				<div class="store-image-wrap">
					{#if discount.image_url}
						<img src={discount.image_url} alt={discount.store_name} class="store-logo" />
					{:else}
						<div class="store-logo-placeholder">
							<span class="placeholder-emoji">{category.emoji}</span>
						</div>
					{/if}
				</div>
				<div class="store-info">
					<div class="badges-row">
						<BankBadge bank={discount.bank} />
						<span class="category-tag">
							{category.emoji} {category.name}
						</span>
					</div>
					<h1 class="store-name">{discount.store_name}</h1>
				</div>
			</div>

			<!-- Divider -->
			<div class="divider"></div>

			<!-- Core Benefit details -->
			<div class="detail-section">
				<div class="highlight-benefit-container">
					{#if discount.discount_pct > 0}
						<div class="benefit-box discount-box">
							<span class="benefit-val">{discount.discount_pct}%</span>
							<span class="benefit-lbl">Ahorro</span>
						</div>
					{/if}
					{#if discount.installments > 0}
						<div class="benefit-box installments-box">
							<span class="benefit-val">{discount.installments}</span>
							<span class="benefit-lbl">Cuotas sin Interés</span>
						</div>
					{/if}
				</div>

				<h2 class="detail-title">{discount.title}</h2>
				<p class="detail-description">{discount.description}</p>
			</div>

			<div class="divider"></div>

			<!-- Logistics/Validity/Days info -->
			<div class="logistics-grid">
				<div class="logistics-card">
					<h3 class="section-subtitle">Vigencia</h3>
					<div class="validity-dates">
						<div class="date-item">
							<span class="date-label">Desde:</span>
							<span class="date-value">{formatDate(discount.valid_from)}</span>
						</div>
						<div class="date-item">
							<span class="date-label">Hasta:</span>
							<span class="date-value">{formatDate(discount.valid_until)}</span>
						</div>
					</div>
				</div>

				<div class="logistics-card">
					<h3 class="section-subtitle">Tarjetas y Medios de Pago</h3>
					<ul class="card-types-list">
						{#each discount.card_types as card}
							<li>
								<span class="card-icon">💳</span>
								<span class="card-name">{formatCardType(card)}</span>
							</li>
						{/each}
					</ul>
				</div>
			</div>

			<div class="divider"></div>

			<!-- Days checklist -->
			<div class="detail-section">
				<h3 class="section-subtitle">Días de la semana activos</h3>
				<div class="days-checklist">
					{#each WEEKDAYS as day}
						{@const active = isDayActive(day.value)}
						<div class="day-check-item {active ? 'active' : 'inactive'}">
							<div class="checkbox-circle">
								{#if active}
									<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" class="check-icon-svg">
										<polyline points="20 6 9 17 4 12"></polyline>
									</svg>
								{/if}
							</div>
							<span class="day-label">{day.label}</span>
						</div>
					{/each}
				</div>
			</div>

			<!-- CTA action -->
			{#if discount.url}
				<div class="action-container">
					<a href={discount.url} target="_blank" rel="noopener noreferrer" class="cta-button" style="background-color: {themeColor}">
						Ir a la web del beneficio
						<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="cta-icon">
							<path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
							<polyline points="15 3 21 3 21 9"></polyline>
							<line x1="10" y1="14" x2="21" y2="3"></line>
						</svg>
					</a>
				</div>
			{/if}
		</div>
	{/if}
</div>

<style>
	.detail-container {
		max-width: 800px;
		margin: 0 auto;
		padding: 24px 16px 80px 16px;
		display: flex;
		flex-direction: column;
		gap: 20px;
	}

	.navigation-row {
		display: flex;
		align-items: center;
	}

	.back-link {
		display: flex;
		align-items: center;
		gap: 8px;
		color: #aaaaaa;
		text-decoration: none;
		font-size: 0.9rem;
		font-weight: 500;
		transition: color 0.2s ease;
	}

	.back-link:hover {
		color: #ffffff;
	}

	.back-icon {
		width: 18px;
		height: 18px;
	}

	/* Card design */
	.detail-card {
		background: #1a1a1a;
		border: 1px solid rgba(255, 255, 255, 0.05);
		border-radius: 16px;
		padding: 32px;
		box-shadow: 0 12px 40px rgba(0, 0, 0, 0.3), 0 0 20px var(--detail-glow);
		display: flex;
		flex-direction: column;
		gap: 24px;
	}

	.detail-card-header {
		display: flex;
		align-items: center;
		gap: 24px;
		flex-wrap: wrap;
	}

	.store-image-wrap {
		width: 80px;
		height: 80px;
		border-radius: 12px;
		background: #121212;
		border: 1px solid rgba(255, 255, 255, 0.05);
		display: flex;
		align-items: center;
		justify-content: center;
		overflow: hidden;
		flex-shrink: 0;
	}

	.store-logo {
		width: 100%;
		height: 100%;
		object-fit: contain;
		padding: 8px;
	}

	.store-logo-placeholder {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 100%;
		height: 100%;
		background: linear-gradient(135deg, #222 0%, #121212 100%);
	}

	.placeholder-emoji {
		font-size: 2.2rem;
	}

	.store-info {
		display: flex;
		flex-direction: column;
		gap: 8px;
	}

	.badges-row {
		display: flex;
		gap: 10px;
		align-items: center;
		flex-wrap: wrap;
	}

	.category-tag {
		font-size: 0.8rem;
		font-weight: 500;
		color: #aaaaaa;
		background: rgba(255, 255, 255, 0.03);
		padding: 4px 10px;
		border-radius: 6px;
		border: 1px solid rgba(255, 255, 255, 0.05);
	}

	.store-name {
		font-size: 2rem;
		font-weight: 800;
		color: #ffffff;
		margin: 0;
		letter-spacing: -0.01em;
	}

	.divider {
		height: 1px;
		background: rgba(255, 255, 255, 0.05);
		width: 100%;
	}

	.detail-section {
		display: flex;
		flex-direction: column;
		gap: 16px;
	}

	/* Highlights and visual benefit tags */
	.highlight-benefit-container {
		display: flex;
		gap: 16px;
		flex-wrap: wrap;
	}

	.benefit-box {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		padding: 16px 24px;
		border-radius: 12px;
		min-width: 120px;
		box-shadow: 0 4px 12px rgba(0,0,0,0.15);
	}

	.discount-box {
		background: rgba(39, 174, 96, 0.1);
		border: 1px solid rgba(46, 204, 113, 0.25);
		color: #2ecc71;
	}

	.installments-box {
		background: rgba(155, 89, 182, 0.1);
		border: 1px solid rgba(155, 89, 182, 0.25);
		color: #9b59b6;
	}

	.benefit-val {
		font-size: 2.25rem;
		font-weight: 800;
		line-height: 1;
		letter-spacing: -0.02em;
	}

	.benefit-lbl {
		font-size: 0.75rem;
		font-weight: 700;
		text-transform: uppercase;
		margin-top: 4px;
		opacity: 0.8;
		letter-spacing: 0.05em;
	}

	.detail-title {
		font-size: 1.25rem;
		font-weight: 700;
		color: #ffffff;
		margin: 8px 0 0 0;
	}

	.detail-description {
		font-size: 1rem;
		color: #cccccc;
		line-height: 1.6;
		margin: 0;
	}

	/* Logistics Grid */
	.logistics-grid {
		display: grid;
		grid-template-columns: 1fr;
		gap: 24px;
	}

	@media (min-width: 600px) {
		.logistics-grid {
			grid-template-columns: 1fr 1fr;
		}
	}

	.logistics-card {
		background: rgba(255, 255, 255, 0.02);
		border: 1px solid rgba(255, 255, 255, 0.03);
		border-radius: 12px;
		padding: 20px;
	}

	.section-subtitle {
		font-size: 0.85rem;
		font-weight: 700;
		color: #666666;
		text-transform: uppercase;
		margin: 0 0 16px 0;
		letter-spacing: 0.05em;
	}

	.validity-dates {
		display: flex;
		flex-direction: column;
		gap: 12px;
	}

	.date-item {
		display: flex;
		justify-content: space-between;
		font-size: 0.95rem;
		border-bottom: 1px dashed rgba(255, 255, 255, 0.05);
		padding-bottom: 8px;
	}

	.date-label {
		color: #888888;
		font-weight: 500;
	}

	.date-value {
		color: #ffffff;
		font-weight: 600;
	}

	/* Card types list */
	.card-types-list {
		list-style: none;
		padding: 0;
		margin: 0;
		display: flex;
		flex-direction: column;
		gap: 10px;
	}

	.card-types-list li {
		display: flex;
		align-items: center;
		gap: 8px;
		font-size: 0.95rem;
		color: #dddddd;
	}

	.card-icon {
		font-size: 1.1rem;
	}

	.card-name {
		font-weight: 500;
	}

	/* Weekdays checklist styles */
	.days-checklist {
		display: grid;
		grid-template-columns: repeat(2, 1fr);
		gap: 10px;
	}

	@media (min-width: 480px) {
		.days-checklist {
			grid-template-columns: repeat(4, 1fr);
		}
	}

	@media (min-width: 640px) {
		.days-checklist {
			grid-template-columns: repeat(7, 1fr);
		}
	}

	.day-check-item {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 8px;
		padding: 12px 8px;
		border-radius: 8px;
		border: 1px solid transparent;
		transition: all 0.2s ease;
	}

	.day-check-item.active {
		background: rgba(52, 152, 219, 0.06);
		border-color: rgba(52, 152, 219, 0.15);
		color: #ffffff;
	}

	.day-check-item.inactive {
		background: rgba(255, 255, 255, 0.01);
		border-color: rgba(255, 255, 255, 0.02);
		color: #444444;
	}

	.checkbox-circle {
		width: 22px;
		height: 22px;
		border-radius: 50%;
		display: flex;
		align-items: center;
		justify-content: center;
		transition: all 0.2s ease;
	}

	.active .checkbox-circle {
		background: #3498db;
		color: #ffffff;
		box-shadow: 0 0 8px rgba(52, 152, 219, 0.4);
	}

	.inactive .checkbox-circle {
		border: 2px solid #333333;
		background: transparent;
	}

	.check-icon-svg {
		width: 14px;
		height: 14px;
	}

	.day-label {
		font-size: 0.8rem;
		font-weight: 600;
	}

	/* Action CTA */
	.action-container {
		display: flex;
		justify-content: center;
		margin-top: 10px;
	}

	.cta-button {
		display: inline-flex;
		align-items: center;
		gap: 10px;
		color: #ffffff;
		font-size: 0.95rem;
		font-weight: 700;
		text-decoration: none;
		padding: 14px 28px;
		border-radius: 8px;
		transition: all 0.2s ease;
		box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
		font-family: 'Inter', sans-serif;
	}

	.cta-button:hover {
		transform: translateY(-2px);
		filter: brightness(1.1);
		box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4);
	}

	.cta-icon {
		width: 16px;
		height: 16px;
	}

	/* Error state */
	.error-view {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		padding: 60px 20px;
		background: #1a1a1a;
		border: 1px dashed rgba(255, 255, 255, 0.1);
		border-radius: 16px;
		text-align: center;
		max-width: 500px;
		margin: 40px auto;
	}

	.error-emoji {
		font-size: 3rem;
		margin-bottom: 16px;
	}

	.error-view h2 {
		font-size: 1.5rem;
		color: #ffffff;
		margin: 0 0 8px 0;
	}

	.error-view p {
		color: #888888;
		margin: 0 0 24px 0;
		font-size: 0.95rem;
		line-height: 1.5;
	}

	.back-button-fill {
		display: inline-block;
		background: #333333;
		color: #ffffff;
		text-decoration: none;
		padding: 10px 24px;
		border-radius: 6px;
		font-size: 0.9rem;
		font-weight: 600;
		transition: background 0.2s;
	}

	.back-button-fill:hover {
		background: #444444;
	}
</style>
