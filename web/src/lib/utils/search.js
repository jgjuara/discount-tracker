/**
 * Filters a list of discounts based on search query, category, bank, day of week, and card type.
 *
 * @param {Array} discounts - Array of normalized discount objects.
 * @param {Object} filters - Filter criteria.
 * @param {string} [filters.query] - Search query (case-insensitive, matched against store_name, title, description).
 * @param {string} [filters.category] - Canonical category code.
 * @param {string} [filters.bank] - Bank identifier ('bbva' or 'santander').
 * @param {number|string} [filters.day] - Day of the week (0=Sunday to 6=Saturday).
 * @param {string} [filters.card] - Card type filter ('credit', 'credito', 'debit', or 'debito').
 * @returns {Array} Filtered list of discounts.
 */
export function filterDiscounts(discounts, { query, category, bank, day, card } = {}) {
  if (!discounts || !Array.isArray(discounts)) return [];
  
  return discounts.filter(d => {
    // 1. Search Query (case-insensitive in store_name, title, description)
    if (query) {
      const q = query.toLowerCase().trim();
      if (q) {
        const match = [d.store_name, d.title, d.description]
          .some(f => f && f.toLowerCase().includes(q));
        if (!match) return false;
      }
    }
    
    // 2. Canonical Category
    if (category && d.canonical_category !== category) {
      return false;
    }
    
    // 3. Bank
    if (bank && d.bank !== bank) {
      return false;
    }
    
    // 4. Day of the Week (0 = Sunday, 6 = Saturday)
    // -1 in days_active means it is active every day.
    if (day !== null && day !== undefined && day !== '') {
      const dayNum = parseInt(day, 10);
      if (!isNaN(dayNum)) {
        const active = d.days_active || [];
        if (!active.includes(-1) && !active.includes(dayNum)) {
          return false;
        }
      }
    }
    
    // 5. Card Type (credit vs debit)
    if (card) {
      const cardType = card.toLowerCase().trim();
      if (cardType === 'credit' || cardType === 'credito') {
        const isCredit = d.card_types && d.card_types.some(t => {
          const tl = t.toLowerCase();
          return tl.includes('credit') || tl.includes('credito') || tl.includes('mastercard') || tl.includes('amex');
        });
        if (!isCredit) return false;
      } else if (cardType === 'debit' || cardType === 'debito') {
        const isDebit = d.card_types && d.card_types.some(t => {
          const tl = t.toLowerCase();
          return tl.includes('debit') || tl.includes('debito');
        });
        if (!isDebit) return false;
      } else {
        // Fallback check: exact or substring match of card code
        const hasCard = d.card_types && d.card_types.some(t => t.toLowerCase().includes(cardType));
        if (!hasCard) return false;
      }
    }
    
    return true;
  });
}
