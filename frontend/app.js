const API_BASE = 'http://localhost:8000/api';
const AUTH_BASE = 'http://localhost:8000/auth';

// Authentication State
let currentUser = null;

// DOM Elements
const researchBtn = document.getElementById('researchBtn');
const generateNoteBtn = document.getElementById('generateNoteBtn');
const resultsArea = document.getElementById('resultsArea');
const profileContent = document.getElementById('profileContent');
const noteResult = document.getElementById('noteResult');
const charCount = document.getElementById('charCount');

const apiKeyInput = document.getElementById('apiKey');
const modelProviderSelect = document.getElementById('modelProvider');
const searchProviderSelect = document.getElementById('searchProvider');
const serperKeyInput = document.getElementById('serperKey');

// ==================== Authentication Functions ====================

/**
 * Check if user is authenticated
 */
async function checkAuth() {
    try {
        const response = await fetch(`${AUTH_BASE}/user`, {
            credentials: 'include' // Include cookies
        });

        if (response.ok) {
            currentUser = await response.json();
            displayUserInfo(currentUser);
            return true;
        } else {
            currentUser = null;
            // Redirect to login if not authenticated
            window.location.href = '/login.html';
            return false;
        }
    } catch (error) {
        console.error('Auth check failed:', error);
        currentUser = null;
        window.location.href = '/login.html';
        return false;
    }
}

/**
 * Display user information in header
 */
function displayUserInfo(user) {
    const apiKeyContainer = document.querySelector('.api-key-container');

    // Check if user profile already exists
    let userProfileDiv = document.getElementById('userProfile');
    if (!userProfileDiv) {
        userProfileDiv = document.createElement('div');
        userProfileDiv.id = 'userProfile';
        userProfileDiv.className = 'user-profile';

        // Insert before API key container
        apiKeyContainer.parentNode.insertBefore(userProfileDiv, apiKeyContainer);
    }

    // Build user profile HTML
    const initials = user.name ? user.name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase() : user.email[0].toUpperCase();

    userProfileDiv.innerHTML = `
        ${user.picture
            ? `<img src="${user.picture}" alt="${user.name || 'User'}" class="user-avatar">`
            : `<div class="user-avatar-placeholder">${initials}</div>`
        }
        <div class="user-info">
            <div class="user-name">${user.name || 'User'}</div>
            <div class="user-email">${user.email}</div>
        </div>
        <button class="logout-btn" onclick="logout()">
            <i class="fa-solid fa-right-from-bracket"></i> Logout
        </button>
    `;
}

/**
 * Logout user
 */
async function logout() {
    try {
        await fetch(`${AUTH_BASE}/logout`, {
            method: 'POST',
            credentials: 'include'
        });

        currentUser = null;
        window.location.href = '/login.html';
    } catch (error) {
        console.error('Logout failed:', error);
        // Force redirect even if logout fails
        window.location.href = '/login.html';
    }
}

/**
 * Handle 401 Unauthorized responses
 */
function handle401(response) {
    if (response.status === 401) {
        window.location.href = '/login.html';
        return true;
    }
    return false;
}

// State
let currentProfileText = "";

// Event Listeners
researchBtn.addEventListener('click', handleResearch);
generateNoteBtn.addEventListener('click', handleGenerateNote);
document.getElementById('copyProfileBtn').addEventListener('click', () => copyToClipboard(currentProfileText));
document.getElementById('copyNoteBtn').addEventListener('click', () => copyToClipboard(noteResult.value));
noteResult.addEventListener('input', updateCharCount);

searchProviderSelect.addEventListener('change', (e) => {
    if (e.target.value === 'serper') {
        serperKeyInput.classList.remove('hidden');
    } else {
        serperKeyInput.classList.add('hidden');
    }
});

