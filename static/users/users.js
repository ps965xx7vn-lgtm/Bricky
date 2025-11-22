/* Users App JavaScript - Authentication and Profile Management */

// Form Validation
class FormValidator {
    constructor(formSelector) {
        this.form = document.querySelector(formSelector);
        this.init();
    }

    init() {
        if (!this.form) return;
        this.form.addEventListener('submit', (e) => this.handleSubmit(e));
        this.setupFieldValidation();
    }

    setupFieldValidation() {
        const inputs = this.form.querySelectorAll('input, textarea');
        inputs.forEach(input => {
            input.addEventListener('blur', () => this.validateField(input));
            input.addEventListener('focus', () => this.clearFieldError(input));
        });
    }

    validateField(field) {
        const value = field.value.trim();
        const fieldName = field.name;
        let isValid = true;

        // Required field check
        if (field.hasAttribute('required') && !value) {
            this.showFieldError(field, 'This field is required');
            return false;
        }

        // Email validation
        if (field.type === 'email' && value) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(value)) {
                this.showFieldError(field, 'Please enter a valid email address');
                return false;
            }
        }

        // Password validation
        if (fieldName === 'password' && value) {
            if (value.length < 8) {
                this.showFieldError(field, 'Password must be at least 8 characters long');
                return false;
            }
        }

        // Confirm password check
        if (fieldName === 'confirm_password') {
            const passwordField = this.form.querySelector('[name="password"]');
            if (passwordField && passwordField.value !== value) {
                this.showFieldError(field, 'Passwords do not match');
                return false;
            }
        }

        this.clearFieldError(field);
        return true;
    }

    showFieldError(field, message) {
        this.clearFieldError(field);
        field.classList.add('error');
        const errorEl = document.createElement('span');
        errorEl.className = 'error-message';
        errorEl.textContent = message;
        field.parentElement.appendChild(errorEl);
    }

    clearFieldError(field) {
        field.classList.remove('error');
        const errorEl = field.parentElement.querySelector('.error-message');
        if (errorEl) {
            errorEl.remove();
        }
    }

    handleSubmit(e) {
        const inputs = this.form.querySelectorAll('input, textarea');
        let formIsValid = true;

        inputs.forEach(input => {
            if (!this.validateField(input)) {
                formIsValid = false;
            }
        });

        if (!formIsValid) {
            e.preventDefault();
        }
    }
}

// Profile Image Preview
class ImagePreview {
    constructor(inputSelector, previewSelector) {
        this.input = document.querySelector(inputSelector);
        this.preview = document.querySelector(previewSelector);
        this.init();
    }

    init() {
        if (!this.input) return;
        this.input.addEventListener('change', (e) => this.handleImageChange(e));
    }

    handleImageChange(event) {
        const file = event.target.files[0];
        if (!file) return;

        // Validate file type
        if (!file.type.startsWith('image/')) {
            alert('Please select an image file');
            event.target.value = '';
            return;
        }

        // Validate file size (max 5MB)
        if (file.size > 5 * 1024 * 1024) {
            alert('File size must be less than 5MB');
            event.target.value = '';
            return;
        }

        // Create preview
        const reader = new FileReader();
        reader.onload = (e) => {
            if (this.preview) {
                this.preview.src = e.target.result;
            }
        };
        reader.readAsDataURL(file);
    }
}

// Password Visibility Toggle
class PasswordToggle {
    constructor() {
        this.init();
    }

    init() {
        const passwordFields = document.querySelectorAll('input[type="password"]');
        passwordFields.forEach((field, index) => {
            const toggleBtn = document.createElement('button');
            toggleBtn.type = 'button';
            toggleBtn.className = 'password-toggle-btn';
            toggleBtn.innerHTML = '<i class="fas fa-eye"></i>';
            toggleBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.togglePassword(field, toggleBtn);
            });
            field.parentElement.appendChild(toggleBtn);
        });
    }

    togglePassword(field, btn) {
        if (field.type === 'password') {
            field.type = 'text';
            btn.innerHTML = '<i class="fas fa-eye-slash"></i>';
        } else {
            field.type = 'password';
            btn.innerHTML = '<i class="fas fa-eye"></i>';
        }
    }
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    // Initialize form validators
    new FormValidator('form');

    // Initialize image preview
    new ImagePreview('input[name="picture"]', '.profile-avatar');

    // Initialize password toggle
    new PasswordToggle();

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', (e) => {
            e.preventDefault();
            const target = document.querySelector(anchor.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });
});

// Show notification message
function showNotification(message, type = 'success', duration = 4000) {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    document.body.appendChild(notification);

    setTimeout(() => {
        notification.classList.add('show');
    }, 100);

    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, duration);
}
