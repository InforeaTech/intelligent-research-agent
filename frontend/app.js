const API_BASE = 'http://localhost:8000/api';

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
            model_provider: modelProvider
        };

        if (searchProviderSelect.value === 'serper') {
            payload.serper_api_key = serperKey;
        }

        const response = await fetch(`${API_BASE}/research`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || 'Research failed');
        }

        const data = await response.json();
        currentProfileText = data.profile;

        // Render Markdown
        profileContent.innerHTML = marked.parse(data.profile);
        resultsArea.classList.remove('hidden');

        // Auto-generate a default note
        handleGenerateNote();

    } catch (error) {
        alert(`Error: ${error.message}`);
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
            body: JSON.stringify({
                profile_text: currentProfileText,
                length,
                tone,
                context,
                api_key: apiKey,
                model_provider: modelProvider
            })
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || 'Note generation failed');
        }

        const data = await response.json();
        noteResult.value = data.note;
        updateCharCount();

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
