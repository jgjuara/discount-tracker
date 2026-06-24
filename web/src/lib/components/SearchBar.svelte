<script>
	let { value = $bindable(''), placeholder = 'Buscar comercios, marcas, cuotas...' } = $props();

	function handleClear() {
		value = '';
	}
</script>

<div class="search-bar-container">
	<div class="search-input-wrapper">
		<span class="search-icon">
			<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-search">
				<circle cx="11" cy="11" r="8"></circle>
				<line x1="21" y1="21" x2="16.65" y2="16.65"></line>
			</svg>
		</span>
		
		<input 
			type="text" 
			bind:value={value} 
			{placeholder}
			class="search-input"
			autocomplete="off"
		/>

		{#if value}
			<button class="clear-button" onclick={handleClear} aria-label="Limpiar búsqueda">
				<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-x">
					<line x1="18" y1="6" x2="6" y2="18"></line>
					<line x1="6" y1="6" x2="18" y2="18"></line>
				</svg>
			</button>
		{/if}
	</div>
</div>

<style>
	.search-bar-container {
		width: 100%;
		max-width: 600px;
		margin: 0 auto;
	}

	.search-input-wrapper {
		position: relative;
		display: flex;
		align-items: center;
		background: #1a1a1a;
		border: 1px solid rgba(255, 255, 255, 0.08);
		border-radius: 12px;
		padding: 0 16px;
		height: 52px;
		transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
	}

	.search-input-wrapper:hover {
		border-color: rgba(255, 255, 255, 0.15);
		box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
	}

	.search-input-wrapper:focus-within {
		background: #202020;
		border-color: #3498db;
		box-shadow: 0 8px 24px rgba(52, 152, 219, 0.15), 0 0 0 1px rgba(52, 152, 219, 0.25);
	}

	.search-icon {
		display: flex;
		align-items: center;
		color: #666666;
		margin-right: 12px;
		transition: color 0.25s ease;
	}

	.search-input-wrapper:focus-within .search-icon {
		color: #3498db;
	}

	.search-icon svg {
		width: 20px;
		height: 20px;
	}

	.search-input {
		flex-grow: 1;
		background: transparent;
		border: none;
		color: #ffffff;
		font-size: 1rem;
		font-family: 'Inter', sans-serif;
		height: 100%;
		outline: none;
		padding: 0;
	}

	.search-input::placeholder {
		color: #666666;
	}

	.clear-button {
		display: flex;
		align-items: center;
		justify-content: center;
		background: transparent;
		border: none;
		color: #888888;
		cursor: pointer;
		padding: 4px;
		border-radius: 50%;
		margin-left: 8px;
		transition: all 0.15s ease;
	}

	.clear-button:hover {
		color: #ffffff;
		background: rgba(255, 255, 255, 0.05);
	}

	.clear-button svg {
		width: 18px;
		height: 18px;
	}
</style>
