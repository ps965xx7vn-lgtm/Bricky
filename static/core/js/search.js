// Search Autocomplete Functionality

document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.querySelector('.search-input-main');
    
    if (!searchInput) return;

    let autocompleteDropdown = null;

    searchInput.addEventListener('input', function() {
        const query = this.value.trim();
        
        if (query.length < 1) {
            if (autocompleteDropdown) autocompleteDropdown.remove();
            return;
        }

        // Remove old dropdown
        if (autocompleteDropdown) autocompleteDropdown.remove();

        // Fetch suggestions
        fetch(`/api/autocomplete/?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                if (data.suggestions.products.length === 0 && data.suggestions.categories.length === 0) {
                    return;
                }

                // Create dropdown
                const dropdown = document.createElement('div');
                dropdown.className = 'autocomplete-dropdown';

                let html = '';

                if (data.suggestions.categories.length > 0) {
                    html += '<div class="autocomplete-section"><strong>Categories</strong>';
                    data.suggestions.categories.forEach(cat => {
                        html += `<div class="autocomplete-item" data-type="category">${cat}</div>`;
                    });
                    html += '</div>';
                }

                if (data.suggestions.products.length > 0) {
                    html += '<div class="autocomplete-section"><strong>Products</strong>';
                    data.suggestions.products.forEach(prod => {
                        html += `<div class="autocomplete-item" data-type="product">${prod}</div>`;
                    });
                    html += '</div>';
                }

                dropdown.innerHTML = html;
                searchInput.parentElement.appendChild(dropdown);
                autocompleteDropdown = dropdown;

                // Add click handlers
                document.querySelectorAll('.autocomplete-item').forEach(item => {
                    item.addEventListener('click', function() {
                        searchInput.value = this.textContent;
                        dropdown.remove();
                        searchInput.form.submit();
                    });
                });
            });
    });

    // Close autocomplete on blur
    searchInput.addEventListener('blur', function() {
        setTimeout(() => {
            if (autocompleteDropdown) autocompleteDropdown.remove();
        }, 200);
    });
});
