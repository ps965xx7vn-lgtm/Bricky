/**
 * Newsletter Subscription Handler
 */

document.addEventListener('DOMContentLoaded', function() {
    // Handle newsletter form on index page
    const newsletterForm = document.getElementById('newsletter-form');
    const newsletterMessage = document.getElementById('newsletter-message');

    if (newsletterForm) {
        newsletterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            handleNewsletterSubmit(this, newsletterMessage);
        });
    }

    // Handle newsletter form on product detail page
    const productNewsletterForm = document.getElementById('newsletter-form-product');
    const productNewsletterMessage = document.getElementById('newsletter-message-product');

    if (productNewsletterForm) {
        productNewsletterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            handleNewsletterSubmit(this, productNewsletterMessage);
        });
    }
});

/**
 * Handle newsletter form submission via AJAX
 * @param {HTMLFormElement} form - The form element
 * @param {HTMLElement} messageElement - Element to display messages
 */
function handleNewsletterSubmit(form, messageElement) {
    const emailInput = form.querySelector('input[name="email"]');
    const submitButton = form.querySelector('button[type="submit"]');
    const email = emailInput.value.trim().toLowerCase();

    if (!email) {
        showMessage(messageElement, 'Please enter a valid email address.', 'error');
        return;
    }

    // Disable button and show loading state
    submitButton.disabled = true;
    const originalText = submitButton.textContent;
    submitButton.textContent = 'Subscribing...';

    // Send AJAX request
    fetch(form.action, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: JSON.stringify({
            email: email
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showMessage(messageElement, data.message || 'Successfully subscribed to our newsletter!', 'success');
            emailInput.value = '';
            emailInput.placeholder = 'Thank you for subscribing!';
            
            // Optional: Redirect after 2 seconds
            setTimeout(() => {
                window.location.href = '/newsletter/success/';
            }, 2000);
        } else {
            showMessage(messageElement, data.message || 'An error occurred. Please try again.', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showMessage(messageElement, 'An error occurred. Please try again.', 'error');
    })
    .finally(() => {
        // Re-enable button
        submitButton.disabled = false;
        submitButton.textContent = originalText;
    });
}

/**
 * Display message in the message element
 * @param {HTMLElement} element - The element to display the message in
 * @param {string} message - The message text
 * @param {string} type - The message type ('success' or 'error')
 */
function showMessage(element, message, type) {
    if (!element) return;

    element.textContent = message;
    element.style.padding = '12px 15px';
    element.style.borderRadius = '6px';
    element.style.fontSize = '14px';
    element.style.fontWeight = '500';
    element.style.animation = 'fadeIn 0.3s ease';

    if (type === 'success') {
        element.style.backgroundColor = '#d4edda';
        element.style.color = '#155724';
        element.style.border = '1px solid #c3e6cb';
    } else if (type === 'error') {
        element.style.backgroundColor = '#f8d7da';
        element.style.color = '#721c24';
        element.style.border = '1px solid #f5c6cb';
    }

    // Auto-clear error messages after 5 seconds
    if (type === 'error') {
        setTimeout(() => {
            element.textContent = '';
            element.style.backgroundColor = '';
            element.style.color = '';
            element.style.border = '';
        }, 5000);
    }
}

// Add fade-in animation
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(-10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
`;
document.head.appendChild(style);
