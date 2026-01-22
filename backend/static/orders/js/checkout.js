/* Checkout Page JavaScript */

document.addEventListener('DOMContentLoaded', function() {
    // Payment method toggle
    document.querySelectorAll('input[name="payment"]').forEach(input => {
        input.addEventListener('change', function() {
            const cardDetails = document.getElementById('card-details');
            if (this.value === 'credit_card') {
                cardDetails.style.display = 'block';
            } else {
                cardDetails.style.display = 'none';
            }
        });
    });

    // Initialize card details visibility
    const cardDetails = document.getElementById('card-details');
    if (cardDetails) {
        const checkedPayment = document.querySelector('input[name="payment"]:checked');
        if (checkedPayment && checkedPayment.value !== 'credit_card') {
            cardDetails.style.display = 'none';
        }
    }

    // Form validation
    const checkoutForm = document.querySelector('.checkout-form');
    if (checkoutForm) {
        checkoutForm.addEventListener('submit', function(e) {
            const terms = document.querySelector('input[name="terms"]');
            if (terms && !terms.checked) {
                e.preventDefault();
                alert('Please agree to the Terms of Service and Privacy Policy');
            }
        });
    }
});
