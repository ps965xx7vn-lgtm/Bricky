// Sort handler - remove inline onchange handler
document.addEventListener('DOMContentLoaded', function() {
    const sortSelect = document.querySelector('.sort-select');
    if (sortSelect) {
        sortSelect.addEventListener('change', function() {
            const sortValue = this.value;
            if (sortValue) {
                // Add sort parameter to URL
                const url = new URL(window.location);
                url.searchParams.set('sort', sortValue);
                window.location.href = url.toString();
            }
        });
    }

    // View switcher
    document.querySelectorAll('.view-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.view-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            const view = this.dataset.view;
            const display = document.getElementById('products-display');
            
            if (view === 'list') {
                display.classList.add('list-view');
            } else {
                display.classList.remove('list-view');
            }
        });
    });
});

function addToCart(e, productId) {
    e.preventDefault();
    e.stopPropagation();
    
    const userIsAuthenticated = document.body.dataset.userAuthenticated === 'true';
    
    if (!userIsAuthenticated) {
        window.location.href = document.body.dataset.loginUrl;
        return;
    }
    
    const form = new FormData();
    form.append('product_id', productId);
    form.append('quantity', 1);

    fetch(document.body.dataset.addToCartUrl, {
        method: 'POST',
        body: form,
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification(data.message, 'success');
            updateCartCount(data.cart_count);
        } else {
            showNotification(data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Error adding to cart', 'error');
    });
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function updateCartCount(count) {
    const cartCount = document.querySelector('.cart-count');
    if (cartCount) {
        cartCount.textContent = count;
    }
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 80px;
        right: 20px;
        background: ${type === 'success' ? '#4caf50' : type === 'error' ? '#ff4444' : '#2196F3'};
        color: white;
        padding: 16px 24px;
        border-radius: 6px;
        z-index: 1000;
        animation: slideIn 0.3s ease;
    `;
    document.body.appendChild(notification);
    setTimeout(() => notification.remove(), 3000);
}
