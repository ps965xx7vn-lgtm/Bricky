

// Review System Functions
class ReviewSystem {
    constructor(productId) {
        this.productId = productId;
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Rating input handling
        const ratingInput = document.getElementById(`rating-input-${this.productId}`);
        if (ratingInput) {
            const radioButtons = ratingInput.querySelectorAll('input[type="radio"]');
            radioButtons.forEach((radio, index) => {
                radio.addEventListener('change', (e) => this.updateRatingDisplay(index + 1, ratingInput));
                radio.addEventListener('mouseover', (e) => this.previewRating(index + 1, ratingInput));
            });
            ratingInput.addEventListener('mouseleave', () => this.resetRatingDisplay(ratingInput));
        }

        // Form submission
        const reviewForm = document.getElementById(`review-form-${this.productId}`);
        if (reviewForm) {
            reviewForm.addEventListener('submit', (e) => this.submitReview(e));
        }

        // Helpful/Unhelpful buttons
        const helpfulButtons = document.querySelectorAll('.helpful-btn');
        const unhelpfulButtons = document.querySelectorAll('.unhelpful-btn');
        
        helpfulButtons.forEach(btn => btn.addEventListener('click', (e) => this.markHelpful(e)));
        unhelpfulButtons.forEach(btn => btn.addEventListener('click', (e) => this.markUnhelpful(e)));
    }

    updateRatingDisplay(rating, container) {
        const stars = container.querySelectorAll('.star-label');
        stars.forEach((star, index) => {
            if (index < rating) {
                star.style.color = '#ffc107';
                star.style.opacity = '1';
            } else {
                star.style.color = '#ccc';
                star.style.opacity = '1';
            }
        });
    }

    previewRating(rating, container) {
        this.updateRatingDisplay(rating, container);
    }

    resetRatingDisplay(container) {
        const checkedRadio = container.querySelector('input[type="radio"]:checked');
        if (checkedRadio) {
            this.updateRatingDisplay(checkedRadio.value, container);
        } else {
            const stars = container.querySelectorAll('.star-label');
            stars.forEach(star => {
                star.style.color = '#ccc';
                star.style.opacity = '1';
            });
        }
    }

    submitReview(e) {
        e.preventDefault();
        const form = e.target;
        const formData = new FormData(form);

        // Validate rating
        const rating = form.querySelector('input[name="rating"]:checked');
        if (!rating) {
            showErrorMessage('Please select a rating');
            return;
        }

        fetch(form.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showModerationMessage(data.message);
                form.reset();
                // Reload reviews after short delay
                setTimeout(() => location.reload(), 3000);
            } else {
                if (data.errors) {
                    showErrorMessage(data.message || 'Please fix the errors below.', data.errors);
                } else {
                    showErrorMessage(data.message || 'Failed to submit review');
                }
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showErrorMessage('An error occurred while submitting your review');
        });
    }

    markHelpful(e) {
        e.preventDefault();
        const button = e.target.closest('.helpful-btn');
        const reviewId = button.dataset.reviewId;
        this.markReviewFeedback(reviewId, 'helpful', button);
    }

    markUnhelpful(e) {
        e.preventDefault();
        const button = e.target.closest('.unhelpful-btn');
        const reviewId = button.dataset.reviewId;
        this.markReviewFeedback(reviewId, 'unhelpful', button);
    }

    markReviewFeedback(reviewId, action, button) {
        const formData = new FormData();
        formData.append('action', action);

        fetch(`/core/review/${reviewId}/helpful/`, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const reviewDiv = document.getElementById(`review-${reviewId}`);
                if (action === 'helpful') {
                    const helpfulCountSpan = button.querySelector('.helpful-count');
                    helpfulCountSpan.textContent = data.helpful_count;
                } else {
                    const unhelpfulCountSpan = button.querySelector('.unhelpful-count');
                    unhelpfulCountSpan.textContent = data.unhelpful_count;
                }
                button.disabled = true;
                button.style.opacity = '0.5';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showErrorMessage('Failed to record your feedback');
        });
    }
}

// Initialize review system when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Get product ID from the page
    const addToCartBtn = document.querySelector('[data-product-id]');
    if (addToCartBtn) {
        const productId = addToCartBtn.dataset.productId;
        window.reviewSystem = new ReviewSystem(productId);
    }
});
