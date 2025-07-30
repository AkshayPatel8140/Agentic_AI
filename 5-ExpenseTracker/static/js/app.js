/**
 * Main JavaScript file for Daily Expense & Income Tracker
 * Handles common functionality across all pages
 */

// Global app object
const ExpenseTracker = {
    // Configuration
    config: {
        apiBaseUrl: '/api',
        dateFormat: 'YYYY-MM-DD',
        currencySymbol: '$',
        animationDuration: 300
    },

    // Utility functions
    utils: {
        /**
         * Format currency amount
         * @param {number} amount - The amount to format
         * @returns {string} Formatted currency string
         */
        formatCurrency: function(amount) {
            return ExpenseTracker.config.currencySymbol + parseFloat(amount).toFixed(2);
        },

        /**
         * Format date for display
         * @param {string|Date} date - The date to format
         * @param {string} format - Format type ('short', 'long', 'relative')
         * @returns {string} Formatted date string
         */
        formatDate: function(date, format = 'short') {
            const dateObj = typeof date === 'string' ? new Date(date) : date;
            
            switch(format) {
                case 'short':
                    return dateObj.toLocaleDateString();
                case 'long':
                    return dateObj.toLocaleDateString('en-US', { 
                        weekday: 'long', 
                        year: 'numeric', 
                        month: 'long', 
                        day: 'numeric' 
                    });
                case 'relative':
                    return ExpenseTracker.utils.getRelativeDateString(dateObj);
                default:
                    return dateObj.toLocaleDateString();
            }
        },

        /**
         * Get relative date string (e.g., "today", "yesterday", "3 days ago")
         * @param {Date} date - The date to compare
         * @returns {string} Relative date string
         */
        getRelativeDateString: function(date) {
            const today = new Date();
            const diffTime = today - date;
            const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));

            if (diffDays === 0) return 'today';
            if (diffDays === 1) return 'yesterday';
            if (diffDays === -1) return 'tomorrow';
            if (diffDays > 1 && diffDays < 7) return `${diffDays} days ago`;
            if (diffDays < -1 && diffDays > -7) return `in ${Math.abs(diffDays)} days`;
            if (diffDays >= 7 && diffDays < 30) {
                const weeks = Math.floor(diffDays / 7);
                return `${weeks} week${weeks > 1 ? 's' : ''} ago`;
            }
            if (diffDays >= 30 && diffDays < 365) {
                const months = Math.floor(diffDays / 30);
                return `${months} month${months > 1 ? 's' : ''} ago`;
            }
            if (diffDays >= 365) {
                const years = Math.floor(diffDays / 365);
                return `${years} year${years > 1 ? 's' : ''} ago`;
            }
            
            return date.toLocaleDateString();
        },

        /**
         * Validate form data
         * @param {Object} data - Form data to validate
         * @param {Object} rules - Validation rules
         * @returns {Object} Validation result
         */
        validateForm: function(data, rules) {
            const errors = {};
            
            for (const field in rules) {
                const value = data[field];
                const rule = rules[field];
                
                if (rule.required && (!value || value.toString().trim() === '')) {
                    errors[field] = `${rule.label || field} is required`;
                    continue;
                }
                
                if (value && rule.type === 'number') {
                    const num = parseFloat(value);
                    if (isNaN(num)) {
                        errors[field] = `${rule.label || field} must be a valid number`;
                        continue;
                    }
                    if (rule.min !== undefined && num < rule.min) {
                        errors[field] = `${rule.label || field} must be at least ${rule.min}`;
                        continue;
                    }
                    if (rule.max !== undefined && num > rule.max) {
                        errors[field] = `${rule.label || field} cannot exceed ${rule.max}`;
                        continue;
                    }
                }
                
                if (value && rule.type === 'string') {
                    if (rule.minLength && value.length < rule.minLength) {
                        errors[field] = `${rule.label || field} must be at least ${rule.minLength} characters`;
                        continue;
                    }
                    if (rule.maxLength && value.length > rule.maxLength) {
                        errors[field] = `${rule.label || field} cannot exceed ${rule.maxLength} characters`;
                        continue;
                    }
                }
            }
            
            return {
                isValid: Object.keys(errors).length === 0,
                errors: errors
            };
        },

        /**
         * Debounce function calls
         * @param {Function} func - Function to debounce
         * @param {number} wait - Wait time in milliseconds
         * @returns {Function} Debounced function
         */
        debounce: function(func, wait) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        },

        /**
         * Show loading state on element
         * @param {HTMLElement} element - Element to show loading on
         * @param {boolean} show - Whether to show or hide loading
         */
        toggleLoading: function(element, show = true) {
            if (show) {
                element.classList.add('loading');
                element.disabled = true;
            } else {
                element.classList.remove('loading');
                element.disabled = false;
            }
        }
    },

    // API functions
    api: {
        /**
         * Make API request
         * @param {string} endpoint - API endpoint
         * @param {Object} options - Request options
         * @returns {Promise} API response
         */
        request: async function(endpoint, options = {}) {
            const url = ExpenseTracker.config.apiBaseUrl + endpoint;
            const defaultOptions = {
                headers: {
                    'Content-Type': 'application/json',
                },
            };
            
            const requestOptions = { ...defaultOptions, ...options };
            
            try {
                const response = await fetch(url, requestOptions);
                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.message || 'API request failed');
                }
                
                return data;
            } catch (error) {
                console.error('API Error:', error);
                throw error;
            }
        },

        /**
         * Add new transaction
         * @param {Object} transactionData - Transaction data
         * @returns {Promise} API response
         */
        addTransaction: function(transactionData) {
            return ExpenseTracker.api.request('/add_transaction', {
                method: 'POST',
                body: JSON.stringify(transactionData)
            });
        },

        /**
         * Update transaction
         * @param {number} id - Transaction ID
         * @param {Object} transactionData - Updated transaction data
         * @returns {Promise} API response
         */
        updateTransaction: function(id, transactionData) {
            return ExpenseTracker.api.request(`/update_transaction/${id}`, {
                method: 'PUT',
                body: JSON.stringify(transactionData)
            });
        },

        /**
         * Delete transaction
         * @param {number} id - Transaction ID
         * @returns {Promise} API response
         */
        deleteTransaction: function(id) {
            return ExpenseTracker.api.request(`/delete_transaction/${id}`, {
                method: 'DELETE'
            });
        },

        /**
         * Add new category
         * @param {Object} categoryData - Category data
         * @returns {Promise} API response
         */
        addCategory: function(categoryData) {
            return ExpenseTracker.api.request('/add_category', {
                method: 'POST',
                body: JSON.stringify(categoryData)
            });
        },

        /**
         * Delete category
         * @param {number} id - Category ID
         * @returns {Promise} API response
         */
        deleteCategory: function(id) {
            return ExpenseTracker.api.request(`/delete_category/${id}`, {
                method: 'DELETE'
            });
        },

        /**
         * Get dashboard data
         * @returns {Promise} API response
         */
        getDashboardData: function() {
            return ExpenseTracker.api.request('/dashboard_data');
        }
    },

    // UI functions
    ui: {
        /**
         * Show alert message
         * @param {string} message - Alert message
         * @param {string} type - Alert type (success, danger, warning, info)
         * @param {number} duration - Auto-hide duration in milliseconds
         */
        showAlert: function(message, type = 'info', duration = 5000) {
            const alertDiv = document.createElement('div');
            alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
            alertDiv.innerHTML = `
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            `;
            
            // Insert at the top of the main content
            const main = document.querySelector('main .container');
            if (main) {
                main.insertBefore(alertDiv, main.firstChild);
            }
            
            // Auto-remove after specified duration
            if (duration > 0) {
                setTimeout(() => {
                    if (alertDiv.parentNode) {
                        alertDiv.remove();
                    }
                }, duration);
            }
        },

        /**
         * Show confirmation dialog
         * @param {string} message - Confirmation message
         * @param {Function} onConfirm - Callback for confirmation
         * @param {Function} onCancel - Callback for cancellation
         */
        showConfirm: function(message, onConfirm, onCancel = null) {
            if (confirm(message)) {
                if (onConfirm) onConfirm();
            } else {
                if (onCancel) onCancel();
            }
        },

        /**
         * Update button loading state
         * @param {HTMLElement} button - Button element
         * @param {boolean} loading - Loading state
         * @param {string} loadingText - Text to show when loading
         */
        setButtonLoading: function(button, loading, loadingText = 'Loading...') {
            if (loading) {
                button.dataset.originalText = button.innerHTML;
                button.innerHTML = `<i class="bi bi-hourglass-split"></i> ${loadingText}`;
                button.disabled = true;
            } else {
                button.innerHTML = button.dataset.originalText || button.innerHTML;
                button.disabled = false;
            }
        },

        /**
         * Animate element
         * @param {HTMLElement} element - Element to animate
         * @param {string} animation - Animation class
         * @param {Function} callback - Callback after animation
         */
        animate: function(element, animation, callback = null) {
            element.classList.add('animate__animated', animation);
            
            const handleAnimationEnd = () => {
                element.classList.remove('animate__animated', animation);
                element.removeEventListener('animationend', handleAnimationEnd);
                if (callback) callback();
            };
            
            element.addEventListener('animationend', handleAnimationEnd);
        },

        /**
         * Update page title
         * @param {string} title - New page title
         */
        setPageTitle: function(title) {
            document.title = title + ' - Daily Expense & Income Tracker';
        }
    },

    // Event handlers
    events: {
        /**
         * Initialize global event listeners
         */
        init: function() {
            // Handle form submissions with loading states
            document.addEventListener('submit', function(e) {
                const form = e.target;
                if (form.classList.contains('api-form')) {
                    const submitBtn = form.querySelector('button[type="submit"]');
                    if (submitBtn) {
                        ExpenseTracker.ui.setButtonLoading(submitBtn, true);
                    }
                }
            });

            // Handle API errors globally
            window.addEventListener('unhandledrejection', function(e) {
                console.error('Unhandled API Error:', e.reason);
                ExpenseTracker.ui.showAlert('An unexpected error occurred. Please try again.', 'danger');
            });

            // Auto-hide alerts after 5 seconds
            document.addEventListener('DOMContentLoaded', function() {
                const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
                alerts.forEach(alert => {
                    setTimeout(() => {
                        if (alert.parentNode) {
                            alert.classList.remove('show');
                            setTimeout(() => alert.remove(), 150);
                        }
                    }, 5000);
                });
            });

            // Handle keyboard shortcuts
            document.addEventListener('keydown', function(e) {
                // Ctrl/Cmd + N: Add new transaction
                if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
                    e.preventDefault();
                    const addTransactionLink = document.querySelector('a[href*="add_transaction"]');
                    if (addTransactionLink) {
                        window.location.href = addTransactionLink.href;
                    }
                }
                
                // Escape: Close modals
                if (e.key === 'Escape') {
                    const openModals = document.querySelectorAll('.modal.show');
                    openModals.forEach(modal => {
                        const modalInstance = bootstrap.Modal.getInstance(modal);
                        if (modalInstance) {
                            modalInstance.hide();
                        }
                    });
                }
            });
        }
    },

    // Local storage functions
    storage: {
        /**
         * Save data to local storage
         * @param {string} key - Storage key
         * @param {*} data - Data to save
         */
        save: function(key, data) {
            try {
                localStorage.setItem('expense_tracker_' + key, JSON.stringify(data));
            } catch (error) {
                console.warn('Failed to save to localStorage:', error);
            }
        },

        /**
         * Load data from local storage
         * @param {string} key - Storage key
         * @param {*} defaultValue - Default value if not found
         * @returns {*} Stored data or default value
         */
        load: function(key, defaultValue = null) {
            try {
                const item = localStorage.getItem('expense_tracker_' + key);
                return item ? JSON.parse(item) : defaultValue;
            } catch (error) {
                console.warn('Failed to load from localStorage:', error);
                return defaultValue;
            }
        },

        /**
         * Remove data from local storage
         * @param {string} key - Storage key
         */
        remove: function(key) {
            try {
                localStorage.removeItem('expense_tracker_' + key);
            } catch (error) {
                console.warn('Failed to remove from localStorage:', error);
            }
        }
    },

    // Initialize the application
    init: function() {
        console.log('Expense Tracker initialized');
        ExpenseTracker.events.init();
        
        // Save user preferences
        const preferences = ExpenseTracker.storage.load('preferences', {
            theme: 'light',
            currency: 'USD',
            dateFormat: 'MM/DD/YYYY'
        });
        
        // Apply saved preferences
        if (preferences.theme === 'dark') {
            document.body.classList.add('dark-theme');
        }
    }
};

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    ExpenseTracker.init();
});

// Export for use in other scripts
window.ExpenseTracker = ExpenseTracker;

