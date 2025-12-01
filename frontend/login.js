/**
 * Login page functionality
 * Handles OAuth provider selection and error display
 */

const API_BASE_URL = 'http://localhost:8000';

// Check for error parameter in URL
window.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    const error = urlParams.get('error');

    if (error) {
        showError(decodeURIComponent(error));
    }
});

/**
 * Initiate login with specified OAuth provider
 */
function loginWithProvider(provider) {
    // Hide any existing errors
    hideError();

    // Show loading state
    showLoading();

    // Redirect to backend OAuth endpoint
    window.location.href = `${API_BASE_URL}/auth/login/${provider}`;
}

/**
 * Show loading state
 */
function showLoading() {
    const loadingState = document.getElementById('loadingState');
    const socialButtons = document.querySelector('.social-buttons');

    if (loadingState && socialButtons) {
        socialButtons.style.opacity = '0.5';
        socialButtons.style.pointerEvents = 'none';
        loadingState.classList.remove('hidden');
    }
}

/**
 * Hide loading state
 */
function hideLoading() {
    const loadingState = document.getElementById('loadingState');
    const socialButtons = document.querySelector('.social-buttons');

    if (loadingState && socialButtons) {
        socialButtons.style.opacity = '1';
        socialButtons.style.pointerEvents = 'auto';
        loadingState.classList.add('hidden');
    }
}

/**
 * Show error message
 */
function showError(message) {
    const errorMessage = document.getElementById('errorMessage');
    const errorText = document.getElementById('errorText');

    if (errorMessage && errorText) {
        errorText.textContent = message;
        errorMessage.classList.remove('hidden');
        hideLoading();
    }
}

/**
 * Hide error message
 */
function hideError() {
    const errorMessage = document.getElementById('errorMessage');

    if (errorMessage) {
        errorMessage.classList.add('hidden');
    }
}
