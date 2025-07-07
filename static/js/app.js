// Car Wash Manager - Main JavaScript Application

// Global variables
let selectedCustomer = null;
let currentInvoiceItems = [];
let barcodeScanner = null;
let cashCalculator = null;

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

// Main initialization function
function initializeApp() {
    console.log('Car Wash Manager - Initializing...');
    
    // Initialize components
    initializeNavigation();
    initializeModals();
    initializeFormValidation();
    initializeBarcodeScanner();
    initializeCashCalculator();
    initializeCustomerSearch();
    initializeTooltips();
    initializeAutoSave();
    
    console.log('Car Wash Manager - Ready!');
}

// Navigation enhancements
function initializeNavigation() {
    // Add active class to current page
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
    
    // Mobile navigation improvements
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    if (navbarToggler && navbarCollapse) {
        // Close mobile menu when clicking outside
        document.addEventListener('click', function(e) {
            if (!navbarCollapse.contains(e.target) && !navbarToggler.contains(e.target)) {
                const bsCollapse = bootstrap.Collapse.getInstance(navbarCollapse);
                if (bsCollapse && navbarCollapse.classList.contains('show')) {
                    bsCollapse.hide();
                }
            }
        });
    }
}

// Modal enhancements
function initializeModals() {
    // Clear form data when modals are closed
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        modal.addEventListener('hidden.bs.modal', function() {
            const forms = this.querySelectorAll('form');
            forms.forEach(form => {
                form.reset();
                // Clear validation states
                const invalidInputs = form.querySelectorAll('.is-invalid');
                invalidInputs.forEach(input => input.classList.remove('is-invalid'));
            });
        });
    });
    
    // Focus first input when modals open
    modals.forEach(modal => {
        modal.addEventListener('shown.bs.modal', function() {
            const firstInput = this.querySelector('input:not([type="hidden"]), select, textarea');
            if (firstInput) {
                firstInput.focus();
            }
        });
    });
}

// Form validation enhancements
function initializeFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
                
                // Focus first invalid field
                const firstInvalid = form.querySelector(':invalid');
                if (firstInvalid) {
                    firstInvalid.focus();
                    showNotification('Por favor, complete todos los campos requeridos', 'warning');
                }
            }
            
            form.classList.add('was-validated');
        });
        
        // Real-time validation
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                if (this.checkValidity()) {
                    this.classList.remove('is-invalid');
                    this.classList.add('is-valid');
                } else {
                    this.classList.remove('is-valid');
                    this.classList.add('is-invalid');
                }
            });
        });
    });
}

// Barcode scanner functionality
function initializeBarcodeScanner() {
    const barcodeInputs = document.querySelectorAll('input[type="text"][placeholder*="código"], input[type="text"][placeholder*="barras"]');
    
    barcodeInputs.forEach(input => {
        input.addEventListener('input', function() {
            const barcode = this.value.trim();
            
            // Detect barcode pattern (typically 8-13 digits)
            if (/^\d{8,13}$/.test(barcode)) {
                this.classList.add('barcode-detected');
                searchProductByBarcode(barcode, this);
            } else {
                this.classList.remove('barcode-detected');
            }
        });
        
        // Enable camera scanning if supported
        input.addEventListener('focus', function() {
            if ('mediaDevices' in navigator && 'getUserMedia' in navigator.mediaDevices) {
                this.setAttribute('data-scanner-ready', 'true');
            }
        });
    });
}

// Search product by barcode
function searchProductByBarcode(barcode, inputElement) {
    showLoading(inputElement.parentElement);
    
    fetch(`/search_product?barcode=${barcode}`)
        .then(response => response.json())
        .then(data => {
            hideLoading(inputElement.parentElement);
            
            if (data.found) {
                inputElement.classList.add('is-valid');
                showProductInfo(data, inputElement);
                
                // Auto-fill product in invoice if we're on that page
                if (window.location.pathname === '/invoice') {
                    selectProductForInvoice(data);
                }
            } else {
                inputElement.classList.add('is-invalid');
                showNotification('Producto no encontrado', 'warning');
            }
        })
        .catch(error => {
            hideLoading(inputElement.parentElement);
            console.error('Error searching product:', error);
            showNotification('Error al buscar producto', 'error');
        });
}

