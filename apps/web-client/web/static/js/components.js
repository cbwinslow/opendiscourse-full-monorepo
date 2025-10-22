// Enhanced UI Components for OpenDiscourse

// Initialize components when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeComponents();
});

function initializeComponents() {
    // Initialize all components
    initializeTooltips();
    initializePopovers();
    initializeTabs();
    initializeModals();
    initializeCharts();
    initializeSearch();
}

// Tooltip initialization
function initializeTooltips() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Popover initialization
function initializePopovers() {
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

// Tab initialization
function initializeTabs() {
    var triggerTabList = [].slice.call(document.querySelectorAll('#profileTabs button'));
    triggerTabList.forEach(function (triggerEl) {
        var tabTrigger = new bootstrap.Tab(triggerEl);
        
        triggerEl.addEventListener('click', function (event) {
            event.preventDefault();
            tabTrigger.show();
        });
    });
}

// Modal initialization
function initializeModals() {
    // Handle modal events
    document.querySelectorAll('.modal').forEach(function(modalElement) {
        modalElement.addEventListener('show.bs.modal', function(event) {
            // Handle modal show event
            console.log('Modal shown:', modalElement.id);
        });
    });
}

// Chart initialization
function initializeCharts() {
    // This would initialize any charting libraries like Chart.js
    // For now, we'll just log that charts are ready
    console.log('Chart components ready');
}

// Enhanced search functionality
function initializeSearch() {
    // Handle search form submissions
    var searchForms = document.querySelectorAll('#advanced-search-form, #search-form, #filter-form');
    searchForms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            handleSearchSubmission(e, form);
        });
    });
    
    // Handle search input with debounce
    var searchInputs = document.querySelectorAll('#search-input, #search-query');
    searchInputs.forEach(function(input) {
        input.addEventListener('input', debounce(function(e) {
            handleSearchInput(e.target);
        }, 300));
    });
}

function handleSearchSubmission(e, form) {
    // Add loading states to search buttons
    var submitButtons = form.querySelectorAll('button[type="submit"]');
    submitButtons.forEach(function(button) {
        button.disabled = true;
        var originalHTML = button.innerHTML;
        button.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Searching...';
        button.setAttribute('data-original-html', originalHTML);
    });
    
    // Re-enable buttons after a delay (in case of errors)
    setTimeout(function() {
        submitButtons.forEach(function(button) {
            if (button.hasAttribute('data-original-html')) {
                button.innerHTML = button.getAttribute('data-original-html');
                button.removeAttribute('data-original-html');
                button.disabled = false;
            }
        });
    }, 5000);
}

function handleSearchInput(inputElement) {
    // Handle real-time search input (autocomplete, suggestions, etc.)
    var query = inputElement.value.trim();
    if (query.length > 2) {
        // In a real implementation, this would fetch search suggestions
        console.log('Search query:', query);
    }
}

// Pagination component
function updatePagination(containerId, paginationData, onPageChangeCallback) {
    var container = document.getElementById(containerId);
    if (!container) return;
    
    var html = '';
    
    if (paginationData.pages > 1) {
        // Previous button
        html += `
            <li class="page-item ${paginationData.page === 1 ? 'disabled' : ''}">
                <a class="page-link" href="#" data-page="${paginationData.page - 1}">
                    <i class="fas fa-chevron-left"></i>
                </a>
            </li>
        `;
        
        // Page numbers
        for (let i = 1; i <= paginationData.pages; i++) {
            if (i === 1 || i === paginationData.pages || (i >= paginationData.page - 2 && i <= paginationData.page + 2)) {
                html += `
                    <li class="page-item ${i === paginationData.page ? 'active' : ''}">
                        <a class="page-link" href="#" data-page="${i}">${i}</a>
                    </li>
                `;
            } else if (i === paginationData.page - 3 || i === paginationData.page + 3) {
                html += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
            }
        }
        
        // Next button
        html += `
            <li class="page-item ${paginationData.page === paginationData.pages ? 'disabled' : ''}">
                <a class="page-link" href="#" data-page="${paginationData.page + 1}">
                    <i class="fas fa-chevron-right"></i>
                </a>
            </li>
        `;
    }
    
    container.innerHTML = html;
    
    // Add event listeners to pagination links
    container.querySelectorAll('.page-link').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const page = parseInt(this.getAttribute('data-page'));
            if (!isNaN(page) && onPageChangeCallback) {
                onPageChangeCallback(page);
            }
        });
    });
}

// Alert component
function showAlert(message, type = 'info', containerSelector = '.container', autoDismiss = true) {
    var alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show alert-with-icon" role="alert">
            ${type === 'success' ? '<i class="fas fa-check-circle"></i>' : 
              type === 'warning' ? '<i class="fas fa-exclamation-triangle"></i>' : 
              type === 'danger' ? '<i class="fas fa-exclamation-circle"></i>' : 
              '<i class="fas fa-info-circle"></i>'}
            <div>${message}</div>
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    
    var container = document.querySelector(containerSelector) || document.querySelector('.container');
    if (container) {
        container.insertAdjacentHTML('afterbegin', alertHtml);
    }
    
    // Auto-dismiss success alerts after 5 seconds
    if (autoDismiss && type === 'success') {
        setTimeout(function() {
            var alerts = document.querySelectorAll('.alert-success');
            alerts.forEach(function(alert) {
                if (alert.classList.contains('show')) {
                    var bsAlert = new bootstrap.Alert(alert);
                    bsAlert.close();
                }
            });
        }, 5000);
    }
}

// Loading spinner component
function showLoadingSpinner(containerSelector) {
    var container = document.querySelector(containerSelector);
    if (container) {
        container.innerHTML = `
            <div class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-2">Loading...</p>
            </div>
        `;
    }
}

function hideLoadingSpinner(containerSelector) {
    var container = document.querySelector(containerSelector);
    if (container) {
        container.innerHTML = '';
    }
}

// Debounce function
function debounce(func, wait, immediate) {
    var timeout;
    return function() {
        var context = this, args = arguments;
        var later = function() {
            timeout = null;
            if (!immediate) func.apply(context, args);
        };
        var callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func.apply(context, args);
    };
}

// Format numbers for display
function formatNumber(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    }
    if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
}

// Format dates for display
function formatDate(dateString) {
    if (!dateString) return '';
    var date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

// Truncate text
function truncateText(text, maxLength = 100) {
    if (!text) return '';
    if (text.length <= maxLength) {
        return text;
    }
    return text.substring(0, maxLength) + '...';
}

// Export components
window.openDiscourseUI = {
    showAlert: showAlert,
    showLoadingSpinner: showLoadingSpinner,
    hideLoadingSpinner: hideLoadingSpinner,
    updatePagination: updatePagination,
    formatNumber: formatNumber,
    formatDate: formatDate,
    truncateText: truncateText,
    debounce: debounce
};