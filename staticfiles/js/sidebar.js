/**
 * Sidebar & Navigation JavaScript
 * Materially-inspired interactions
 */

(function() {
    'use strict';

    // DOM Elements
    const body = document.body;
    const menuToggle = document.getElementById('menu-toggle');
    const sidebarOverlay = document.getElementById('sidebar-overlay');
    const navLinks = document.querySelectorAll('.nav-link');

    // Constants
    const STORAGE_KEY = 'sidebar-collapsed';
    const MOBILE_BREAKPOINT = 768;

    /**
     * Check if device is mobile
     */
    function isMobile() {
        return window.innerWidth < MOBILE_BREAKPOINT;
    }

    /**
     * Toggle sidebar collapsed state
     */
    function toggleSidebar() {
        if (isMobile()) {
            body.classList.toggle('sidebar-mobile-open');
            sidebarOverlay.classList.toggle('active');
            
            // Prevent body scroll when sidebar is open on mobile
            if (body.classList.contains('sidebar-mobile-open')) {
                body.style.overflow = 'hidden';
            } else {
                body.style.overflow = '';
            }
        } else {
            body.classList.toggle('sidebar-collapsed');
            
            // Save state to localStorage
            const isCollapsed = body.classList.contains('sidebar-collapsed');
            localStorage.setItem(STORAGE_KEY, isCollapsed);
        }
    }

    /**
     * Close mobile sidebar
     */
    function closeMobileSidebar() {
        if (isMobile()) {
            body.classList.remove('sidebar-mobile-open');
            sidebarOverlay.classList.remove('active');
            body.style.overflow = '';
        }
    }

    /**
     * Set active nav link based on current URL
     */
    function setActiveNavLink() {
        const currentPath = window.location.pathname;
        
        navLinks.forEach(link => {
            const linkPath = link.getAttribute('href');
            
            if (linkPath && currentPath.includes(linkPath) && linkPath !== '/') {
                link.classList.add('active');
            } else if (linkPath === '/' && currentPath === '/') {
                link.classList.add('active');
            } else {
                link.classList.remove('active');
            }
        });
    }

    /**
     * Handle window resize
     */
    function handleResize() {
        if (!isMobile()) {
            body.classList.remove('sidebar-mobile-open');
            sidebarOverlay.classList.remove('active');
            body.style.overflow = '';
        }
    }

    /**
     * Restore sidebar state from localStorage
     */
    function restoreSidebarState() {
        if (!isMobile()) {
            const isCollapsed = localStorage.getItem(STORAGE_KEY) === 'true';
            if (isCollapsed) {
                body.classList.add('sidebar-collapsed');
            }
        }
    }

    /**
     * Add smooth scroll behavior to nav links
     */
    function initSmoothScroll() {
        navLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                // Close mobile sidebar when clicking a link
                closeMobileSidebar();
                
                // Add loading animation
                const icon = this.querySelector('.nav-link-icon');
                if (icon) {
                    icon.style.transform = 'rotate(360deg)';
                    setTimeout(() => {
                        icon.style.transform = '';
                    }, 300);
                }
            });
        });
    }

    /**
     * Initialize tooltips for collapsed sidebar (desktop)
     */
    function initTooltips() {
        if (!isMobile() && body.classList.contains('sidebar-collapsed')) {
            navLinks.forEach(link => {
                const text = link.querySelector('.nav-link-text');
                if (text) {
                    link.setAttribute('title', text.textContent.trim());
                }
            });
        }
    }

    /**
     * Add ripple effect to buttons
     */
    function createRipple(event) {
        const button = event.currentTarget;
        const ripple = document.createElement('span');
        const rect = button.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = event.clientX - rect.left - size / 2;
        const y = event.clientY - rect.top - size / 2;

        ripple.style.width = ripple.style.height = size + 'px';
        ripple.style.left = x + 'px';
        ripple.style.top = y + 'px';
        ripple.classList.add('ripple');

        button.appendChild(ripple);

        setTimeout(() => {
            ripple.remove();
        }, 600);
    }

    /**
     * Initialize all functionality
     */
    function init() {
        // Restore sidebar state
        restoreSidebarState();

        // Set active nav link
        setActiveNavLink();

        // Initialize smooth scroll
        initSmoothScroll();

        // Initialize tooltips
        initTooltips();

        // Event Listeners
        if (menuToggle) {
            menuToggle.addEventListener('click', toggleSidebar);
        }

        if (sidebarOverlay) {
            sidebarOverlay.addEventListener('click', closeMobileSidebar);
        }

        // Handle window resize with debounce
        let resizeTimeout;
        window.addEventListener('resize', function() {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(handleResize, 150);
        });

        // Add ripple effect to buttons
        document.querySelectorAll('.btn-modern, .btn-primary-modern').forEach(button => {
            button.addEventListener('click', createRipple);
        });

        // Handle escape key to close mobile sidebar
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && body.classList.contains('sidebar-mobile-open')) {
                closeMobileSidebar();
            }
        });

        // Add stagger animation to nav items
        navLinks.forEach((link, index) => {
            link.style.animationDelay = `${index * 0.05}s`;
            link.classList.add('animate-fade-in-left');
        });
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();

// Add ripple CSS dynamically
const style = document.createElement('style');
style.textContent = `
    .ripple {
        position: absolute;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.6);
        transform: scale(0);
        animation: ripple-animation 0.6s ease-out;
        pointer-events: none;
    }

    @keyframes ripple-animation {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }

    button {
        position: relative;
        overflow: hidden;
    }
`;
document.head.appendChild(style);
