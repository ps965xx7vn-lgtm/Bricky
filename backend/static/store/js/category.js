/* Category Page JavaScript */

// Get CSRF token from cookies
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

// Show notification with animation
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    const colors = {
        'success': '#4caf50',
        'error': '#f44336',
        'warning': '#ff9800',
        'info': '#2196f3'
    };
    
    notification.style.cssText = `
        position: fixed;
        bottom: 20px;
        left: 20px;
        padding: 16px 24px;
        background: ${colors[type] || colors['info']};
        color: white;
        border-radius: 6px;
        z-index: 1000;
        animation: slideUp 0.3s ease;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        max-width: 350px;
        font-weight: 500;
        font-size: 14px;
    `;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideDown 0.3s ease forwards';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Update cart count in navbar
function updateCartCount(count) {
    const cartCount = document.querySelector('.cart-count');
    if (cartCount) {
        cartCount.textContent = count;
        // Add pulse animation
        cartCount.style.animation = 'pulse 0.4s ease';
        setTimeout(() => {
            cartCount.style.animation = 'none';
        }, 400);
    }
}

// Quick view modal function
function quickView(e, productId, productName) {
    e.preventDefault();
    e.stopPropagation();
    
    console.log('Quick view for product:', productId, productName);
    
    // Create simple modal notification
    showNotification(`Quick view for "${productName}" - Feature coming soon!`, 'info');
    
    // TODO: Implement full quick view modal in future
    // This would load product details in a modal without navigating away
}

// Update sort when dropdown changes
function updateSort(value) {
    if (value) {
        const url = new URL(window.location);
        url.searchParams.set('sort', value);
        window.location.href = url.toString();
    }
}

// Add to cart function
function addToCart(e, productId) {
    if (e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    console.log('Adding product to cart:', productId);
    
    // Check if user is authenticated - if not, redirect to login
    const isAuthenticated = document.body.dataset.authenticated === 'true';
    if (!isAuthenticated) {
        showNotification('Please log in or register to add items to cart', 'info');
        setTimeout(() => {
            window.location.href = '/users/login/?next=' + window.location.pathname;
        }, 1500);
        return;
    }
    
    // Find the button that was clicked
    let button = e && e.target ? e.target : null;
    if (button && !button.classList.contains('btn-cart')) {
        button = button.closest('.btn-cart');
    }
    
    if (button) {
        button.disabled = true;
        const originalText = button.innerHTML;
        button.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
    }
    
    const form = new FormData();
    form.append('product_id', productId);
    form.append('quantity', 1);

    fetch('/orders/cart/add/', {
        method: 'POST',
        body: form,
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => {
        if (response.status === 302 || response.redirected) {
            showNotification('Please log in to add items to cart', 'warning');
            window.location.href = '/users/login/';
            return null;
        }
        return response.json();
    })
    .then(data => {
        if (!data) return;
        
        if (data.success) {
            showNotification(data.message, 'success');
            if (data.cart_count !== undefined) {
                updateCartCount(data.cart_count);
            }
        } else {
            showNotification(data.message || 'Failed to add item to cart', 'error');
        }
    })
    .catch(error => {
        console.error('Error adding to cart:', error);
        showNotification('Error adding to cart. Please try again.', 'error');
    })
    .finally(() => {
        // Re-enable button
        if (button) {
            button.disabled = false;
            button.innerHTML = originalText;
        }
    });
}

// Initialize event listeners on document ready
document.addEventListener('DOMContentLoaded', function() {
    // Handle view mode toggle
    document.querySelectorAll('.view-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.view-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            const view = this.dataset.view;
            const grid = document.getElementById('products-view');
            
            if (view === 'list') {
                grid.classList.add('list-view');
            } else {
                grid.classList.remove('list-view');
            }
        });
    });
});
