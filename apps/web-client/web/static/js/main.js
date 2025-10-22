// Main JavaScript for OpenDiscourse

// Initialize tooltips
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize Bootstrap popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Handle form submissions with loading states
    var forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function() {
            var submitButtons = form.querySelectorAll('button[type="submit"]');
            submitButtons.forEach(function(button) {
                button.disabled = true;
                var originalText = button.innerHTML;
                button.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading...';
                button.setAttribute('data-original-text', originalText);
            });
        });
    });
});

// Utility functions
function showAlert(message, type = 'info') {
    var alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    
    var alertContainer = document.querySelector('.container .alert-container') || 
                        document.querySelector('.container');
    
    if (alertContainer) {
        alertContainer.insertAdjacentHTML('afterbegin', alertHtml);
    }
}

function hideAlert() {
    var alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        var bsAlert = new bootstrap.Alert(alert);
        bsAlert.close();
    });
}

function formatNumber(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    }
    if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
}

function formatDate(dateString) {
    var date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

function truncateText(text, maxLength = 100) {
    if (text.length <= maxLength) {
        return text;
    }
    return text.substring(0, maxLength) + '...';
}

// API helper functions
function apiRequest(endpoint, options = {}) {
    var defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        },
    };
    
    var mergedOptions = Object.assign(defaultOptions, options);
    
    return fetch('/api' + endpoint, mergedOptions)
        .then(response => {
            if (!response.ok) {
                throw new Error('API request failed: ' + response.status);
            }
            return response.json();
        });
}

function getMember(memberId) {
    return apiRequest('/members/' + memberId);
}

function searchMembers(query, page = 1, perPage = 20) {
    return apiRequest('/members?page=' + page + '&per_page=' + perPage + '&search=' + encodeURIComponent(query));
}

function getDiscrepancies(page = 1, perPage = 20, filters = {}) {
    var params = new URLSearchParams();
    params.append('page', page);
    params.append('per_page', perPage);
    
    Object.keys(filters).forEach(key => {
        if (filters[key]) {
            params.append(key, filters[key]);
        }
    });
    
    return apiRequest('/discrepancies?' + params.toString());
}

function getStatistics() {
    return apiRequest('/statistics');
}

// Debounce function for search inputs
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Export functions for use in templates
window.openDiscourse = {
    showAlert: showAlert,
    hideAlert: hideAlert,
    formatNumber: formatNumber,
    formatDate: formatDate,
    truncateText: truncateText,
    api: {
        getMember: getMember,
        searchMembers: searchMembers,
        getDiscrepancies: getDiscrepancies,
        getStatistics: getStatistics
    },
    utils: {
        debounce: debounce
    }
};