async function handleResearch() {
    const name = document.getElementById('personName').value.trim();
    const company = document.getElementById('companyName').value.trim();
    const additionalInfo = document.getElementById('additionalInfo').value.trim();
    const apiKey = apiKeyInput.value.trim();
    const modelProvider = modelProviderSelect.value;
    const serperKey = serperKeyInput.value.trim();

    if (!name) {
        alert('Please enter a name.');
        return;
    }

    setLoading(true);
    resultsArea.classList.add('hidden');

    try {
        const payload = {
            name,
            company,
            additional_info: additionalInfo,
            api_key: apiKey,
            model_provider: modelProvider,
            search_provider: searchProviderSelect.value
        };

        if (searchProviderSelect.value === 'serper') {
            payload.serper_api_key = serperKey;
        }

        const response = await fetch(`${API_BASE}/research`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include', // Include auth cookies
            body: JSON.stringify(payload)
        });

        if (handle401(response)) return; // Redirect to login if not authenticated

        if (!response.ok) {
            const err = await response.json();
            // Handle both string and object error details
            let errorMessage = 'Research failed';
            if (err.detail) {
                if (typeof err.detail === 'string') {
                    errorMessage = err.detail;
                } else if (Array.isArray(err.detail)) {
                    // Pydantic validation errors come as an array
                    errorMessage = err.detail.map(e => e.msg || JSON.stringify(e)).join(', ');
                } else if (typeof err.detail === 'object') {
                    errorMessage = err.detail.msg || JSON.stringify(err.detail);
                }
            }
            throw new Error(errorMessage);
        }

        const data = await response.json();
        currentProfileText = data.profile;

        // Display cache indicator for profile
        const profileHeader = document.querySelector('.profile-section .card-header h2');
        if (data.from_cache) {
            if (!document.getElementById('profileCacheBadge')) {
                const badge = document.createElement('span');
                badge.id = 'profileCacheBadge';
                badge.className = 'cache-badge';
                badge.textContent = '⚡ From Cache';
                profileHeader.appendChild(badge);
            }
        } else {
            const existingBadge = document.getElementById('profileCacheBadge');
            if (existingBadge) existingBadge.remove();
        }

        // Render Markdown
        profileContent.innerHTML = marked.parse(data.profile);
        resultsArea.classList.remove('hidden');

        // Auto-populate cached note if available
        if (data.cached_note) {
            noteResult.value = data.cached_note;
            updateCharCount();

            // Show cache badge for note
            const noteHeader = document.querySelector('.note-section .card-header h2');
            if (data.cached_note_from_cache) {
                if (!document.getElementById('noteCacheBadge')) {
                    const badge = document.createElement('span');
                    badge.id = 'noteCacheBadge';
                    badge.className = 'cache-badge';
                    badge.textContent = '⚡ From Cache';
                    noteHeader.appendChild(badge);
                }
            }
        } else {
            // Generate a new note if no cached note available
            handleGenerateNote();
        }

    } catch (error) {
        // Check if it's a validation error about the name
        if (error.message.includes('Full name must include') ||
            error.message.includes('Name must contain') ||
            error.message.includes('Name cannot be empty') ||
            error.message.includes('Invalid input')) {

            // Extract the actual error message
            let errorText = error.message;
            // Remove "Invalid input: " prefix if present
            errorText = errorText.replace(/Invalid input:\s*/i, '');
            // Remove "Value error, " prefix from Pydantic
            errorText = errorText.replace(/Value error,\s*/i, '');

            // Display inline error message
            const existingAlert = document.querySelector('.validation-alert');
            if (existingAlert) existingAlert.remove();

            const alertContainer = document.createElement('div');
            alertContainer.className = 'validation-alert';
            alertContainer.style.cssText = 'background: #fee2e2; border: 1px solid #ef4444; color: #991b1b; padding: 12px; border-radius: 8px; margin-top: 8px; font-size: 14px;';
            alertContainer.innerHTML = `<strong>⚠️ Invalid Name!</strong><br>${errorText}<br><em style="font-size: 12px; color: #7f1d1d;">Example: "John Doe"</em>`;
            document.getElementById('personName').parentElement.appendChild(alertContainer);
            setTimeout(() => {
                alertContainer.remove();
            }, 7000);

            // Refocus on the name input field
            document.getElementById('personName').focus();
            document.getElementById('personName').select();
        } else {
            alert(`Error: ${error.message}`);
        }
    } finally {
        setLoading(false);
    }
}

async function handleGenerateNote() {
    if (!currentProfileText) return;

    const length = parseInt(document.getElementById('noteLength').value);
    const tone = document.getElementById('noteTone').value;
    const context = document.getElementById('noteContext').value;
    const apiKey = apiKeyInput.value.trim();
    const modelProvider = modelProviderSelect.value;

    generateNoteBtn.disabled = true;
    generateNoteBtn.textContent = 'Generating...';

    try {
        const response = await fetch(`${API_BASE}/generate-note`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include', // Include auth cookies
            body: JSON.stringify({
                profile_text: currentProfileText,
                length,
                tone,
                context,
                api_key: apiKey,
                model_provider: modelProvider
            })
        });

        if (handle401(response)) return; // Redirect to login if not authenticated

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || 'Note generation failed');
        }

        const data = await response.json();
        noteResult.value = data.note;
        updateCharCount();

        // Display cache indicator for note
        const noteHeader = document.querySelector('.note-section .card-header h2');
        if (data.from_cache) {
            if (!document.getElementById('noteCacheBadge')) {
                const badge = document.createElement('span');
                badge.id = 'noteCacheBadge';
                badge.className = 'cache-badge';
                badge.textContent = '⚡ From Cache';
                noteHeader.appendChild(badge);
            }
        } else {
            const existingBadge = document.getElementById('noteCacheBadge');
            if (existingBadge) existingBadge.remove();
        }

    } catch (error) {
        alert(`Error: ${error.message}`);
    } finally {
        generateNoteBtn.disabled = false;
        generateNoteBtn.textContent = 'Generate Note';
    }
}

function setLoading(isLoading) {
    const btnText = researchBtn.querySelector('.btn-text');
    const loader = researchBtn.querySelector('.loader');

    if (isLoading) {
        researchBtn.disabled = true;
        btnText.classList.add('hidden');
        loader.classList.remove('hidden');
    } else {
        researchBtn.disabled = false;
        btnText.classList.remove('hidden');
        loader.classList.add('hidden');
    }
}

function updateCharCount() {
    const count = noteResult.value.length;
    charCount.textContent = `${count} chars`;
    if (count > 300) {
        charCount.style.color = '#ef4444'; // Red warning
    } else {
        charCount.style.color = '#94a3b8';
    }
}

async function copyToClipboard(text) {
    if (!text) return;
    try {
        await navigator.clipboard.writeText(text);
        alert('Copied to clipboard!');
    } catch (err) {
        console.error('Failed to copy:', err);
    }
}

// ==================== Initialize ====================

// Check authentication on page load
window.addEventListener('DOMContentLoaded', () => {
    checkAuth();
});

