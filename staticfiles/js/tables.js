/**
 * Tables & Lists JavaScript - Materially Inspired
 * Enhanced table interactions and filtering
 */

(function() {
    'use strict';

    // ============================================
    // TABLE ROW ACTIONS
    // ============================================
    
    /**
     * Add hover effects and click handlers to table rows
     */
    function enhanceTableRows() {
        const tables = document.querySelectorAll('.data-table');
        
        tables.forEach(table => {
            const rows = table.querySelectorAll('tbody tr');
            
            rows.forEach(row => {
                // Add click to select (optional)
                row.addEventListener('click', function(e) {
                    // Don't select if clicking on action buttons
                    if (e.target.closest('.action-btn')) {
                        return;
                    }
                    
                    // Toggle selection
                    this.classList.toggle('selected');
                });
            });
        });
    }
    
    // ============================================
    // FILTER FORM ENHANCEMENTS
    // ============================================
    
    /**
     * Auto-submit filter form on change
     */
    function enhanceFilters() {
        const filterForms = document.querySelectorAll('.filter-form');
        
        filterForms.forEach(form => {
            const autoSubmit = form.hasAttribute('data-auto-submit');
            
            if (autoSubmit) {
                const inputs = form.querySelectorAll('input, select');
                
                inputs.forEach(input => {
                    input.addEventListener('change', debounce(function() {
                        form.submit();
                    }, 300));
                });
            }
            
            // Reset button functionality
            const resetBtn = form.querySelector('[data-reset]');
            if (resetBtn) {
                resetBtn.addEventListener('click', function(e) {
                    e.preventDefault();
                    form.reset();
                    
                    // Clear URL parameters
                    const url = new URL(window.location);
                    url.search = '';
                    window.location.href = url.toString();
                });
            }
        });
    }
    
    // ============================================
    // SORTING FUNCTIONALITY
    // ============================================
    
    /**
     * Add client-side table sorting
     */
    function enableTableSorting() {
        const tables = document.querySelectorAll('.data-table[data-sortable]');
        
        tables.forEach(table => {
            const headers = table.querySelectorAll('thead th[data-sortable]');
            
            headers.forEach((header, index) => {
                header.style.cursor = 'pointer';
                header.innerHTML += ' <i class="fas fa-sort text-muted"></i>';
                
                header.addEventListener('click', function() {
                    sortTable(table, index, this);
                });
            });
        });
    }
    
    /**
     * Sort table by column
     */
    function sortTable(table, columnIndex, header) {
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));
        const isAscending = header.classList.contains('sort-asc');
        
        // Remove sorting classes from all headers
        table.querySelectorAll('thead th').forEach(th => {
            th.classList.remove('sort-asc', 'sort-desc');
            const icon = th.querySelector('i');
            if (icon) {
                icon.className = 'fas fa-sort text-muted';
            }
        });
        
        // Sort rows
        rows.sort((a, b) => {
            const aValue = a.cells[columnIndex].textContent.trim();
            const bValue = b.cells[columnIndex].textContent.trim();
            
            // Try numeric comparison first
            const aNum = parseFloat(aValue.replace(/[^\d.-]/g, ''));
            const bNum = parseFloat(bValue.replace(/[^\d.-]/g, ''));
            
            if (!isNaN(aNum) && !isNaN(bNum)) {
                return isAscending ? bNum - aNum : aNum - bNum;
            }
            
            // Fallback to string comparison
            return isAscending 
                ? bValue.localeCompare(aValue)
                : aValue.localeCompare(bValue);
        });
        
        // Update header classes and icon
        if (isAscending) {
            header.classList.add('sort-desc');
            header.querySelector('i').className = 'fas fa-sort-down text-primary';
        } else {
            header.classList.add('sort-asc');
            header.querySelector('i').className = 'fas fa-sort-up text-primary';
        }
        
        // Reappend rows
        rows.forEach(row => tbody.appendChild(row));
    }
    
    // ============================================
    // SEARCH FUNCTIONALITY
    // ============================================
    
    /**
     * Add live search to tables
     */
    function enableTableSearch() {
        const searchInputs = document.querySelectorAll('[data-table-search]');
        
        searchInputs.forEach(input => {
            const tableId = input.getAttribute('data-table-search');
            const table = document.querySelector(tableId);
            
            if (!table) return;
            
            input.addEventListener('input', debounce(function() {
                const searchTerm = this.value.toLowerCase();
                const rows = table.querySelectorAll('tbody tr');
                
                rows.forEach(row => {
                    const text = row.textContent.toLowerCase();
                    row.style.display = text.includes(searchTerm) ? '' : 'none';
                });
                
                updateEmptyState(table, searchTerm);
            }, 300));
        });
    }
    
    /**
     * Update empty state message
     */
    function updateEmptyState(table, searchTerm) {
        const visibleRows = table.querySelectorAll('tbody tr:not([style*="display: none"])');
        let emptyState = table.querySelector('.search-empty-state');
        
        if (visibleRows.length === 0 && searchTerm) {
            if (!emptyState) {
                emptyState = document.createElement('tr');
                emptyState.className = 'search-empty-state';
                emptyState.innerHTML = `
                    <td colspan="100%" class="text-center py-4">
                        <i class="fas fa-search fa-2x text-muted mb-2"></i>
                        <p class="text-muted">Aucun résultat trouvé pour "${searchTerm}"</p>
                    </td>
                `;
                table.querySelector('tbody').appendChild(emptyState);
            }
        } else if (emptyState) {
            emptyState.remove();
        }
    }
    
    // ============================================
    // BULK ACTIONS
    // ============================================
    
    /**
     * Enable bulk selection and actions
     */
    function enableBulkActions() {
        const bulkTables = document.querySelectorAll('[data-bulk-actions]');
        
        bulkTables.forEach(table => {
            // Add checkboxes to rows
            addBulkCheckboxes(table);
            
            // Add select all functionality
            const selectAll = table.querySelector('.select-all');
            if (selectAll) {
                selectAll.addEventListener('change', function() {
                    const checkboxes = table.querySelectorAll('.row-checkbox');
                    checkboxes.forEach(cb => cb.checked = this.checked);
                    updateBulkActionsBar();
                });
            }
            
            // Monitor row selections
            table.addEventListener('change', function(e) {
                if (e.target.classList.contains('row-checkbox')) {
                    updateBulkActionsBar();
                }
            });
        });
    }
    
    /**
     * Add checkboxes to table rows
     */
    function addBulkCheckboxes(table) {
        // Add header checkbox
        const headerRow = table.querySelector('thead tr');
        const checkboxTh = document.createElement('th');
        checkboxTh.innerHTML = '<input type="checkbox" class="select-all">';
        headerRow.insertBefore(checkboxTh, headerRow.firstChild);
        
        // Add row checkboxes
        const rows = table.querySelectorAll('tbody tr');
        rows.forEach(row => {
            const checkboxTd = document.createElement('td');
            checkboxTd.innerHTML = '<input type="checkbox" class="row-checkbox">';
            row.insertBefore(checkboxTd, row.firstChild);
        });
    }
    
    /**
     * Update bulk actions bar
     */
    function updateBulkActionsBar() {
        const selectedCount = document.querySelectorAll('.row-checkbox:checked').length;
        let bulkBar = document.querySelector('.bulk-actions-bar');
        
        if (selectedCount > 0) {
            if (!bulkBar) {
                bulkBar = createBulkActionsBar();
                document.querySelector('.app-main').prepend(bulkBar);
            }
            
            bulkBar.querySelector('.selected-count').textContent = `${selectedCount} élément(s) sélectionné(s)`;
            bulkBar.style.display = 'flex';
        } else if (bulkBar) {
            bulkBar.style.display = 'none';
        }
    }
    
    /**
     * Create bulk actions bar
     */
    function createBulkActionsBar() {
        const bar = document.createElement('div');
        bar.className = 'bulk-actions-bar';
        bar.innerHTML = `
            <div class="selected-count"></div>
            <div class="bulk-actions">
                <button class="btn btn-secondary btn-sm" data-action="export">
                    <i class="fas fa-download me-1"></i>Exporter
                </button>
                <button class="btn btn-danger btn-sm" data-action="delete">
                    <i class="fas fa-trash me-1"></i>Supprimer
                </button>
            </div>
        `;
        return bar;
    }
    
    // ============================================
    // EXPORT FUNCTIONALITY
    // ============================================
    
    /**
     * Handle table export
     */
    function handleTableExport() {
        const exportButtons = document.querySelectorAll('[data-export]');
        
        exportButtons.forEach(button => {
            button.addEventListener('click', function() {
                const format = this.getAttribute('data-export');
                const tableId = this.getAttribute('data-table');
                const table = document.querySelector(tableId);
                
                if (table) {
                    exportTable(table, format);
                }
            });
        });
    }
    
    /**
     * Export table to format
     */
    function exportTable(table, format) {
        if (format === 'csv') {
            exportToCSV(table);
        } else if (format === 'excel') {
            // Handled server-side
            console.log('Excel export handled server-side');
        } else if (format === 'pdf') {
            // Handled server-side
            console.log('PDF export handled server-side');
        }
    }
    
    /**
     * Export table to CSV
     */
    function exportToCSV(table) {
        const rows = table.querySelectorAll('tr');
        const csv = [];
        
        rows.forEach(row => {
            const cells = row.querySelectorAll('th, td');
            const rowData = Array.from(cells).map(cell => {
                return '"' + cell.textContent.trim().replace(/"/g, '""') + '"';
            });
            csv.push(rowData.join(','));
        });
        
        const csvContent = csv.join('\n');
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = 'export_' + Date.now() + '.csv';
        link.click();
    }
    
    // ============================================
    // PAGINATION ENHANCEMENT
    // ============================================
    
    /**
     * Add keyboard navigation to pagination
     */
    function enhancePagination() {
        document.addEventListener('keydown', function(e) {
            const pagination = document.querySelector('.pagination');
            if (!pagination) return;
            
            // Left arrow - previous page
            if (e.key === 'ArrowLeft') {
                const prevLink = pagination.querySelector('.page-item:not(.disabled) .page-link[rel="prev"]');
                if (prevLink) prevLink.click();
            }
            
            // Right arrow - next page
            if (e.key === 'ArrowRight') {
                const nextLink = pagination.querySelector('.page-item:not(.disabled) .page-link[rel="next"]');
                if (nextLink) nextLink.click();
            }
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
    
    // ============================================
    // INITIALIZE
    // ============================================
    
    document.addEventListener('DOMContentLoaded', function() {
        enhanceTableRows();
        enhanceFilters();
        enableTableSorting();
        enableTableSearch();
        enableBulkActions();
        handleTableExport();
        enhancePagination();
    });
    
})();

// ============================================
// ADDITIONAL STYLES (injected)
// ============================================
const tableStyles = `
.data-table tbody tr.selected {
    background-color: #FEF3C7 !important;
}

.data-table thead th.sort-asc,
.data-table thead th.sort-desc {
    background: #FEF3C7;
    color: #D97706;
}

.bulk-actions-bar {
    display: none;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 1.5rem;
    background: white;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    margin-bottom: 1.5rem;
    animation: slideDown 0.3s ease-out;
}

.bulk-actions-bar .selected-count {
    font-weight: 600;
    color: var(--text-dark);
}

.bulk-actions-bar .bulk-actions {
    display: flex;
    gap: 0.5rem;
}

@keyframes slideDown {
    from {
        opacity: 0;
        transform: translateY(-20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}
`;

const styleSheet = document.createElement('style');
styleSheet.textContent = tableStyles;
document.head.appendChild(styleSheet);
