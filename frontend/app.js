/**
 * Research Agent - Main Application
 * Claude-style UI with collapsible sidebar
 */

var API_BASE = API_BASE || 'http://localhost:8000/api';
var AUTH_BASE = AUTH_BASE || 'http://localhost:8000/auth';

const state = {
    currentUser: null,
    activeModuleId: null,
    outputPanel: null,
    sidebarOpen: true
};

// ==================== App Controller ====================

window.app = {
    async init() {
        console.log('App initializing...');

        // Initialize theme
        initTheme();

        // Initialize sidebar
        initSidebar();

        // Initialize output panel
        if (window.OutputPanel) {
            state.outputPanel = new OutputPanel('outputPanelContainer');
            window.outputPanel = state.outputPanel; // Global reference for tab switching
        }

        // Check authentication
        const isAuth = await checkAuth();

        // Render dashboard
        this.renderDashboard();

        console.log('App initialized');
    },

    renderDashboard() {
        const grid = document.getElementById('moduleGrid');
        console.log('Rendering dashboard, grid:', grid);
        console.log('ModuleRegistry:', window.ModuleRegistry);

        if (grid && window.ModuleRegistry) {
            const modules = window.ModuleRegistry.getAll();
            console.log('Modules found:', modules.length, modules);

            if (modules.length === 0) {
                grid.innerHTML = '<p style="color: var(--text-muted);">No modules registered. Please refresh the page.</p>';
                return;
            }

            grid.innerHTML = modules
                .map(mod => window.createResearchCard ? window.createResearchCard(mod) : `<div>Missing card renderer</div>`)
                .join('');
        } else {
            console.error('Grid or ModuleRegistry not found');
        }
    },

    navigateToDashboard() {
        const dashboard = document.getElementById('moduleDashboard');
        const activeView = document.getElementById('activeModuleView');
        const pageTitle = document.getElementById('pageTitle');
        const backBtn = document.getElementById('backBtn');

        if (dashboard) dashboard.classList.remove('hidden');
        if (activeView) activeView.classList.add('hidden');
        if (pageTitle) pageTitle.textContent = 'Research Dashboard';
        if (backBtn) backBtn.classList.add('hidden');  // Hide back button on dashboard

        state.activeModuleId = null;
    },

    selectModule(id) {
        console.log('Selecting module:', id);
        const dashboard = document.getElementById('moduleDashboard');
        const activeView = document.getElementById('activeModuleView');
        const pageTitle = document.getElementById('pageTitle');

        if (!dashboard || !activeView) return;

        dashboard.classList.add('hidden');
        activeView.classList.remove('hidden');

        // Show the back button in top bar
        const backBtn = document.getElementById('backBtn');
        if (backBtn) backBtn.classList.remove('hidden');

        const module = window.ModuleRegistry.get(id);
        if (!module) {
            console.error('Module not found:', id);
            return;
        }

        state.activeModuleId = id;

        // Update page title in top bar
        if (pageTitle) pageTitle.textContent = module.name;

        // Render form
        this.renderModuleForm(module);

        // Ensure Configuration panel is EXPANDED when selecting from dashboard
        const inputSection = document.getElementById('inputSection');
        const toggleBtn = document.getElementById('toggleInputBtn');
        if (inputSection && inputSection.classList.contains('collapsed')) {
            inputSection.classList.remove('collapsed');
            const icon = toggleBtn?.querySelector('i');
            if (icon) icon.style.transform = 'rotate(0deg)';
        }

        // Setup output panel
        if (state.outputPanel) {
            state.outputPanel.clear();
            if (module.outputTabs) {
                module.outputTabs.forEach(tab => state.outputPanel.addTab(tab.id, tab.label, tab.icon));
            }
        }

        // Close sidebar on mobile after selection
        if (window.innerWidth <= 1024) {
            closeSidebar();
        }
    },

    renderModuleForm(module) {
        const container = document.getElementById('moduleFormContainer');
        if (!container || !module.inputFields) return;

        container.innerHTML = module.inputFields
            .map(field => this.createFieldHTML(field))
            .join('');

        // Setup submit button
        const btn = document.getElementById('runResearchBtn');
        if (btn) {
            const newBtn = btn.cloneNode(true);
            btn.parentNode.replaceChild(newBtn, btn);
            newBtn.onclick = () => this.handleModuleSubmit(module);
        }
    },

    createFieldHTML(field) {
        let inputHtml = '';

        switch (field.type) {
            case 'textarea':
                inputHtml = `<textarea id="${field.id}" placeholder="${field.placeholder || ''}" rows="4"></textarea>`;
                break;

            case 'select':
            case 'multiselect':
                const multiple = field.type === 'multiselect' ? 'multiple' : '';
                inputHtml = `
                    <select id="${field.id}" ${multiple}>
                        ${field.options.map(opt =>
                    `<option value="${opt.value}">${opt.label}</option>`
                ).join('')}
                    </select>`;
                break;

            case 'checkbox':
                return `
                    <div class="control-group">
                        <input type="checkbox" id="${field.id}">
                        <label for="${field.id}" style="margin-bottom: 0;">${field.label}</label>
                    </div>`;

            case 'radio-group':
                inputHtml = `
                    <div class="form-radio-group" id="${field.id}">
                        ${field.options.map((opt, index) => `
                            <label class="radio-option">
                                <input type="radio" name="${field.id}" value="${opt.value}" 
                                       ${opt.checked || (index === 0 && !field.options.some(o => o.checked)) ? 'checked' : ''}>
                                <span class="radio-label">${opt.label}</span>
                            </label>
                        `).join('')}
                    </div>`;
                break;

            default:
                inputHtml = `<input type="${field.type}" id="${field.id}" 
                             placeholder="${field.placeholder || ''}" 
                             ${field.required ? 'required' : ''}>`;
        }

        return `
            <div class="form-group">
                <label for="${field.id}">${field.label}</label>
                ${inputHtml}
            </div>
        `;
    },

    async handleModuleSubmit(module) {
        const formData = {};

        // Collect form data
        module.inputFields.forEach(field => {
            if (field.type === 'radio-group') {
                const checked = document.querySelector(`input[name="${field.id}"]:checked`);
                formData[field.id] = checked ? checked.value : null;
            } else {
                const el = document.getElementById(field.id);
                if (!el) return;

                if (field.type === 'checkbox') {
                    formData[field.id] = el.checked;
                } else if (field.type === 'multiselect') {
                    formData[field.id] = Array.from(el.selectedOptions).map(opt => opt.value);
                } else {
                    formData[field.id] = el.value;
                }
            }
        });

        // Add global settings
        formData.apiKey = document.getElementById('apiKey')?.value || '';
        formData.modelProvider = document.getElementById('modelProvider')?.value || 'gemini';
        formData.searchProvider = document.getElementById('searchProvider')?.value || 'ddg';

        try {
            this.setLoading(true);
            const result = await module.handleSubmit(formData);

            // Render results
            if (module.renderResults && state.outputPanel) {
                module.renderResults(result, state.outputPanel);
            }

            if (window.showToast) {
                window.showToast('Analysis Complete', 'success');
            }

            // Refresh history
            if (window.HistoryManager?.loadProfiles) {
                setTimeout(() => window.HistoryManager.loadProfiles(), 1000);
            }

        } catch (e) {
            console.error('Module submit error:', e);
            if (window.showToast) {
                window.showToast(e.message || 'An error occurred', 'error');
            }
        } finally {
            this.setLoading(false);
        }
    },

    setLoading(isLoading) {
        const btn = document.getElementById('runResearchBtn');
        if (!btn) return;

        const btnText = btn.querySelector('.btn-text');
        const loader = btn.querySelector('.btn-loader');

        if (isLoading) {
            btn.disabled = true;
            if (btnText) btnText.classList.add('hidden');
            if (loader) loader.classList.remove('hidden');
        } else {
            btn.disabled = false;
            if (btnText) btnText.classList.remove('hidden');
            if (loader) loader.classList.add('hidden');
        }
    },

    toggleInputSection() {
        const section = document.getElementById('inputSection');
        const btn = document.getElementById('toggleInputBtn');

        if (!section) return;

        section.classList.toggle('collapsed');

        // Rotate icon
        const icon = btn?.querySelector('i');
        if (icon) {
            if (section.classList.contains('collapsed')) {
                icon.style.transform = 'rotate(180deg)';
            } else {
                icon.style.transform = 'rotate(0deg)';
            }
        }
    },

    // Load profile from history into view
    loadProfileIntoView(profile) {
        this.selectModule('person-research');

        // Populate form
        setTimeout(() => {
            const nameInput = document.getElementById('personName');
            const companyInput = document.getElementById('companyName');
            if (nameInput) nameInput.value = profile.name || '';
            if (companyInput) companyInput.value = profile.company || '';

            // Auto-collapse the Configuration panel for historical profiles
            const inputSection = document.getElementById('inputSection');
            const toggleBtn = document.getElementById('toggleInputBtn');
            if (inputSection && !inputSection.classList.contains('collapsed')) {
                inputSection.classList.add('collapsed');
                const icon = toggleBtn?.querySelector('i');
                if (icon) icon.style.transform = 'rotate(180deg)';
            }

            // Populate output with full notes history
            const data = {
                profile: profile.profile_text,
                notes: profile.notes || [],  // Pass full notes array for history
                id: profile.id,
                isFromHistory: true  // Flag to indicate this is a historical profile
            };

            const module = window.ModuleRegistry.get('person-research');
            if (module && state.outputPanel) {
                module.renderResults(data, state.outputPanel);
            }
        }, 100);
    }
}

