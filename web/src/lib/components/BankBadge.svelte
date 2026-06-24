<script>
	let { bank = '' } = $props();
	
	const bankName = $derived(bank ? bank.toUpperCase() : 'DESCONOCIDO');
	const badgeClass = $derived(bank ? `badge-${bank.toLowerCase()}` : '');
</script>

<span class="bank-badge {badgeClass}">
	{bankName}
</span>

<style>
	.bank-badge {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		padding: 4px 10px;
		font-size: 0.75rem;
		font-weight: 700;
		letter-spacing: 0.05em;
		border-radius: 9999px;
		color: #ffffff;
		text-transform: uppercase;
		font-family: 'Inter', sans-serif;
		box-shadow: 0 2px 4px rgba(0, 0, 0, 0.25);
		text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
	}
	
	.badge-bbva {
		background-color: #004A97;
		border: 1px solid rgba(255, 255, 255, 0.15);
	}
	
	.badge-santander {
		background-color: #EC0000;
		border: 1px solid rgba(255, 255, 255, 0.15);
	}
</style>