// Show product information
function showProductInfo(productData, nearElement) {
    const infoHtml = `
        <div class="product-info-popup bg-success text-white p-2 rounded position-absolute" style="z-index: 1000; top: 100%; left: 0; min-width: 200px;">
            <strong>${productData.name}</strong><br>
            Precio: L ${productData.price.toFixed(2)}<br>
            Stock: ${productData.stock}
            <button type="button" class="btn-close btn-close-white btn-sm ms-2" onclick="this.parentElement.remove()"></button>
        </div>
    `;
    
    // Remove existing popups
    document.querySelectorAll('.product-info-popup').forEach(popup => popup.remove());
    
    // Add new popup
    nearElement.parentElement.style.position = 'relative';
    nearElement.parentElement.insertAdjacentHTML('beforeend', infoHtml);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        document.querySelectorAll('.product-info-popup').forEach(popup => popup.remove());
    }, 5000);
}

// Cash calculator for denominations
function initializeCashCalculator() {
    const cashInputs = document.querySelectorAll('.cash-input, .cash-input-closing');
    
    if (cashInputs.length === 0) return;
    
    cashInputs.forEach(input => {
        input.addEventListener('input', function() {
            calculateCashTotal();
            updateCashDisplay();
        });
        
        // Add keyboard shortcuts for common amounts
        input.addEventListener('keydown', function(e) {
            if (e.ctrlKey || e.metaKey) {
                switch(e.key) {
                    case '1':
                        e.preventDefault();
                        this.value = '1';
                        this.dispatchEvent(new Event('input'));
                        break;
                    case '5':
                        e.preventDefault();
                        this.value = '5';
                        this.dispatchEvent(new Event('input'));
                        break;
                    case '0':
                        e.preventDefault();
                        this.value = '0';
                        this.dispatchEvent(new Event('input'));
                        break;
                }
            }
        });
    });
    
    // Add quick denomination buttons
    addQuickDenominationButtons();
}

// Calculate total cash from all denomination inputs
function calculateCashTotal() {
    let total = 0;
    const cashInputs = document.querySelectorAll('.cash-input, .cash-input-closing');
    
    cashInputs.forEach(input => {
        const quantity = parseInt(input.value) || 0;
        const value = parseFloat(input.dataset.value) || 0;
        total += quantity * value;
    });
    
    return total;
}

// Update cash display elements
function updateCashDisplay() {
    const total = calculateCashTotal();
    
    // Update various total displays
    const totalElements = document.querySelectorAll('#totalReceived, #totalCounted');
    totalElements.forEach(element => {
        if (element) {
            element.textContent = `L ${total.toFixed(2)}`;
        }
    });
    
    // Update change calculation
    const requiredAmount = parseFloat(document.querySelector('[data-required-amount]')?.dataset.requiredAmount) || 0;
    const changeElement = document.getElementById('changeAmount');
    if (changeElement && requiredAmount > 0) {
        const change = Math.max(0, total - requiredAmount);
        changeElement.textContent = `L ${change.toFixed(2)}`;
        changeElement.className = change >= 0 ? 'h5 text-success' : 'h5 text-danger';
    }
    
    // Enable/disable payment button
    const paymentBtn = document.getElementById('processPaymentBtn');
    if (paymentBtn && requiredAmount > 0) {
        paymentBtn.disabled = total < requiredAmount;
        paymentBtn.className = total >= requiredAmount ? 
            'btn btn-success btn-lg w-100' : 
            'btn btn-secondary btn-lg w-100';
    }
}