// ==================== Authentication ====================

async function checkAuth() {
    try {
        const response = await fetch(`${AUTH_BASE}/user`, { credentials: 'include' });
        if (response.ok) {
            state.currentUser = await response.json();
            displayUserInfo(state.currentUser);
            return true;
        } else {
            handleLoginRedirect();
            return false;
        }
    } catch (error) {
        console.error('Auth check failed:', error);
        handleLoginRedirect();
        return false;
    }
}

function handleLoginRedirect() {
    if (!window.location.pathname.includes('login.html')) {
        window.location.href = '/login.html';
    }
}

function displayUserInfo(user) {
    const userProfileDiv = document.getElementById('userProfile');
    if (!userProfileDiv) return;

    const initials = user.name
        ? user.name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase()
        : user.email[0].toUpperCase();

    userProfileDiv.innerHTML = `
        ${user.picture
            ? `<img src="${user.picture}" alt="${user.name}" class="user-avatar">`
            : `<div class="user-avatar-placeholder">${initials}</div>`
        }
        <div class="user-info">
            <div class="user-name">${user.name || 'User'}</div>
        </div>
        <button class="logout-btn" onclick="logout()" title="Logout">
            <i class="fa-solid fa-right-from-bracket"></i>
        </button>
    `;
}

async function logout() {
    try {
        await fetch(`${AUTH_BASE}/logout`, { method: 'POST', credentials: 'include' });
    } catch (error) {
        console.error('Logout error:', error);
    }
    window.location.href = '/login.html';
}

