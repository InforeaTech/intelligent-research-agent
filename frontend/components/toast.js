/**
 * Toast Notification Component
 * 
 * Lightweight toast notifications for user feedback.
 * Supports multiple types: success, error, warning, info
 */

const Toast = {
    container: null,
    defaultDuration: 4000,

    /**
     * Initialize the toast container
     */
    init() {
        if (!this.container) {
            this.container = document.getElementById('toastContainer');

            if (!this.container) {
                this.container = document.createElement('div');
                this.container.id = 'toastContainer';
                this.container.className = 'toast-container';
                this.container.setAttribute('aria-live', 'polite');
                this.container.setAttribute('aria-atomic', 'true');
                document.body.appendChild(this.container);
            }
        }
    },

    /**
     * Show a toast notification
     * @param {string} message - Message to display
     * @param {string} type - Type: 'success', 'error', 'warning', 'info'
     * @param {number} duration - Duration in ms (0 for persistent)
     */
    show(message, type = 'info', duration = this.defaultDuration) {
        this.init();

        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.setAttribute('role', 'alert');

        const icon = this._getIcon(type);

        toast.innerHTML = `
            <span class="toast-icon">${icon}</span>
            <span class="toast-message">${message}</span>
            <button class="toast-close" aria-label="Close">
                <i class="fa-solid fa-xmark"></i>
            </button>
        `;

        // Close button handler
        toast.querySelector('.toast-close').addEventListener('click', () => {
            this._dismiss(toast);
        });

        this.container.appendChild(toast);

        // Auto-dismiss
        if (duration > 0) {
            setTimeout(() => this._dismiss(toast), duration);
        }

        return toast;
    },

    /**
     * Show success toast
     */
    success(message, duration) {
        return this.show(message, 'success', duration);
    },

    /**
     * Show error toast
     */
    error(message, duration) {
        return this.show(message, 'error', duration);
    },

    /**
     * Show warning toast
     */
    warning(message, duration) {
        return this.show(message, 'warning', duration);
    },

    /**
     * Show info toast
     */
    info(message, duration) {
        return this.show(message, 'info', duration);
    },

    /**
     * Dismiss a toast
     * @private
     */
    _dismiss(toast) {
        if (!toast || !toast.parentNode) return;

        toast.classList.add('toast-exit');
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    },

    /**
     * Get icon for toast type
     * @private
     */
    _getIcon(type) {
        const icons = {
            success: '<i class="fa-solid fa-circle-check"></i>',
            error: '<i class="fa-solid fa-circle-xmark"></i>',
            warning: '<i class="fa-solid fa-triangle-exclamation"></i>',
            info: '<i class="fa-solid fa-circle-info"></i>'
        };
        return icons[type] || icons.info;
    },

    /**
     * Clear all toasts
     */
    clearAll() {
        if (this.container) {
            this.container.innerHTML = '';
        }
    }
};

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Toast;
}
