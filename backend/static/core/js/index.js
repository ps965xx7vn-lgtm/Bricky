/* Index Page JavaScript */

document.addEventListener('DOMContentLoaded', function() {
    // Add to cart button handlers
    document.querySelectorAll('.add-to-cart-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            addToCart(this.dataset.productId, this.dataset.productName);
        });
    });

    // Notify me button handlers
    document.querySelectorAll('.notify-me-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            notifyMe(this.dataset.productId);
        });
    });

    // Newsletter form handler
    const newsletterForm = document.getElementById('newsletter-form');
    if (newsletterForm) {
        newsletterForm.addEventListener('submit', handleNewsletter);
    }
});

// Add to cart function
function addToCart(productId, productName) {
    const form = new FormData();
    form.append('product_id', productId);
    form.append('quantity', 1);

    fetch("/orders/cart/add/", {
        method: 'POST',
        body: form,
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification(productName + ' added to cart', 'success');
            updateCartCount(data.cart_count);
        } else if (data.requires_login) {
            showNotification('Please log in or register to add items to cart', 'info');
            // Optionally redirect to login page
            setTimeout(() => {
                window.location.href = '/users/login/?next=' + window.location.pathname;
            }, 1500);
        } else {
            showNotification(data.message || 'Failed to add to cart', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Error adding to cart', 'error');
    });
}

// Notify me function (placeholder)
function notifyMe(productId) {
    showNotification('We will notify you when this item is back in stock', 'info');
}

// Handle newsletter subscription
function handleNewsletter(event) {
    event.preventDefault();
    const form = event.target;
    const email = form.querySelector('input[type="email"]').value;
    
    // Send newsletter subscription request
    fetch('/core/newsletter-subscribe/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ email: email })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Successfully subscribed to newsletter!', 'success');
            form.reset();
        } else {
            showNotification(data.message || 'Failed to subscribe', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Error subscribing to newsletter', 'error');
    });
}
