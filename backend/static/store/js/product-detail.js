/* Product Detail JavaScript Functions */

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
        max-width: 90%;
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
        cartCount.style.animation = 'pulse 0.4s ease';
        setTimeout(() => {
            cartCount.style.animation = 'none';
        }, 400);
    }
}

// Change main product image
function changeImage(img) {
    const mainImage = document.getElementById('mainImage');
    if (mainImage) {
        mainImage.src = img.src;
    }
    
    document.querySelectorAll('.thumbnail').forEach(thumb => {
        thumb.classList.remove('active');
    });
    img.classList.add('active');
}

// Increase quantity
function increaseQty(maxStock) {
    const qtyInput = document.getElementById('quantity');
    if (qtyInput) {
        const current = parseInt(qtyInput.value);
        if (current < maxStock) {
            qtyInput.value = current + 1;
        } else {
            showNotification(`Maximum ${maxStock} items available`, 'warning');
        }
    }
}

// Decrease quantity
function decreaseQty() {
    const qtyInput = document.getElementById('quantity');
    if (qtyInput) {
        const current = parseInt(qtyInput.value);
        if (current > 1) {
            qtyInput.value = current - 1;
        }
    }
}

// Switch between product tabs
function switchTab(e, tabName) {
    e.preventDefault();
    
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Remove active class from all buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab
    const selectedTab = document.getElementById(tabName);
    if (selectedTab) {
        selectedTab.classList.add('active');
    }
    
    // Mark button as active
    e.target.classList.add('active');
}

// Add product to cart
function addToCart(productId, productName) {
    console.log('addToCart called with productId:', productId);
    
    const qtyInput = document.getElementById('quantity');
    if (!qtyInput) {
        showNotification('Quantity field not found', 'error');
        return;
    }
    
    const quantity = parseInt(qtyInput.value);
    const button = document.getElementById('add-to-cart-btn');
    
    console.log('Button found:', button ? 'yes' : 'no');
    console.log('Quantity:', quantity);
    
    // Validate quantity
    if (isNaN(quantity) || quantity < 1) {
        showNotification('Please enter a valid quantity', 'warning');
        return;
    }
    
    // Disable button and show loading state
    button.disabled = true;
    const originalText = button.innerHTML;
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Adding...';
    
    // Verify addToCartUrl is defined
    if (typeof addToCartUrl === 'undefined') {
        console.error('addToCartUrl is not defined');
        showNotification('Configuration error. Please reload the page.', 'error');
        button.disabled = false;
        button.innerHTML = originalText;
        return;
    }
    
    console.log('Posting to URL:', addToCartUrl);
    console.log('CSRF Token:', getCookie('csrftoken') ? 'found' : 'not found');
    
    const form = new FormData();
    form.append('product_id', productId);
    form.append('quantity', quantity);

    fetch(addToCartUrl, {
        method: 'POST',
        body: form,
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => {
        console.log('Response status:', response.status);
        console.log('Response ok:', response.ok);
        
        // Handle authentication redirect
        if (response.status === 302 || response.redirected) {
            showNotification('Please log in to add items to cart', 'warning');
            window.location.href = '/users/login/';
            return null;
        }
        
        // Always try to parse JSON response
        return response.json().then(data => {
            console.log('Response data:', data);
            return {
                status: response.status,
                ok: response.ok,
                data: data
            };
        }).catch(e => {
            console.error('Failed to parse response:', e);
            return {
                status: response.status,
                ok: response.ok,
                data: null,
                parseError: true
            };
        });
    })
    .then(responseObj => {
        if (!responseObj) return; // If redirected
        
        const { status, ok, data, parseError } = responseObj;
        
        console.log('Processing response:', { status, ok, data, parseError });
        
        if (parseError) {
            throw new Error(`HTTP ${status}: Failed to parse response`);
        }
        
        if (!ok) {
            if (status === 401 || status === 403) {
                showNotification('Please log in to add items to cart', 'warning');
                window.location.href = '/users/login/';
                return;
            }
            throw new Error(data?.message || `HTTP ${status}: ${data?.error || 'Unknown error'}`);
        }
        
        if (data.success) {
            showNotification(data.message, 'success');
            updateCartCount(data.cart_count);
            // Reset quantity input
            qtyInput.value = 1;
        } else {
            showNotification(data.message || 'Failed to add item to cart', 'error');
        }
    })
    .catch(error => {
        console.error('Error adding to cart:', error);
        showNotification(error.message || 'Error adding to cart. Please try again.', 'error');
    })
    .finally(() => {
        // Re-enable button and restore text
        button.disabled = false;
        button.innerHTML = originalText;
    });
}

// Initialize event listeners on page load
document.addEventListener('DOMContentLoaded', function() {
    // Handle quantity input directly
    const qtyInput = document.getElementById('quantity');
    if (qtyInput) {
        qtyInput.addEventListener('change', function() {
            let value = parseInt(this.value);
            const maxStock = parseInt(this.max);
            
            // Validate input
            if (isNaN(value) || value < 1) {
                this.value = 1;
            } else if (value > maxStock) {
                this.value = maxStock;
                showNotification(`Maximum ${maxStock} items available`, 'warning');
            }
        });
        
        // Prevent non-numeric input
        qtyInput.addEventListener('input', function() {
            this.value = this.value.replace(/[^0-9]/g, '');
        });
    }
    
    // Image thumbnail click handler
    document.querySelectorAll('[data-change-image]').forEach(img => {
        img.addEventListener('click', function() {
            changeImage(this);
        });
    });
    
    // Quantity control handlers
    const qtyDecreaseBtn = document.getElementById('qty-decrease');
    if (qtyDecreaseBtn) {
        qtyDecreaseBtn.addEventListener('click', decreaseQty);
    }
    
    const qtyIncreaseBtn = document.getElementById('qty-increase');
    if (qtyIncreaseBtn) {
        qtyIncreaseBtn.addEventListener('click', function() {
            const maxStock = parseInt(this.dataset.maxStock) || 1;
            increaseQty(maxStock);
        });
    }
    
    // Add to cart button handler
    const addToCartBtn = document.getElementById('add-to-cart-btn');
    if (addToCartBtn) {
        addToCartBtn.addEventListener('click', function(e) {
            e.preventDefault();
            const productId = this.dataset.productId;
            const productName = this.dataset.productName;
            addToCart(productId, productName);
        });
    }
    
    // Tab button handlers
    document.querySelectorAll('[data-tab]').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const tabName = this.dataset.tab;
            
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // Remove active class from all buttons
            document.querySelectorAll('[data-tab]').forEach(b => {
                b.classList.remove('active');
            });
            
            // Show selected tab
            const selectedTab = document.getElementById(tabName);
            if (selectedTab) {
                selectedTab.classList.add('active');
            }
            
            // Mark button as active
            this.classList.add('active');
        });
    });
    
    // Add keyboard support for quantity
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && e.target.id === 'quantity') {
            const button = document.getElementById('add-to-cart-btn');
            if (button && !button.disabled) {
                button.click();
            }
        }
    });
});

// Export functions for global use
window.addToCart = addToCart;
window.changeImage = changeImage;
window.increaseQty = increaseQty;
window.decreaseQty = decreaseQty;
window.switchTab = switchTab;
window.showNotification = showNotification;
window.getCookie = getCookie;
