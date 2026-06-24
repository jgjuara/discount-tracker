<script>
	import { CANONICAL_CATEGORIES, DAYS_WEEK, CARD_TYPES, BANKS } from '../utils/taxonomy.js';

	let {
		selectedCategory = $bindable(''),
		selectedBank = $bindable(''),
		selectedDay = $bindable(''),
		selectedCard = $bindable('')
	} = $props();

	// Check if any filters are active
	const hasActiveFilters = $derived(
		selectedCategory !== '' || 
		selectedBank !== '' || 
		selectedDay !== '' || 
		selectedCard !== ''
	);

	function selectCategory(key) {
		if (selectedCategory === key) {
			selectedCategory = ''; // Toggle off
		} else {
			selectedCategory = key;
		}
	}

	function resetFilters() {
		selectedCategory = '';
		selectedBank = '';
		selectedDay = '';
		selectedCard = '';
	}
</script>

<div class="filter-panel">
	<!-- Category selection row (Scrollable Chips) -->
	<div class="category-scroll-container">
		<div class="category-chips">
			<button 
				type="button" 
				class="category-chip {selectedCategory === '' ? 'active' : ''}"
				onclick={() => selectedCategory = ''}
			>
				<span class="chip-emoji">✨</span>
				<span class="chip-name">Todos</span>
			</button>
			{#each Object.entries(CANONICAL_CATEGORIES) as [key, cat]}
				<button 
					type="button" 
					class="category-chip {selectedCategory === key ? 'active' : ''}"
					onclick={() => selectCategory(key)}
				>
					<span class="chip-emoji">{cat.emoji}</span>
					<span class="chip-name">{cat.name}</span>
				</button>
			{/each}
		</div>
	</div>

	<!-- Sub-filters (Bank, Card, Day) -->
	<div class="sub-filters-container">
		<div class="filter-group">
			<label for="bank-filter" class="filter-label">Banco</label>
			<div class="button-group">
				<button 
					type="button" 
					class="group-btn {selectedBank === '' ? 'active' : ''}" 
					onclick={() => selectedBank = ''}
				>
					Todos
				</button>
				<button 
					type="button" 
					class="group-btn btn-bbva {selectedBank === 'bbva' ? 'active' : ''}" 
					onclick={() => selectedBank = 'bbva'}
				>
					BBVA
				</button>
				<button 
					type="button" 
					class="group-btn btn-santander {selectedBank === 'santander' ? 'active' : ''}" 
					onclick={() => selectedBank = 'santander'}
				>
					Santander
				</button>
			</div>
		</div>

		<div class="filter-group">
			<label for="card-filter" class="filter-label">Tarjeta</label>
			<div class="button-group">
				<button 
					type="button" 
					class="group-btn {selectedCard === '' ? 'active' : ''}" 
					onclick={() => selectedCard = ''}
				>
					Todas
				</button>
				<button 
					type="button" 
					class="group-btn {selectedCard === 'credit' ? 'active' : ''}" 
					onclick={() => selectedCard = 'credit'}
				>
					Crédito
				</button>
				<button 
					type="button" 
					class="group-btn {selectedCard === 'debit' ? 'active' : ''}" 
					onclick={() => selectedCard = 'debit'}
				>
					Débito
				</button>
			</div>
		</div>

		<div class="filter-group select-group">
			<label for="day-select" class="filter-label">Día de la semana</label>
			<select 
				id="day-select" 
				bind:value={selectedDay}
				class="filter-select"
			>
				<option value="">Cualquier día</option>
				{#each DAYS_WEEK as d}
					<option value={d.value.toString()}>{d.label}</option>
				{/each}
			</select>
		</div>

		{#if hasActiveFilters}
			<div class="reset-container">
				<button type="button" class="reset-button" onclick={resetFilters}>
					Limpiar filtros
				</button>
			</div>
		{/if}
	</div>
</div>

<style>
	.filter-panel {
		display: flex;
		flex-direction: column;
		gap: 20px;
		width: 100%;
		background: #151515;
		border: 1px solid rgba(255, 255, 255, 0.04);
		border-radius: 16px;
		padding: 20px;
		box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
	}

	/* Scrollable categories */
	.category-scroll-container {
		width: 100%;
		overflow-x: auto;
		scrollbar-width: none; /* Firefox */
		padding-bottom: 4px;
	}

	.category-scroll-container::-webkit-scrollbar {
		display: none; /* Chrome, Safari, Opera */
	}

	.category-chips {
		display: flex;
		gap: 10px;
		width: max-content;
		padding: 2px;
	}

	.category-chip {
		display: flex;
		align-items: center;
		gap: 8px;
		padding: 8px 16px;
		background: #202020;
		border: 1px solid rgba(255, 255, 255, 0.06);
		border-radius: 9999px;
		color: #aaaaaa;
		font-size: 0.85rem;
		font-weight: 500;
		cursor: pointer;
		transition: all 0.2s ease;
		font-family: 'Inter', sans-serif;
	}

	.category-chip:hover {
		color: #ffffff;
		border-color: rgba(255, 255, 255, 0.15);
		background: #252525;
	}

	.category-chip.active {
		color: #ffffff;
		background: #3498db;
		border-color: #3498db;
		box-shadow: 0 0 12px rgba(52, 152, 219, 0.4);
	}

	.chip-emoji {
		font-size: 1rem;
	}

	/* Sub-filters grid */
	.sub-filters-container {
		display: grid;
		grid-template-columns: 1fr;
		gap: 16px;
		align-items: flex-end;
	}

	@media (min-width: 768px) {
		.sub-filters-container {
			grid-template-columns: repeat(3, 1fr) auto;
		}
	}

	.filter-group {
		display: flex;
		flex-direction: column;
		gap: 8px;
	}

	.filter-label {
		font-size: 0.75rem;
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		color: #666666;
	}

	/* Button Groups */
	.button-group {
		display: flex;
		background: #202020;
		border: 1px solid rgba(255, 255, 255, 0.06);
		border-radius: 8px;
		padding: 2px;
		height: 40px;
	}

	.group-btn {
		flex: 1;
		background: transparent;
		border: none;
		color: #888888;
		font-size: 0.85rem;
		font-weight: 500;
		cursor: pointer;
		border-radius: 6px;
		transition: all 0.15s ease;
		font-family: 'Inter', sans-serif;
	}

	.group-btn:hover {
		color: #ffffff;
	}

	.group-btn.active {
		color: #ffffff;
		background: #333333;
		box-shadow: 0 2px 4px rgba(0, 0, 0, 0.15);
	}

	.group-btn.btn-bbva.active {
		background: #004A97;
		box-shadow: 0 2px 8px rgba(0, 74, 151, 0.4);
	}

	.group-btn.btn-santander.active {
		background: #EC0000;
		box-shadow: 0 2px 8px rgba(236, 0, 0, 0.4);
	}

	/* Select elements */
	.filter-select {
		background: #202020;
		border: 1px solid rgba(255, 255, 255, 0.06);
		border-radius: 8px;
		color: #e0e0e0;
		padding: 0 12px;
		font-size: 0.85rem;
		height: 40px;
		outline: none;
		cursor: pointer;
		transition: all 0.15s ease;
		font-family: 'Inter', sans-serif;
	}

	.filter-select:hover {
		border-color: rgba(255, 255, 255, 0.15);
	}

	.filter-select:focus {
		border-color: #3498db;
	}

	/* Reset button */
	.reset-container {
		display: flex;
		align-items: center;
		height: 40px;
	}

	.reset-button {
		background: transparent;
		border: 1px solid rgba(231, 76, 60, 0.2);
		color: #e74c3c;
		border-radius: 8px;
		padding: 0 16px;
		font-size: 0.85rem;
		font-weight: 500;
		height: 100%;
		cursor: pointer;
		transition: all 0.2s ease;
		font-family: 'Inter', sans-serif;
		width: 100%;
	}

	.reset-button:hover {
		background: rgba(231, 76, 60, 0.1);
		border-color: #e74c3c;
		color: #ff6b6b;
	}
</style>
