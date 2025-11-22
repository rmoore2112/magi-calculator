/**
 * MAGI Calculator - Data Persistence Module
 * Handles saving and loading user form data to/from browser localStorage
 */

const MAGIPersistence = {
    STORAGE_KEY: 'magi_calculator_user_data',
    VERSION: '1.0',

    /**
     * Get all form field IDs that should be persisted
     */
    getFormFields: function() {
        return [
            'filing_status',
            'tax_year',
            'target_magi',
            'wages',
            'business_income',
            'rental_income',
            'retirement_income',
            'social_security',
            'other_income',
            'tax_exempt_interest',
            'itemized_deductions',
            'student_loan_interest',
            'ira_contributions',
            'hsa_contributions',
            'self_employment_tax',
            'other_adjustments'
        ];
    },

    /**
     * Get the radio button value for deduction type
     */
    getDeductionType: function() {
        const radios = document.querySelectorAll('input[name="use_standard_deduction"]');
        for (const radio of radios) {
            if (radio.checked) {
                return radio.value;
            }
        }
        return 'true'; // Default
    },

    /**
     * Set the radio button value for deduction type
     */
    setDeductionType: function(value) {
        const radios = document.querySelectorAll('input[name="use_standard_deduction"]');
        for (const radio of radios) {
            if (radio.value === value) {
                radio.checked = true;
                // Trigger change event to show/hide itemized deductions field
                radio.dispatchEvent(new Event('change'));
            }
        }
    },

    /**
     * Save current form data to localStorage
     */
    saveData: function() {
        if (!this.isLocalStorageAvailable()) {
            console.warn('localStorage is not available');
            return false;
        }

        try {
            const data = {
                version: this.VERSION,
                timestamp: new Date().toISOString(),
                use_standard_deduction: this.getDeductionType()
            };

            // Collect all form field values
            this.getFormFields().forEach(fieldId => {
                const element = document.getElementById(fieldId);
                if (element) {
                    data[fieldId] = element.value;
                }
            });

            localStorage.setItem(this.STORAGE_KEY, JSON.stringify(data));
            console.log('Data saved successfully');
            return true;
        } catch (e) {
            console.error('Error saving data:', e);
            return false;
        }
    },

    /**
     * Load saved data from localStorage
     */
    loadData: function() {
        if (!this.isLocalStorageAvailable()) {
            console.warn('localStorage is not available');
            return null;
        }

        try {
            const dataStr = localStorage.getItem(this.STORAGE_KEY);
            if (!dataStr) {
                console.log('No saved data found');
                return null;
            }

            const data = JSON.parse(dataStr);

            // Version check (for future compatibility)
            if (data.version !== this.VERSION) {
                console.warn('Data version mismatch, ignoring saved data');
                return null;
            }

            console.log('Data loaded successfully');
            return data;
        } catch (e) {
            console.error('Error loading data:', e);
            return null;
        }
    },

    /**
     * Populate form fields with saved data
     */
    populateForm: function(data) {
        if (!data) {
            return false;
        }

        try {
            // Populate all text/number fields
            this.getFormFields().forEach(fieldId => {
                if (data.hasOwnProperty(fieldId)) {
                    const element = document.getElementById(fieldId);
                    if (element) {
                        element.value = data[fieldId];
                    }
                }
            });

            // Set deduction type radio buttons
            if (data.use_standard_deduction) {
                this.setDeductionType(data.use_standard_deduction);
            }

            console.log('Form populated successfully');
            return true;
        } catch (e) {
            console.error('Error populating form:', e);
            return false;
        }
    },

    /**
     * Clear saved data from localStorage
     */
    clearData: function() {
        if (!this.isLocalStorageAvailable()) {
            return false;
        }

        try {
            localStorage.removeItem(this.STORAGE_KEY);
            console.log('Data cleared successfully');
            return true;
        } catch (e) {
            console.error('Error clearing data:', e);
            return false;
        }
    },

    /**
     * Get timestamp of last save
     */
    getLastSaveTimestamp: function() {
        const data = this.loadData();
        return data ? data.timestamp : null;
    },

    /**
     * Format timestamp for display
     */
    formatTimestamp: function(isoString) {
        if (!isoString) {
            return 'Never';
        }

        try {
            const date = new Date(isoString);
            const now = new Date();
            const diffMs = now - date;
            const diffMins = Math.floor(diffMs / 60000);
            const diffHours = Math.floor(diffMs / 3600000);
            const diffDays = Math.floor(diffMs / 86400000);

            if (diffMins < 1) {
                return 'Just now';
            } else if (diffMins < 60) {
                return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
            } else if (diffHours < 24) {
                return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
            } else if (diffDays < 30) {
                return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
            } else {
                return date.toLocaleDateString();
            }
        } catch (e) {
            return 'Unknown';
        }
    },

    /**
     * Check if localStorage is available
     */
    isLocalStorageAvailable: function() {
        try {
            const test = '__storage_test__';
            localStorage.setItem(test, test);
            localStorage.removeItem(test);
            return true;
        } catch (e) {
            return false;
        }
    },

    /**
     * Update the "last saved" timestamp display
     */
    updateTimestampDisplay: function() {
        const timestamp = this.getLastSaveTimestamp();
        const element = document.getElementById('last-saved-timestamp');
        const infoBox = document.getElementById('saved-data-info');

        if (element && timestamp) {
            const formatted = this.formatTimestamp(timestamp);
            element.textContent = formatted;
            if (infoBox) {
                infoBox.style.display = 'flex';
            }
        }
    },

    /**
     * Initialize persistence on page load
     */
    init: function() {
        console.log('Initializing MAGI Persistence...');

        // Load and populate saved data
        const data = this.loadData();
        if (data) {
            this.populateForm(data);
            this.updateTimestampDisplay();
        }

        // Setup form submission to auto-save
        const form = document.querySelector('.magi-form');
        if (form) {
            form.addEventListener('submit', () => {
                this.saveData();
            });
        }

        // Setup clear data button
        const clearButton = document.getElementById('clear-saved-data');
        if (clearButton) {
            clearButton.addEventListener('click', (e) => {
                e.preventDefault();
                if (confirm('Are you sure you want to clear all saved data?')) {
                    this.clearData();
                    location.reload();
                }
            });
        }

        console.log('MAGI Persistence initialized');
    }
};

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => MAGIPersistence.init());
} else {
    MAGIPersistence.init();
}
