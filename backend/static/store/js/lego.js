/* ============================================
   BRICKY LEGO STORE - Professional JavaScript
   ============================================ */

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

// Add to cart via AJAX
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

// Update cart count in navbar
function updateCartCount(count) {
    const cartCount = document.querySelector('.cart-count');
    if (cartCount) {
        cartCount.textContent = count;
    }
}

// Notify me when back in stock
function notifyMe(productId) {
    showNotification('We\'ll notify you when this item is back in stock!', 'info');
    console.log('Notification request for product:', productId);
}

// Show notification
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        bottom: 20px;
        left: 20px;
        padding: 16px 24px;
        background: ${type === 'success' ? '#4caf50' : type === 'error' ? '#f44336' : type === 'warning' ? '#ff9800' : '#2196f3'};
        color: white;
        border-radius: 4px;
        z-index: 1000;
        animation: slideUp 0.3s ease;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        max-width: 300px;
    `;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideDown 0.3s ease forwards';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Handle newsletter submission
function handleNewsletter(e) {
    e.preventDefault();
    const email = e.target.querySelector('input[type="email"]').value;
    showNotification(`Thanks! We'll send updates to ${email}`, 'success');
    e.target.reset();
}

// Mobile navigation toggle
function setupMobileNav() {
    const hamburger = document.querySelector('.hamburger');
    const navLinks = document.querySelector('.nav-links');
    
    if (hamburger) {
        hamburger.addEventListener('click', () => {
            navLinks.classList.toggle('active');
        });
        
        // Close menu when link is clicked
        document.querySelectorAll('.nav-links a').forEach(link => {
            link.addEventListener('click', () => {
                navLinks.classList.remove('active');
            });
        });
    }
}

// Auto-submit filters on change
function setupFilters() {
    const filterForm = document.querySelector('.filter-controls');
    if (!filterForm) return;
    
    filterForm.querySelectorAll('select').forEach(select => {
        select.addEventListener('change', () => {
            // Auto submit on select change
            const applyBtn = filterForm.querySelector('.apply-btn');
            if (applyBtn) {
                applyBtn.click();
            }
        });
    });
}

// Back to top button
function setupBackToTop() {
    const backToTopBtn = document.getElementById('back-to-top');
    if (!backToTopBtn) return;
    
    window.addEventListener('scroll', () => {
        if (window.scrollY > 300) {
            backToTopBtn.classList.add('show');
        } else {
            backToTopBtn.classList.remove('show');
        }
    });
    
    // Add click listener to back-to-top button
    backToTopBtn.addEventListener('click', backToTop);
}

function backToTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupMobileNav();
    setupFilters();
    setupBackToTop();
    
    // Add animations on scroll
    observeElements();
});

// Observe elements for animation
function observeElements() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, { threshold: 0.1 });
    
    document.querySelectorAll('.product-card, .category-card, .feature').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'all 0.6s ease';
        observer.observe(el);
    });
}

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Ctrl+T or Cmd+T for top
    if ((e.ctrlKey || e.metaKey) && e.key === 't') {
        e.preventDefault();
        backToTop();
    }
});

// Add animation styles
const style = document.createElement('style');
style.textContent = `
    @keyframes slideUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideDown {
        from {
            opacity: 1;
            transform: translateY(0);
        }
        to {
            opacity: 0;
            transform: translateY(20px);
        }
    }
`;
document.head.appendChild(style);
