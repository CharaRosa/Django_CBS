/**
 * Forms JavaScript - Materially Inspired
 * Enhanced form interactions and validation
 */

(function() {
    'use strict';

    // ============================================
    // FORM VALIDATION ENHANCEMENT
    // ============================================
    
    /**
     * Add real-time validation feedback
     */
    function enhanceFormValidation() {
        const forms = document.querySelectorAll('form');
        
        forms.forEach(form => {
            const inputs = form.querySelectorAll('input, select, textarea');
            
            inputs.forEach(input => {
                // Add focus/blur effects
                input.addEventListener('focus', function() {
                    this.closest('.form-group')?.classList.add('focused');
                });
                
                input.addEventListener('blur', function() {
                    this.closest('.form-group')?.classList.remove('focused');
                    validateField(this);
                });
                
                // Real-time validation on input
                input.addEventListener('input', function() {
                    if (this.classList.contains('is-invalid')) {
                        validateField(this);
                    }
                });
            });
        });
    }
    
    /**
     * Validate individual field
     */
    function validateField(field) {
        const value = field.value.trim();
        const required = field.hasAttribute('required');
        const type = field.type;
        
        // Remove previous validation classes
        field.classList.remove('is-valid', 'is-invalid');
        
        // Check if required field is empty
        if (required && !value) {
            field.classList.add('is-invalid');
            showFieldError(field, 'Ce champ est requis');
            return false;
        }
        
        // Email validation
        if (type === 'email' && value) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(value)) {
                field.classList.add('is-invalid');
                showFieldError(field, 'Adresse email invalide');
                return false;
            }
        }
        
        // Number validation
        if (type === 'number' && value) {
            const min = field.getAttribute('min');
            const max = field.getAttribute('max');
            const numValue = parseFloat(value);
            
            if (min && numValue < parseFloat(min)) {
                field.classList.add('is-invalid');
                showFieldError(field, `La valeur doit être au moins ${min}`);
                return false;
            }
            
            if (max && numValue > parseFloat(max)) {
                field.classList.add('is-invalid');
                showFieldError(field, `La valeur ne peut pas dépasser ${max}`);
                return false;
            }
        }
        
        // If all checks pass
        if (value) {
            field.classList.add('is-valid');
            hideFieldError(field);
        }
        
        return true;
    }
    
    /**
     * Show field error message
     */
    function showFieldError(field, message) {
        let errorElement = field.parentElement.querySelector('.invalid-feedback');
        
        if (!errorElement) {
            errorElement = document.createElement('div');
            errorElement.className = 'invalid-feedback';
            field.parentElement.appendChild(errorElement);
        }
        
        errorElement.textContent = message;
        errorElement.style.display = 'block';
    }
    
    /**
     * Hide field error message
     */
    function hideFieldError(field) {
        const errorElement = field.parentElement.querySelector('.invalid-feedback');
        if (errorElement) {
            errorElement.style.display = 'none';
        }
    }
    
    // ============================================
    // FORM SUBMISSION HANDLING
    // ============================================
    
    /**
     * Handle form submission with loading state
     */
    function handleFormSubmission() {
        const forms = document.querySelectorAll('form');
        
        forms.forEach(form => {
            form.addEventListener('submit', function(e) {
                // Validate all fields before submission
                const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
                let isValid = true;
                
                inputs.forEach(input => {
                    if (!validateField(input)) {
                        isValid = false;
                    }
                });
                
                if (!isValid) {
                    e.preventDefault();
                    showAlert('Veuillez corriger les erreurs dans le formulaire', 'danger');
                    return;
                }
                
                // Add loading state to submit button
                const submitBtn = form.querySelector('button[type="submit"]');
                if (submitBtn) {
                    submitBtn.disabled = true;
                    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>En cours...';
                }
            });
        });
    }
    
    // ============================================
    // AUTO-SAVE FUNCTIONALITY (Optional)
    // ============================================
    
    /**
     * Auto-save form data to localStorage
     */
    function enableAutoSave() {
        const forms = document.querySelectorAll('form[data-autosave]');
        
        forms.forEach(form => {
            const formId = form.getAttribute('id') || 'form_' + Date.now();
            const storageKey = 'autosave_' + formId;
            
            // Load saved data
            loadFormData(form, storageKey);
            
            // Save on input change
            form.addEventListener('input', debounce(function() {
                saveFormData(form, storageKey);
            }, 500));
            
            // Clear on successful submit
            form.addEventListener('submit', function() {
                localStorage.removeItem(storageKey);
            });
        });
    }
    
    /**
     * Save form data to localStorage
     */
    function saveFormData(form, storageKey) {
        const formData = {};
        const inputs = form.querySelectorAll('input, select, textarea');
        
        inputs.forEach(input => {
            if (input.name && input.type !== 'password') {
                formData[input.name] = input.value;
            }
        });
        
        localStorage.setItem(storageKey, JSON.stringify(formData));
        showAutoSaveIndicator();
    }
    
    /**
     * Load form data from localStorage
     */
    function loadFormData(form, storageKey) {
        const savedData = localStorage.getItem(storageKey);
        
        if (savedData) {
            try {
                const formData = JSON.parse(savedData);
                
                Object.keys(formData).forEach(name => {
                    const input = form.querySelector(`[name="${name}"]`);
                    if (input && input.type !== 'password') {
                        input.value = formData[name];
                    }
                });
                
                showAlert('Données de formulaire restaurées', 'info');
            } catch (e) {
                console.error('Error loading form data:', e);
            }
        }
    }
    
    /**
     * Show auto-save indicator
     */
    function showAutoSaveIndicator() {
        let indicator = document.querySelector('.autosave-indicator');
        
        if (!indicator) {
            indicator = document.createElement('div');
            indicator.className = 'autosave-indicator';
            indicator.innerHTML = '<i class="fas fa-check-circle me-1"></i>Sauvegardé';
            document.body.appendChild(indicator);
        }
        
        indicator.classList.add('show');
        
        setTimeout(() => {
            indicator.classList.remove('show');
        }, 2000);
    }
    
    // ============================================
    // CHARACTER COUNTER
    // ============================================
    
    /**
     * Add character counter to textareas
     */
    function addCharacterCounters() {
        const textareas = document.querySelectorAll('textarea[maxlength]');
        
        textareas.forEach(textarea => {
            const maxLength = textarea.getAttribute('maxlength');
            const counter = document.createElement('div');
            counter.className = 'character-counter';
            counter.style.cssText = 'text-align: right; font-size: 0.8125rem; color: #6B7280; margin-top: 0.25rem;';
            
            textarea.parentElement.appendChild(counter);
            
            function updateCounter() {
                const remaining = maxLength - textarea.value.length;
                counter.textContent = `${remaining} caractères restants`;
                
                if (remaining < 50) {
                    counter.style.color = '#EF4444';
                } else {
                    counter.style.color = '#6B7280';
                }
            }
            
            textarea.addEventListener('input', updateCounter);
            updateCounter();
        });
    }
    
    // ============================================
    // CONFIRMATION DIALOGS
    // ============================================
    
    /**
     * Add confirmation to dangerous actions
     */
    function addConfirmationDialogs() {
        const dangerousButtons = document.querySelectorAll('[data-confirm]');
        
        dangerousButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                const message = this.getAttribute('data-confirm');
                if (!confirm(message)) {
                    e.preventDefault();
                }
            });
        });
    }
    
    // ============================================
    // UTILITY FUNCTIONS
    // ============================================
    
    /**
     * Debounce function
     */
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
    
    /**
     * Show alert message
     */
    function showAlert(message, type = 'info') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type}`;
        alertDiv.innerHTML = `
            <i class="fas fa-${getAlertIcon(type)} alert-icon"></i>
            <span>${message}</span>
        `;
        
        const container = document.querySelector('.app-main') || document.body;
        container.insertBefore(alertDiv, container.firstChild);
        
        setTimeout(() => {
            alertDiv.style.animation = 'fadeOut 0.3s ease-out';
            setTimeout(() => alertDiv.remove(), 300);
        }, 5000);
    }
    
    /**
     * Get icon for alert type
     */
    function getAlertIcon(type) {
        const icons = {
            success: 'check-circle',
            danger: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    }
    
    // ============================================
    // INITIALIZE
    // ============================================
    
    document.addEventListener('DOMContentLoaded', function() {
        enhanceFormValidation();
        handleFormSubmission();
        enableAutoSave();
        addCharacterCounters();
        addConfirmationDialogs();
    });
    
})();

// ============================================
// AUTOSAVE INDICATOR STYLES (injected)
// ============================================
const autoSaveStyles = `
.autosave-indicator {
    position: fixed;
    bottom: 2rem;
    right: 2rem;
    background: #10B981;
    color: white;
    padding: 0.75rem 1.5rem;
    border-radius: 10px;
    box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
    font-size: 0.875rem;
    font-weight: 600;
    opacity: 0;
    transform: translateY(20px);
    transition: all 0.3s ease;
    z-index: 9999;
}

.autosave-indicator.show {
    opacity: 1;
    transform: translateY(0);
}
`;

const styleSheet = document.createElement('style');
styleSheet.textContent = autoSaveStyles;
document.head.appendChild(styleSheet);
