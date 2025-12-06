/**
 * Person Research Module
 * Deep research on individuals using AI agents
 */

const PersonResearchModule = {
    id: 'person-research',
    name: 'Person Research',
    description: 'Deep research on individuals using AI-powered analysis. Get comprehensive profiles with background, insights, and key information.',
    icon: 'fa-solid fa-user-tie',
    accentColor: '#3B82F6', // Blue

    inputFields: [
        {
            id: 'personName',
            label: 'Person Name',
            type: 'text',
            placeholder: 'Enter full name (e.g., Satya Nadella)',
            required: true
        },
        {
            id: 'companyName',
            label: 'Company / Organization',
            type: 'text',
            placeholder: 'Current or relevant company',
            required: false
        },
        {
            id: 'additionalInfo',
            label: 'Additional Context',
            type: 'textarea',
            placeholder: 'Any additional context to narrow down search (role, location, etc.)',
            required: false
        },
        {
            id: 'searchMode',
            label: 'Search Mode',
            type: 'radio-group',
            options: [
                { value: 'rag', label: 'RAG', checked: true },
                { value: 'tools', label: 'Tools' },
                { value: 'hybrid', label: 'Hybrid' }
            ]
        },
        {
            id: 'bypassCache',
            label: 'Bypass cache (force fresh results)',
            type: 'checkbox'
        }
    ],

    outputTabs: [
        { id: 'profile', label: 'Profile', icon: 'fa-solid fa-id-card' },
        { id: 'note', label: 'Outreach Note', icon: 'fa-solid fa-envelope' },
        { id: 'deep', label: 'Deep Research', icon: 'fa-solid fa-microscope' }
    ],

    async handleSubmit(formData) {
        const API_BASE = 'http://localhost:8000/api';

        // Store profile ID for note generation
        this.currentProfileId = null;

        // 1. Generate profile
        const profileResponse = await fetch(`${API_BASE}/research`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({
                name: formData.personName,
                company: formData.companyName,
                additional_info: formData.additionalInfo || '',
                api_key: formData.apiKey || '',
                model_provider: formData.modelProvider || 'gemini',
                search_provider: formData.searchProvider || 'ddg',
                search_mode: formData.searchMode || 'rag',
                bypass_cache: formData.bypassCache || false
            })
        });

        if (!profileResponse.ok) {
            const error = await profileResponse.json();
            throw new Error(error.detail || 'Failed to generate profile');
        }

        const profileData = await profileResponse.json();
        this.currentProfileId = profileData.id;

        return {
            profile: profileData.profile,
            cached_note: profileData.cached_note,
            from_cache: profileData.from_cache,
            id: profileData.id,
            research_data: profileData.research_data
        };
    },

    renderResults(data, outputPanel) {
        // Profile tab
        let profileContent = data.profile || 'No profile generated.';
        if (data.from_cache) {
            profileContent = `<span class="cache-badge"><i class="fa-solid fa-bolt"></i> CACHED</span>\n\n${profileContent}`;
        }
        outputPanel.setContent('profile', profileContent);

        // Note tab - show notes history if available, or generation form
        if (data.notes && data.notes.length > 0) {
            // Show notes history with option to generate new
            outputPanel.setContent('note', this.getNotesHistoryHTML(data.notes, data.id), () => this.setupNotesHistory(data.id, outputPanel));
        } else if (data.cached_note) {
            // Backward compatibility: single cached note
            outputPanel.setContent('note', `<span class="history-badge"><i class="fa-solid fa-history"></i> FROM HISTORY</span>\n\n${data.cached_note}`);
        } else {
            // No notes - show generation form
            outputPanel.setContent('note', this.getNoteFormHTML(data.id), () => this.setupNoteForm(data.id, outputPanel));
        }

        // Deep research tab - pass setup callback
        outputPanel.setContent('deep', this.getDeepResearchFormHTML(), () => this.setupDeepResearchForm(outputPanel));

        // Activate profile tab
        outputPanel.activateTab('profile');
    },

    getNotesHistoryHTML(notes, profileId) {
        const sortedNotes = [...notes].sort((a, b) => new Date(b.timestamp || b.created_at) - new Date(a.timestamp || a.created_at));

        return `
<div class="notes-history">
    <div class="notes-history-header">
        <h4><i class="fa-solid fa-history"></i> Previous Notes (${notes.length})</h4>
        <button class="btn-secondary" id="showNoteFormBtn">
            <i class="fa-solid fa-plus"></i> Generate New Note
        </button>
    </div>
    
    <!-- New Note Form (hidden by default) -->
    <div id="newNoteFormContainer" class="new-note-form hidden">
        ${this.getNoteFormHTML(profileId)}
    </div>
    
    <!-- Notes List -->
    <div class="notes-list">
        ${sortedNotes.map((note, index) => `
            <div class="note-card" data-note-index="${index}">
                <div class="note-card-header" onclick="this.parentElement.classList.toggle('expanded')">
                    <div class="note-meta">
                        <span class="note-tone"><i class="fa-solid fa-palette"></i> ${note.tone || 'professional'}</span>
                        <span class="note-length"><i class="fa-solid fa-text-width"></i> ${note.length || 'medium'}</span>
                        <span class="note-date"><i class="fa-regular fa-clock"></i> ${this.formatDate(note.timestamp || note.created_at)}</span>
                    </div>
                    <i class="fa-solid fa-chevron-down expand-icon"></i>
                </div>
                <div class="note-card-body">
                    <div class="markdown-content">${window.marked ? marked.parse(note.note_text || note.note_content || '') : (note.note_text || note.note_content || '')}</div>
                    <div class="note-actions">
                        <button class="btn-icon copy-note-btn" data-note-index="${index}" title="Copy to clipboard">
                            <i class="fa-regular fa-copy"></i>
                        </button>
                    </div>
                </div>
            </div>
        `).join('')}
    </div>
</div>
        `;
    },

    formatDate(dateStr) {
        if (!dateStr) return 'Unknown';
        const date = new Date(dateStr);
        const now = new Date();
        const diff = now - date;

        // Less than 24 hours
        if (diff < 86400000) {
            const hours = Math.floor(diff / 3600000);
            if (hours < 1) return 'Just now';
            return `${hours}h ago`;
        }
        // Less than 7 days
        if (diff < 604800000) {
            const days = Math.floor(diff / 86400000);
            return `${days}d ago`;
        }
        // Otherwise show date
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    },

    setupNotesHistory(profileId, outputPanel) {
        // Toggle new note form visibility
        const showFormBtn = document.getElementById('showNoteFormBtn');
        const formContainer = document.getElementById('newNoteFormContainer');

        if (showFormBtn && formContainer) {
            showFormBtn.addEventListener('click', () => {
                formContainer.classList.toggle('hidden');
                showFormBtn.innerHTML = formContainer.classList.contains('hidden')
                    ? '<i class="fa-solid fa-plus"></i> Generate New Note'
                    : '<i class="fa-solid fa-minus"></i> Hide Form';
            });
        }

        // Setup the note generation form inside the container
        this.setupNoteForm(profileId, outputPanel);

        // Setup copy buttons
        document.querySelectorAll('.copy-note-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const noteCard = btn.closest('.note-card');
                const content = noteCard.querySelector('.markdown-content')?.textContent || '';
                navigator.clipboard.writeText(content).then(() => {
                    if (window.showToast) window.showToast('Note copied!', 'success');
                });
            });
        });
    },

    getNoteFormHTML(profileId) {
        return `
<div class="note-generator">
    <h4><i class="fa-solid fa-wand-magic-sparkles"></i> Generate Outreach Note</h4>
    
    <div class="form-group">
        <label for="noteLength">Length</label>
        <select id="noteLength">
            <option value="short">Short (2-3 sentences)</option>
            <option value="medium" selected>Medium (1 paragraph)</option>
            <option value="long">Long (2-3 paragraphs)</option>
        </select>
    </div>
    
    <div class="form-group">
        <label for="noteTone">Tone</label>
        <select id="noteTone">
            <option value="professional" selected>Professional</option>
            <option value="friendly">Friendly</option>
            <option value="casual">Casual</option>
            <option value="formal">Formal</option>
        </select>
    </div>
    
    <div class="form-group">
        <label for="noteContext">Context / Purpose</label>
        <textarea id="noteContext" rows="3" placeholder="e.g., Reaching out about a potential partnership opportunity..."></textarea>
    </div>
    
    <div class="form-group control-group">
        <input type="checkbox" id="noteBypassCache">
        <label for="noteBypassCache">Bypass cache</label>
    </div>
    
    <button class="btn-primary" id="generateNoteBtn" data-profile-id="${profileId}">
        <span class="btn-text"><i class="fa-solid fa-sparkles"></i> Generate Note</span>
        <span class="btn-loader hidden"></span>
    </button>
    
    <div id="noteResult" class="markdown-content" style="margin-top: 16px;"></div>
</div>
        `;
    },

    setupNoteForm(profileId, outputPanel) {
        const btn = document.getElementById('generateNoteBtn');
        if (!btn) return;

        btn.addEventListener('click', async () => {
            const length = document.getElementById('noteLength').value;
            const tone = document.getElementById('noteTone').value;
            const context = document.getElementById('noteContext').value;
            const bypass = document.getElementById('noteBypassCache').checked;

            const btnText = btn.querySelector('.btn-text');
            const loader = btn.querySelector('.btn-loader');

            btn.disabled = true;
            btnText.classList.add('hidden');
            loader.classList.remove('hidden');

            try {
                const API_BASE = 'http://localhost:8000/api';
                const response = await fetch(`${API_BASE}/generate-note`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    credentials: 'include',
                    body: JSON.stringify({
                        profile_text: outputPanel.tabs.get('profile').content.replace(/<[^>]*>/g, ''),
                        length,
                        tone,
                        context,
                        profile_id: profileId,
                        model_provider: document.getElementById('modelProvider')?.value || 'gemini',
                        bypass_cache: bypass
                    })
                });

                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(error.detail || 'Failed to generate note');
                }

                const data = await response.json();
                const resultDiv = document.getElementById('noteResult');
                if (resultDiv) {
                    let noteContent = data.note;
                    if (data.from_cache) {
                        noteContent = `<span class="cache-badge"><i class="fa-solid fa-bolt"></i> CACHED</span>\n\n${noteContent}`;
                    }
                    resultDiv.innerHTML = window.marked ? marked.parse(noteContent) : noteContent;
                }

                if (window.showToast) {
                    window.showToast('Note generated!', 'success');
                }

            } catch (error) {
                if (window.showToast) {
                    window.showToast(error.message, 'error');
                }
            } finally {
                btn.disabled = false;
                btnText.classList.remove('hidden');
                loader.classList.add('hidden');
            }
        });
    },

    getDeepResearchFormHTML() {
        return `
<div class="deep-research-form">
    <h4><i class="fa-solid fa-microscope"></i> Deep Research</h4>
    <p style="color: var(--text-secondary); margin-bottom: 16px;">
        Perform in-depth research on a specific topic related to this person.
    </p>
    
    <div class="form-group">
        <label for="deepTopic">Research Topic</label>
        <textarea id="deepTopic" rows="3" placeholder="e.g., Their leadership style and key business decisions at Microsoft..."></textarea>
    </div>
    
    <div class="form-group">
        <label for="deepMode">Search Mode</label>
        <div class="form-radio-group" id="deepMode">
            <label class="radio-option">
                <input type="radio" name="deepMode" value="rag" checked>
                <span class="radio-label">RAG</span>
            </label>
            <label class="radio-option">
                <input type="radio" name="deepMode" value="tools">
                <span class="radio-label">Tools</span>
            </label>
            <label class="radio-option">
                <input type="radio" name="deepMode" value="hybrid">
                <span class="radio-label">Hybrid</span>
            </label>
        </div>
    </div>
    
    <button class="btn-primary" id="runDeepResearchBtn">
        <span class="btn-text"><i class="fa-solid fa-rocket"></i> Run Deep Research</span>
        <span class="btn-loader hidden"></span>
    </button>
    
    <div id="deepResult" class="markdown-content" style="margin-top: 16px;"></div>
</div>
        `;
    },

    setupDeepResearchForm(outputPanel) {
        const btn = document.getElementById('runDeepResearchBtn');
        if (!btn) return;

        btn.addEventListener('click', async () => {
            const topic = document.getElementById('deepTopic').value;
            if (!topic.trim()) {
                if (window.showToast) window.showToast('Please enter a research topic', 'warning');
                return;
            }

            const mode = document.querySelector('input[name="deepMode"]:checked')?.value || 'rag';

            const btnText = btn.querySelector('.btn-text');
            const loader = btn.querySelector('.btn-loader');

            btn.disabled = true;
            btnText.classList.add('hidden');
            loader.classList.remove('hidden');

            try {
                const API_BASE = 'http://localhost:8000/api';
                const response = await fetch(`${API_BASE}/deep-research`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    credentials: 'include',
                    body: JSON.stringify({
                        topic,
                        search_mode: mode,
                        model_provider: document.getElementById('modelProvider')?.value || 'gemini',
                        search_provider: document.getElementById('searchProvider')?.value || 'ddg'
                    })
                });

                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(error.detail || 'Failed to run deep research');
                }

                const data = await response.json();
                const resultDiv = document.getElementById('deepResult');
                if (resultDiv) {
                    resultDiv.innerHTML = window.marked ? marked.parse(data.report) : data.report;
                }

                if (window.showToast) {
                    window.showToast('Deep research complete!', 'success');
                }

            } catch (error) {
                if (window.showToast) {
                    window.showToast(error.message, 'error');
                }
            } finally {
                btn.disabled = false;
                btnText.classList.remove('hidden');
                loader.classList.add('hidden');
            }
        });
    }
};

// Register the module
window.ModuleRegistry.register(PersonResearchModule);