// ==================== Sidebar ====================

function initSidebar() {
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('mainContent');
    const toggleBtn = document.getElementById('sidebarToggleBtn');
    const closeBtn = document.getElementById('sidebarCloseBtn');
    const overlay = document.getElementById('sidebarOverlay');
    const newResearchBtn = document.getElementById('newResearchBtn');

    console.log('Initializing sidebar:', { sidebar, toggleBtn, closeBtn });

    // Load saved state (desktop only)
    if (window.innerWidth > 1024) {
        const savedState = localStorage.getItem('sidebarCollapsed');
        if (savedState === 'true') {
            sidebar?.classList.add('collapsed');
            mainContent?.classList.add('expanded');
            state.sidebarOpen = false;
        }
    }

    // Toggle button click handler
    if (toggleBtn) {
        toggleBtn.addEventListener('click', () => {
            console.log('Toggle sidebar clicked');
            toggleSidebar();
        });
    }

    // Close button (mobile)
    if (closeBtn) {
        closeBtn.addEventListener('click', () => {
            console.log('Close sidebar clicked');
            closeSidebar();
        });
    }

    // Overlay click (mobile)
    if (overlay) {
        overlay.addEventListener('click', closeSidebar);
    }

    // New research button
    if (newResearchBtn) {
        newResearchBtn.addEventListener('click', () => {
            window.app.navigateToDashboard();
            if (window.innerWidth <= 1024) {
                closeSidebar();
            }
        });
    }

    // Handle resize
    let resizeTimer;
    window.addEventListener('resize', () => {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(() => {
            if (window.innerWidth > 1024) {
                overlay?.classList.remove('visible');
                sidebar?.classList.remove('open');
            }
        }, 100);
    });
}