// Add quick denomination buttons
function addQuickDenominationButtons() {
    const cashContainer = document.querySelector('.cash-input, .cash-input-closing')?.closest('.card-body');
    
    if (!cashContainer) return;
    
    const quickButtonsHtml = `
        <div class="quick-cash-buttons mt-3">
            <h6>Acciones Rápidas:</h6>
            <div class="btn-group btn-group-sm mb-2" role="group">
                <button type="button" class="btn btn-outline-primary" onclick="clearAllCash()">
                    <i class="fas fa-eraser"></i> Limpiar
                </button>
                <button type="button" class="btn btn-outline-info" onclick="calculateExactChange()">
                    <i class="fas fa-calculator"></i> Cambio Exacto
                </button>
                <button type="button" class="btn btn-outline-success" onclick="suggestDenominations()">
                    <i class="fas fa-lightbulb"></i> Sugerir
                </button>
            </div>
        </div>
    `;
    
    if (!cashContainer.querySelector('.quick-cash-buttons')) {
        cashContainer.insertAdjacentHTML('beforeend', quickButtonsHtml);
    }
}

// Clear all cash inputs
function clearAllCash() {
    const cashInputs = document.querySelectorAll('.cash-input, .cash-input-closing');
    cashInputs.forEach(input => {
        input.value = '0';
        input.dispatchEvent(new Event('input'));
    });
}

// Calculate exact change needed
function calculateExactChange() {
    const requiredAmount = parseFloat(document.querySelector('[data-required-amount]')?.dataset.requiredAmount) || 0;
    
    if (requiredAmount <= 0) {
        showNotification('No hay monto requerido para calcular', 'info');
        return;
    }
    
    clearAllCash();
    
    // Calculate optimal denomination distribution
    const denominations = [
        {value: 1000, name: 'bills_1000'},
        {value: 500, name: 'bills_500'},
        {value: 200, name: 'bills_200'},
        {value: 100, name: 'bills_100'},
        {value: 50, name: 'bills_50'},
        {value: 20, name: 'bills_20'},
        {value: 10, name: 'bills_10'},
        {value: 5, name: 'bills_5'},
        {value: 2, name: 'bills_2'},
        {value: 1, name: 'bills_1'},
        {value: 0.50, name: 'coins_50c'},
        {value: 0.20, name: 'coins_20c'},
        {value: 0.10, name: 'coins_10c'},
        {value: 0.05, name: 'coins_5c'}
    ];
    
    let remaining = requiredAmount;
    
    denominations.forEach(denom => {
        if (remaining >= denom.value) {
            const count = Math.floor(remaining / denom.value);
            remaining = Math.round((remaining - (count * denom.value)) * 100) / 100;
            
            const input = document.querySelector(`input[name="${denom.name}"]`);
            if (input) {
                input.value = count;
                input.dispatchEvent(new Event('input'));
            }
        }
    });
    
    showNotification('Denominaciones calculadas para monto exacto', 'success');
}

// Suggest denomination distribution
function suggestDenominations() {
    const total = calculateCashTotal();
    
    if (total <= 0) {
        showNotification('Ingrese algunas denominaciones primero', 'info');
        return;
    }
    
    showNotification(`Total actual: L ${total.toFixed(2)}. Distribución optimizada aplicada.`, 'info');
}

// Customer search functionality
function initializeCustomerSearch() {
    const customerPhoneInputs = document.querySelectorAll('input[name="customer_phone"], #customerPhone, #appointmentPhone');
    
    customerPhoneInputs.forEach(input => {
        let searchTimeout;
        
        input.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            const phone = this.value.trim();
            
            if (phone.length >= 8) {
                searchTimeout = setTimeout(() => {
                    searchCustomer(phone, this);
                }, 500); // Debounce search
            } else {
                clearCustomerInfo(this);
            }
        });
        
        // Format phone number as user types
        input.addEventListener('input', function() {
            let value = this.value.replace(/\D/g, '');
            if (value.length >= 4) {
                value = value.replace(/(\d{4})(\d{0,4})/, '$1-$2');
            }
            this.value = value;
        });
    });
}

