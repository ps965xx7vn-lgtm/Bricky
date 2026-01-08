/* Search Modal Functionality */

function openSearchModal(e) {
    if (e && e.preventDefault) {
        e.preventDefault();
    }
    document.getElementById('search-modal').classList.add('active');
    document.querySelector('.search-modal-input').focus();
}

function closeSearchModal() {
    document.getElementById('search-modal').classList.remove('active');
}

function setSuggestion(text) {
    document.querySelector('.search-modal-input').value = text;
    document.querySelector('.search-modal-form').submit();
}

function goToCategory(category) {
    window.location.href = `/?category=${encodeURIComponent(category.toLowerCase().replace(/ /g, '-'))}`;
}

// Initialize event listeners and other functionality
document.addEventListener('DOMContentLoaded', function() {
    // Button event listeners
    const searchOpenBtn = document.getElementById('search-open-btn');
    const searchCloseBtn = document.getElementById('search-close-btn');
    
    if (searchOpenBtn) {
        searchOpenBtn.addEventListener('click', openSearchModal);
    }
    
    if (searchCloseBtn) {
        searchCloseBtn.addEventListener('click', closeSearchModal);
    }

    // Close modal on Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeSearchModal();
        }
    });

    // Open modal on Ctrl+K or Cmd+K
    document.addEventListener('keydown', function(e) {
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            openSearchModal();
        }
    });

    // Autocomplete for search modal
    const searchInput = document.querySelector('.search-modal-input');
    const suggestionsContainer = document.getElementById('search-suggestions');

    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const query = this.value.trim();
            
            if (query.length < 2) {
                suggestionsContainer.innerHTML = '';
                return;
            }

            fetch(`/api/autocomplete/?q=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    let html = '';

                    if (data.suggestions.categories.length > 0) {
                        html += '<div class="suggestions-section"><h4>Categories</h4>';
                        data.suggestions.categories.forEach(cat => {
                            html += `<div class="suggestion-item" data-category="${cat}">${cat}</div>`;
                        });
                        html += '</div>';
                    }

                    if (data.suggestions.products.length > 0) {
                        html += '<div class="suggestions-section"><h4>Products</h4>';
                        data.suggestions.products.forEach(prod => {
                            html += `<div class="suggestion-item" data-suggestion="${prod}">${prod}</div>`;
                        });
                        html += '</div>';
                    }

                    suggestionsContainer.innerHTML = html;
                    
                    // Add event listeners to dynamically created suggestion items
                    document.querySelectorAll('.suggestion-item').forEach(item => {
                        item.addEventListener('click', function() {
                            if (this.dataset.category) {
                                goToCategory(this.dataset.category);
                            } else if (this.dataset.suggestion) {
                                setSuggestion(this.dataset.suggestion);
                            }
                        });
                    });
                });
        });
    }
});
