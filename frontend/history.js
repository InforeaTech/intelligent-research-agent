/**
 * History Sidebar Management
 * Updated for Claude-style UI layout
 */

var API_BASE = API_BASE || 'http://localhost:8000/api';

const HistoryManager = {
    sidebar: null,
    mainContent: null,
    historyList: null,
    currentProfileId: null,
    lastFocusedElement: null,

    // Pagination state
    currentSkip: 0,
    pageSize: 20,
    totalProfiles: 0,
    currentSort: 'recent',
    isSearching: false,

    init() {
        // Use new element IDs from Claude-style layout
        this.sidebar = document.getElementById('sidebar');
        this.mainContent = document.getElementById('mainContent');
        this.historyList = document.getElementById('historyList');

        if (!this.sidebar || !this.historyList) {
            console.warn('History sidebar elements not found');
            return;
        }

        // Search with debounce
        const searchInput = document.getElementById('historySearch');
        if (searchInput) {
            let searchTimeout;
            searchInput.addEventListener('input', (e) => {
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(() => this.handleSearch(e.target.value), 300);
            });
        }

        // Load More button
        const loadMoreBtn = document.getElementById('loadMoreBtn');
        if (loadMoreBtn) {
            loadMoreBtn.addEventListener('click', () => this.loadMore());
        }

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.sidebar && !this.sidebar.classList.contains('collapsed')) {
                this.close();
            }
        });

        // Load recent profiles on init
        this.loadProfiles();
    },

    // Toast notification system
    showToast(message, type = 'info', duration = 3000) {
        const container = document.getElementById('toastContainer');
        if (!container) return;

        const icons = {
            success: '<i class="fa-solid fa-circle-check toast-icon"></i>',
            error: '<i class="fa-solid fa-circle-xmark toast-icon"></i>',
            warning: '<i class="fa-solid fa-triangle-exclamation toast-icon"></i>',
            info: '<i class="fa-solid fa-circle-info toast-icon"></i>'
        };

        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            ${icons[type] || icons.info}
            <span class="toast-message">${message}</span>
            <button class="toast-close" aria-label="Close notification"><i class="fa-solid fa-xmark"></i></button>
        `;

        container.appendChild(toast);

        // Close button
        toast.querySelector('.toast-close').addEventListener('click', () => {
            this.dismissToast(toast);
        });

        // Auto dismiss
        setTimeout(() => this.dismissToast(toast), duration);
    },

    dismissToast(toast) {
        if (!toast || toast.classList.contains('toast-exit')) return;
        toast.classList.add('toast-exit');
        setTimeout(() => toast.remove(), 300);
    },

    async loadProfiles(skip = 0, limit = 20, sort = 'recent', append = false) {
        const skeleton = document.getElementById('historySkeleton');

        if (!append && skeleton) {
            skeleton.classList.remove('hidden');
        }

        try {
            const response = await fetch(`${API_BASE}/profiles?skip=${skip}&limit=${limit}&sort=${sort}`, {
                credentials: 'include'
            });

            if (response.status === 401) {
                this.showEmpty(true);
                return;
            }

            if (!response.ok) throw new Error('Failed to load history');

            const data = await response.json();
            this.totalProfiles = data.total;
            this.currentSkip = skip + data.profiles.length;
            this.renderProfiles(data.profiles, data.total, append);
            this.updateLoadMoreButton();
        } catch (error) {
            console.error('History load failed:', error);
            this.showEmpty(true);
        } finally {
            if (skeleton) skeleton.classList.add('hidden');
        }
    },

    async loadMore() {
        const btn = document.getElementById('loadMoreBtn');
        if (!btn) return;

        const text = btn.querySelector('.load-more-text');
        const spinner = btn.querySelector('.load-more-spinner');

        btn.disabled = true;
        if (text) text.textContent = 'Loading...';
        if (spinner) spinner.classList.remove('hidden');

        await this.loadProfiles(this.currentSkip, this.pageSize, this.currentSort, true);

        btn.disabled = false;
        if (text) text.textContent = 'Load More';
        if (spinner) spinner.classList.add('hidden');
    },

    updateLoadMoreButton() {
        const btn = document.getElementById('loadMoreBtn');
        if (btn) {
            const hasMore = this.currentSkip < this.totalProfiles;
            btn.classList.toggle('hidden', !hasMore || this.isSearching);
        }
    },

    renderProfiles(profiles, total, append = false) {
        if (!this.historyList) return;

        if (profiles.length === 0 && !append) {
            this.showEmpty(true);
            return;
        }

        this.showEmpty(false);
        const html = profiles.map(profile => `
            <div class="history-item" data-id="${profile.id}" onclick="HistoryManager.loadProfile(${profile.id})" role="listitem" tabindex="0">
                <div class="history-item-header">
                    <span class="history-item-title">${this.escapeHtml(profile.name)}</span>
                    <button class="history-item-delete" onclick="HistoryManager.deleteProfile(${profile.id}, event)" title="Delete" aria-label="Delete profile">
                        <i class="fa-regular fa-trash-can"></i>
                    </button>
                </div>
                <div class="history-item-subtitle">
                    ${profile.company ? `<i class="fa-solid fa-building"></i> ${this.escapeHtml(profile.company)}` : ''}
                    <span><i class="fa-regular fa-clock"></i> ${this.formatDate(profile.timestamp)}</span>
                </div>
            </div>
        `).join('');

        if (append) {
            this.historyList.insertAdjacentHTML('beforeend', html);
        } else {
            this.historyList.innerHTML = html;
        }
    },

    async loadProfile(profileId) {
        try {
            const response = await fetch(`${API_BASE}/profiles/${profileId}`, {
                credentials: 'include'
            });

            if (!response.ok) throw new Error('Failed to load profile');

            const profile = await response.json();

            // Populate main view using App Controller
            if (window.app && window.app.loadProfileIntoView) {
                window.app.loadProfileIntoView(profile);
            } else {
                console.error('App controller not initialized');
            }

            // Mark as active in sidebar
            this.setActiveProfile(profileId);

            // Toast notification
            this.showToast(`Loaded "${profile.name}"`, 'success');

        } catch (error) {
            this.showToast(`Error loading profile: ${error.message}`, 'error');
        }
    },

    async deleteProfile(profileId, event) {
        event.stopPropagation();

        if (!confirm('Delete this profile and all its notes?')) return;

        try {
            const response = await fetch(`${API_BASE}/profiles/${profileId}`, {
                method: 'DELETE',
                credentials: 'include'
            });

            if (!response.ok) throw new Error('Failed to delete profile');

            const item = this.historyList.querySelector(`[data-id="${profileId}"]`);
            if (item) item.remove();

            if (this.historyList.children.length === 0) {
                this.showEmpty(true);
            }

            // Toast notification
            this.showToast('Profile deleted', 'success');

        } catch (error) {
            this.showToast(`Error deleting: ${error.message}`, 'error');
        }
    },

    close() {
        if (!this.sidebar) return;
        this.sidebar.classList.add('collapsed');
        if (this.mainContent) {
            this.mainContent.classList.add('expanded');
        }
    },

    setActiveProfile(profileId) {
        this.currentProfileId = profileId;
        if (!this.historyList) return;
        this.historyList.querySelectorAll('.history-item').forEach(item => {
            item.classList.toggle('active', parseInt(item.dataset.id) === profileId);
        });
    },

    showEmpty(show) {
        const emptyState = document.getElementById('historyEmpty');
        if (emptyState) {
            emptyState.classList.toggle('hidden', !show);
        }
    },

    formatDate(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diff = now - date;

        const minutes = Math.floor(diff / 60000);
        const hours = Math.floor(diff / 3600000);
        const days = Math.floor(diff / 86400000);

        if (minutes < 1) return 'just now';
        if (minutes < 60) return `${minutes}m ago`;
        if (hours < 24) return `${hours}h ago`;
        if (days < 7) return `${days}d ago`;
        return date.toLocaleDateString();
    },

    async handleSearch(query) {
        if (!query || query.length < 2) {
            this.isSearching = false;
            this.currentSkip = 0;
            this.loadProfiles();
            return;
        }

        this.isSearching = true;
        this.showEmpty(false);
        this.updateLoadMoreButton();

        try {
            const response = await fetch(`${API_BASE}/profiles/search?q=${encodeURIComponent(query)}`, {
                credentials: 'include'
            });

            if (!response.ok) throw new Error('Search failed');

            const data = await response.json();
            this.renderProfiles(data.results, data.count);
        } catch (error) {
            console.error('Search error:', error);
            this.showEmpty(true);
        }
    },

    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
};

// Make showToast globally accessible
function showToast(message, type = 'info', duration = 3000) {
    HistoryManager.showToast(message, type, duration);
}

window.showToast = showToast;
window.HistoryManager = HistoryManager;

// Initialize on page load - delayed to ensure DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
        HistoryManager.init();
    }, 200);
});
