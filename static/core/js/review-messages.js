// Review Message Management Functions

function closeMessage(button) {
    button.closest('.review-message').style.display = 'none';
}

function showSuccessMessage(message = 'Your review has been submitted successfully!') {
    const messageDiv = document.getElementById('review-success-message');
    document.getElementById('success-message-text').textContent = message;
    messageDiv.style.display = 'block';
    messageDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
    setTimeout(() => {
        messageDiv.style.display = 'none';
    }, 5000);
}

function showErrorMessage(message = 'An error occurred while submitting your review.', errors = null) {
    const messageDiv = document.getElementById('review-error-message');
    document.getElementById('error-message-text').textContent = message;
    
    if (errors) {
        const errorList = document.getElementById('error-list');
        const errorDetails = document.getElementById('error-details');
        errorList.innerHTML = '';
        
        for (const [field, errorArray] of Object.entries(errors)) {
            if (Array.isArray(errorArray)) {
                errorArray.forEach(error => {
                    const li = document.createElement('li');
                    li.textContent = `${field}: ${error}`;
                    errorList.appendChild(li);
                });
            }
        }
        errorDetails.style.display = 'block';
    } else {
        document.getElementById('error-details').style.display = 'none';
    }
    
    messageDiv.style.display = 'block';
    messageDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

function showInfoMessage(message = 'You have already reviewed this product.') {
    const messageDiv = document.getElementById('review-info-message');
    document.getElementById('info-message-text').textContent = message;
    messageDiv.style.display = 'block';
    messageDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
    setTimeout(() => {
        messageDiv.style.display = 'none';
    }, 5000);
}

function showModerationMessage(message = 'Your review has been submitted and will appear after moderation.') {
    const messageDiv = document.getElementById('review-moderation-message');
    document.getElementById('moderation-message-text').textContent = message;
    messageDiv.style.display = 'block';
    messageDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
    setTimeout(() => {
        messageDiv.style.display = 'none';
    }, 5000);
}