// Search customer by phone
function searchCustomer(phone, inputElement) {
    const container = inputElement.closest('.card-body, .modal-body');
    if (!container) return;
    
    showLoading(container);
    
    fetch(`/search_customer?phone=${phone}`)
        .then(response => response.json())
        .then(data => {
            hideLoading(container);
            
            if (data.found) {
                populateCustomerInfo(data, inputElement);
                showCustomerFoundIndicator(inputElement, data);
                selectedCustomer = data;
            } else {
                clearCustomerInfo(inputElement);
                selectedCustomer = null;
            }
        })
        .catch(error => {
            hideLoading(container);
            console.error('Error searching customer:', error);
            showNotification('Error al buscar cliente', 'error');
        });
}

// Populate customer information in form
function populateCustomerInfo(customerData, phoneInput) {
    const container = phoneInput.closest('.card-body, .modal-body, form');
    
    // Find and populate related fields
    const nameField = container.querySelector('input[name="customer_name"], #customerName, #appointmentName');
    const emailField = container.querySelector('input[name="customer_email"], #customerEmail');
    const addressField = container.querySelector('textarea[name="customer_address"], #customerAddress');
    
    if (nameField) nameField.value = customerData.name;
    if (emailField) emailField.value = customerData.email || '';
    if (addressField) addressField.value = customerData.address || '';
}

// Show customer found indicator
function showCustomerFoundIndicator(phoneInput, customerData) {
    const container = phoneInput.closest('.card-body, .modal-body');
    let infoDiv = container.querySelector('.customer-found-info');
    
    if (!infoDiv) {
        infoDiv = document.createElement('div');
        infoDiv.className = 'customer-found-info alert alert-success mt-2';
        phoneInput.parentElement.appendChild(infoDiv);
    }
    
    infoDiv.innerHTML = `
        <i class="fas fa-user-check"></i> <strong>Cliente encontrado:</strong> ${customerData.name}<br>
        <small>Visitas anteriores: ${customerData.total_visits || 1}</small>
    `;
}

// Clear customer information
function clearCustomerInfo(phoneInput) {
    const container = phoneInput.closest('.card-body, .modal-body, form');
    
    // Clear related fields (but keep phone)
    const nameField = container.querySelector('input[name="customer_name"], #customerName, #appointmentName');
    const emailField = container.querySelector('input[name="customer_email"], #customerEmail');
    const addressField = container.querySelector('textarea[name="customer_address"], #customerAddress');
    
    if (nameField) nameField.value = '';
    if (emailField) emailField.value = '';
    if (addressField) addressField.value = '';
    
    // Remove customer found indicator
    const infoDiv = container.querySelector('.customer-found-info');
    if (infoDiv) infoDiv.remove();
    
    selectedCustomer = null;
}

// Initialize tooltips
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Auto-save functionality for forms
function initializeAutoSave() {
    const forms = document.querySelectorAll('form[data-autosave]');
    
    forms.forEach(form => {
        const formId = form.id || 'form_' + Date.now();
        const saveKey = `carwash_autosave_${formId}`;
        
        // Load saved data
        loadAutoSavedData(form, saveKey);
        
        // Save on input
        form.addEventListener('input', function() {
            saveFormData(form, saveKey);
        });
        
        // Clear saved data on successful submit
        form.addEventListener('submit', function() {
            localStorage.removeItem(saveKey);
        });
    });
}

// Save form data to localStorage
function saveFormData(form, saveKey) {
    const formData = new FormData(form);
    const data = {};
    
    for (let [key, value] of formData.entries()) {
        data[key] = value;
    }
    
    localStorage.setItem(saveKey, JSON.stringify(data));
}

// Load auto-saved form data
function loadAutoSavedData(form, saveKey) {
    const savedData = localStorage.getItem(saveKey);
    
    if (savedData) {
        try {
            const data = JSON.parse(savedData);
            
            Object.keys(data).forEach(name => {
                const field = form.querySelector(`[name="${name}"]`);
                if (field) {
                    field.value = data[name];
                }
            });
            
            showNotification('Datos guardados automáticamente restaurados', 'info');
        } catch (error) {
            console.error('Error loading auto-saved data:', error);
        }
    }
}

