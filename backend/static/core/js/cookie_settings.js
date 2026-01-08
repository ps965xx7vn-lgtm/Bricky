function toggleCookie(type) {
    const toggle = document.getElementById(type + '-toggle');
    toggle.classList.toggle('active');
}

function acceptAllCookies() {
    document.getElementById('analytics-toggle').classList.add('active');
    document.getElementById('marketing-toggle').classList.add('active');
    document.getElementById('preference-toggle').classList.add('active');
    
    localStorage.setItem('analytics_cookies', 'true');
    localStorage.setItem('marketing_cookies', 'true');
    localStorage.setItem('preference_cookies', 'true');
    
    alert('All cookies accepted. Thank you!');
}

function rejectNonEssentialCookies() {
    document.getElementById('analytics-toggle').classList.remove('active');
    document.getElementById('marketing-toggle').classList.remove('active');
    document.getElementById('preference-toggle').classList.remove('active');
    
    localStorage.setItem('analytics_cookies', 'false');
    localStorage.setItem('marketing_cookies', 'false');
    localStorage.setItem('preference_cookies', 'false');
    
    alert('Non-essential cookies rejected.');
}

function saveCookiePreferences() {
    const analytics = document.getElementById('analytics-toggle').classList.contains('active');
    const marketing = document.getElementById('marketing-toggle').classList.contains('active');
    const preference = document.getElementById('preference-toggle').classList.contains('active');
    
    localStorage.setItem('analytics_cookies', analytics);
    localStorage.setItem('marketing_cookies', marketing);
    localStorage.setItem('preference_cookies', preference);
    
    alert('Your cookie preferences have been saved!');
}

// Load preferences on page load
window.addEventListener('load', function() {
    if (localStorage.getItem('analytics_cookies') === 'true') {
        document.getElementById('analytics-toggle').classList.add('active');
    }
    if (localStorage.getItem('marketing_cookies') === 'true') {
        document.getElementById('marketing-toggle').classList.add('active');
    }
    if (localStorage.getItem('preference_cookies') === 'true') {
        document.getElementById('preference-toggle').classList.add('active');
    }
});

// Event listeners for toggle switches
document.addEventListener('DOMContentLoaded', function() {
    const analyticsToggle = document.getElementById('analytics-toggle');
    if (analyticsToggle) {
        analyticsToggle.addEventListener('click', function() {
            toggleCookie('analytics');
        });
    }
    
    const marketingToggle = document.getElementById('marketing-toggle');
    if (marketingToggle) {
        marketingToggle.addEventListener('click', function() {
            toggleCookie('marketing');
        });
    }
    
    const preferenceToggle = document.getElementById('preference-toggle');
    if (preferenceToggle) {
        preferenceToggle.addEventListener('click', function() {
            toggleCookie('preference');
        });
    }
    
    // Button handlers
    const acceptAllBtn = document.querySelector('.btn-accept-all');
    if (acceptAllBtn) {
        acceptAllBtn.addEventListener('click', acceptAllCookies);
    }
    
    const rejectAllBtn = document.querySelector('.btn-reject-all');
    if (rejectAllBtn) {
        rejectAllBtn.addEventListener('click', rejectNonEssentialCookies);
    }
    
    const saveBtn = document.querySelector('.btn-save');
    if (saveBtn) {
        saveBtn.addEventListener('click', saveCookiePreferences);
    }
});

// Export functions for global use
window.toggleCookie = toggleCookie;
window.acceptAllCookies = acceptAllCookies;
window.rejectNonEssentialCookies = rejectNonEssentialCookies;
window.saveCookiePreferences = saveCookiePreferences;