function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('mainContent');
    const overlay = document.getElementById('sidebarOverlay');

    const isMobile = window.innerWidth <= 1024;

    if (isMobile) {
        // Mobile: slide in/out with overlay
        const isOpen = sidebar?.classList.contains('open');
        if (isOpen) {
            closeSidebar();
        } else {
            sidebar?.classList.add('open');
            sidebar?.classList.remove('collapsed');
            overlay?.classList.add('visible');
        }
    } else {
        // Desktop: toggle collapsed state
        sidebar?.classList.toggle('collapsed');
        mainContent?.classList.toggle('expanded');

        // Save state to localStorage
        const isNowCollapsed = sidebar?.classList.contains('collapsed');
        state.sidebarOpen = !isNowCollapsed;
        localStorage.setItem('sidebarCollapsed', isNowCollapsed);
    }
}

function closeSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');

    sidebar?.classList.remove('open');
    overlay?.classList.remove('visible');
}

// ==================== Theme ====================

function initTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);

    const themeBtn = document.getElementById('themeToggle');
    if (themeBtn) {
        themeBtn.addEventListener('click', () => {
            const current = document.documentElement.getAttribute('data-theme') || 'light';
            const next = current === 'light' ? 'dark' : 'light';

            document.documentElement.setAttribute('data-theme', next);
            localStorage.setItem('theme', next);
            updateThemeIcon(next);
        });
    }
}

function updateThemeIcon(theme) {
    const icon = document.querySelector('#themeToggle i');
    if (icon) {
        icon.className = theme === 'light' ? 'fa-solid fa-moon' : 'fa-solid fa-sun';
    }
}

// ==================== Toast Notifications ====================

function showToast(message, type = 'info', duration = 4000) {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const iconMap = {
        success: 'fa-circle-check',
        error: 'fa-circle-xmark',
        warning: 'fa-triangle-exclamation',
        info: 'fa-circle-info'
    };

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <i class="toast-icon fa-solid ${iconMap[type] || iconMap.info}"></i>
        <span class="toast-message">${message}</span>
        <button class="toast-close" onclick="this.parentElement.remove()">
            <i class="fa-solid fa-xmark"></i>
        </button>
    `;

    container.appendChild(toast);

    // Auto remove
    setTimeout(() => {
        toast.classList.add('toast-exit');
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

window.showToast = showToast;
window.logout = logout;
window.toggleSidebar = toggleSidebar;
window.closeSidebar = closeSidebar;

// ==================== Initialize on DOM Ready ====================

document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, initializing app...');
    // Small delay to ensure all scripts are loaded
    setTimeout(() => {
        window.app.init();
    }, 50);
});