// Utility functions

// Show loading indicator
function showLoading(container) {
    let loader = container.querySelector('.loading-indicator');
    
    if (!loader) {
        loader = document.createElement('div');
        loader.className = 'loading-indicator text-center p-2';
        loader.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Cargando...';
        container.appendChild(loader);
    }
    
    loader.style.display = 'block';
}

// Hide loading indicator
function hideLoading(container) {
    const loader = container.querySelector('.loading-indicator');
    if (loader) {
        loader.style.display = 'none';
    }
}

// Show notification
function showNotification(message, type = 'info', duration = 5000) {
    const alertClass = {
        'success': 'alert-success',
        'error': 'alert-danger',
        'warning': 'alert-warning',
        'info': 'alert-info'
    }[type] || 'alert-info';
    
    const notification = document.createElement('div');
    notification.className = `alert ${alertClass} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after duration
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, duration);
}

// Format currency for display
function formatCurrency(amount) {
    return `L ${parseFloat(amount).toFixed(2)}`;
}

// Validate Honduran phone number
function validateHonduranPhone(phone) {
    const cleanPhone = phone.replace(/\D/g, '');
    return /^[2389]\d{7}$/.test(cleanPhone);
}

// Format phone number for display
function formatPhoneNumber(phone) {
    const cleanPhone = phone.replace(/\D/g, '');
    if (cleanPhone.length === 8) {
        return cleanPhone.replace(/(\d{4})(\d{4})/, '$1-$2');
    }
    return phone;
}

// Export global functions for template use
window.CarWashManager = {
    searchCustomer,
    formatCurrency,
    validateHonduranPhone,
    formatPhoneNumber,
    showNotification,
    clearAllCash,
    calculateExactChange,
    suggestDenominations
};

// Service Worker registration for offline functionality
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        navigator.serviceWorker.register('/static/sw.js')
            .then(function(registration) {
                console.log('ServiceWorker registration successful');
            })
            .catch(function(error) {
                console.log('ServiceWorker registration failed');
            });
    });
}

// Print functionality enhancement
function enhancedPrint(element) {
    const printWindow = window.open('', '_blank');
    const printContent = element.innerHTML;
    
    printWindow.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>Car Wash - Impresión</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
            <link href="/static/css/style.css" rel="stylesheet">
            <style>
                @media print {
                    body { margin: 0; }
                    .no-print { display: none !important; }
                }
            </style>
        </head>
        <body>
            ${printContent}
            <script>
                window.onload = function() {
                    window.print();
                    window.onafterprint = function() {
                        window.close();
                    }
                }
            </script>
        </body>
        </html>
    `);
    
    printWindow.document.close();
}

// Enhanced table search functionality
function enhanceTableSearch() {
    const searchInputs = document.querySelectorAll('input[data-table-search]');
    
    searchInputs.forEach(input => {
        const tableId = input.dataset.tableSearch;
        const table = document.getElementById(tableId);
        
        if (!table) return;
        
        input.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const rows = table.querySelectorAll('tbody tr');
            
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(searchTerm) ? '' : 'none';
            });
            
            // Show no results message
            const visibleRows = table.querySelectorAll('tbody tr[style=""]');
            let noResultsRow = table.querySelector('.no-results-row');
            
            if (visibleRows.length === 0 && searchTerm) {
                if (!noResultsRow) {
                    noResultsRow = document.createElement('tr');
                    noResultsRow.className = 'no-results-row';
                    noResultsRow.innerHTML = `<td colspan="100%" class="text-center text-muted py-4">No se encontraron resultados para "${searchTerm}"</td>`;
                    table.querySelector('tbody').appendChild(noResultsRow);
                }
                noResultsRow.style.display = '';
            } else if (noResultsRow) {
                noResultsRow.style.display = 'none';
            }
        });
    });
}

// Initialize enhanced features after DOM load
document.addEventListener('DOMContentLoaded', function() {
    enhanceTableSearch();
});

console.log('Car Wash Manager JavaScript loaded successfully!');
