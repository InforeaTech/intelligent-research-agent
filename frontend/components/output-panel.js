/**
 * Output Panel Component
 * Displays tabbed output with copy and download functionality
 */

class OutputPanel {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.tabs = new Map();
        this.activeTabId = null;
    }

    clear() {
        if (!this.container) return;
        this.container.innerHTML = `
            <div class="output-tabs-wrapper">
                <div class="output-tabs"></div>
                <div class="output-actions">
                    <button class="btn-icon" id="copyOutputBtn" title="Copy to clipboard">
                        <i class="fa-regular fa-copy"></i>
                    </button>
                    <button class="btn-icon" id="downloadPdfBtn" title="Download as PDF">
                        <i class="fa-solid fa-file-pdf"></i>
                    </button>
                </div>
            </div>
            <div class="output-content-area"></div>
        `;
        this.tabs.clear();
        this.activeTabId = null;

        // Setup action buttons
        this.setupActionButtons();
    }

    setupActionButtons() {
        const copyBtn = this.container.querySelector('#copyOutputBtn');
        const pdfBtn = this.container.querySelector('#downloadPdfBtn');

        if (copyBtn) {
            copyBtn.addEventListener('click', () => this.copyToClipboard());
        }

        if (pdfBtn) {
            pdfBtn.addEventListener('click', () => this.downloadAsPdf());
        }
    }

    addTab(id, label, icon) {
        this.tabs.set(id, { label, icon, content: '', rawContent: '', setupCallback: null });
        // Set first added tab as active by default if none active
        if (!this.activeTabId) {
            this.activeTabId = id;
        }
        this.renderTabs();
    }

    setContent(id, content, setupCallback = null) {
        if (this.tabs.has(id)) {
            const tab = this.tabs.get(id);
            tab.rawContent = content; // Store raw markdown
            tab.content = content;
            if (setupCallback) {
                tab.setupCallback = setupCallback;
            }
            if (this.activeTabId === id) {
                this.renderContent(id);
                // Run setup callback after render if provided
                if (tab.setupCallback) {
                    setTimeout(() => tab.setupCallback(), 50);
                }
            }
        }
    }

    activateTab(id) {
        if (this.tabs.has(id)) {
            this.activeTabId = id;
            this.renderTabs();
            this.renderContent(id);
            // Re-run setup callback when tab is activated
            const tab = this.tabs.get(id);
            if (tab.setupCallback) {
                setTimeout(() => tab.setupCallback(), 50);
            }
        }
    }

    renderTabs() {
        const tabsContainer = this.container.querySelector('.output-tabs');
        if (!tabsContainer) return;

        tabsContainer.innerHTML = Array.from(this.tabs.entries()).map(([id, tab]) => `
            <button class="tab-btn ${this.activeTabId === id ? 'active' : ''}" 
                    onclick="window.outputPanel.activateTab('${id}')">
                <i class="${tab.icon}"></i> ${tab.label}
            </button>
        `).join('');
    }

    renderContent(id) {
        const contentContainer = this.container.querySelector('.output-content-area');
        if (!contentContainer) return;

        const tab = this.tabs.get(id);
        if (!tab || !tab.content) {
            contentContainer.innerHTML = `
                <div class="empty-state">
                    <i class="fa-regular fa-file-lines"></i>
                    <p>No content generated yet</p>
                    <small>Run a research to see results here</small>
                </div>
            `;
            return;
        }

        // Check if content is already HTML (contains form elements)
        // In this case, don't parse as markdown
        const isHtmlForm = /<(select|input|button|form|textarea)\b/i.test(tab.content);

        let htmlContent = tab.content;
        if (window.marked && !isHtmlForm) {
            // Configure marked for better rendering
            marked.setOptions({
                breaks: true,
                gfm: true
            });
            htmlContent = marked.parse(tab.content);
        }

        contentContainer.innerHTML = `
            <div class="markdown-content">
                ${htmlContent}
            </div>
        `;
    }

    copyToClipboard() {
        const tab = this.tabs.get(this.activeTabId);
        if (!tab || !tab.rawContent) {
            if (window.showToast) showToast('No content to copy', 'warning');
            return;
        }

        // Strip HTML tags to get plain text
        const plainText = tab.rawContent.replace(/<[^>]*>/g, '');

        navigator.clipboard.writeText(plainText).then(() => {
            if (window.showToast) showToast('Copied to clipboard!', 'success');
        }).catch(err => {
            console.error('Copy failed:', err);
            if (window.showToast) showToast('Failed to copy', 'error');
        });
    }

    downloadAsPdf() {
        const tab = this.tabs.get(this.activeTabId);
        if (!tab || !tab.content) {
            if (window.showToast) showToast('No content to download', 'warning');
            return;
        }

        // Create a printable window
        const printWindow = window.open('', '_blank');
        if (!printWindow) {
            if (window.showToast) showToast('Please allow popups to download PDF', 'warning');
            return;
        }

        // Parse content
        let htmlContent = tab.content;
        if (window.marked) {
            htmlContent = marked.parse(tab.content);
        }

        // Get current date for filename
        const date = new Date().toISOString().split('T')[0];
        const title = `Research Report - ${date}`;

        printWindow.document.write(`
            <!DOCTYPE html>
            <html>
            <head>
                <title>${title}</title>
                <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
                <style>
                    * {
                        margin: 0;
                        padding: 0;
                        box-sizing: border-box;
                    }
                    body {
                        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                        font-size: 11pt;
                        line-height: 1.6;
                        color: #1a1a1a;
                        padding: 40px;
                        max-width: 800px;
                        margin: 0 auto;
                    }
                    h1 {
                        font-size: 24pt;
                        font-weight: 700;
                        margin-bottom: 8px;
                        color: #1a1a1a;
                        border-bottom: 2px solid #D97706;
                        padding-bottom: 8px;
                    }
                    h2 {
                        font-size: 16pt;
                        font-weight: 600;
                        margin: 24px 0 12px 0;
                        color: #1a1a1a;
                    }
                    h3 {
                        font-size: 13pt;
                        font-weight: 600;
                        margin: 18px 0 8px 0;
                        color: #333;
                    }
                    p {
                        margin-bottom: 12px;
                    }
                    ul, ol {
                        margin: 12px 0;
                        padding-left: 24px;
                    }
                    li {
                        margin-bottom: 6px;
                    }
                    strong {
                        font-weight: 600;
                    }
                    code {
                        background: #f5f5f5;
                        padding: 2px 6px;
                        border-radius: 4px;
                        font-size: 10pt;
                    }
                    pre {
                        background: #f5f5f5;
                        padding: 16px;
                        border-radius: 8px;
                        overflow-x: auto;
                        margin: 12px 0;
                    }
                    blockquote {
                        border-left: 3px solid #D97706;
                        padding-left: 16px;
                        margin: 12px 0;
                        color: #555;
                        font-style: italic;
                    }
                    a {
                        color: #D97706;
                    }
                    .header {
                        margin-bottom: 32px;
                        padding-bottom: 16px;
                        border-bottom: 1px solid #eee;
                    }
                    .header p {
                        color: #666;
                        font-size: 10pt;
                    }
                    .footer {
                        margin-top: 40px;
                        padding-top: 16px;
                        border-top: 1px solid #eee;
                        font-size: 9pt;
                        color: #888;
                        text-align: center;
                    }
                    @media print {
                        body {
                            padding: 20px;
                        }
                        .no-print {
                            display: none;
                        }
                    }
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>Research Report</h1>
                    <p>Generated on ${new Date().toLocaleDateString('en-US', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        })}</p>
                </div>
                <div class="content">
                    ${htmlContent}
                </div>
                <div class="footer">
                    Generated by Research Agent
                </div>
                <script>
                    window.onload = function() {
                        window.print();
                        setTimeout(function() {
                            window.close();
                        }, 500);
                    }
                </script>
            </body>
            </html>
        `);
        printWindow.document.close();

        if (window.showToast) showToast('Opening print dialog...', 'info');
    }

    getCurrentContent() {
        const tab = this.tabs.get(this.activeTabId);
        return tab ? tab.rawContent : '';
    }
}

// Global reference for tab switching
window.OutputPanel = OutputPanel;
window.outputPanel = null;

// Initialize global reference when panel is created
const originalInit = window.app?.init;
if (window.app) {
    const origInit = window.app.init;
    window.app.init = async function () {
        await origInit.call(this);
        // Store reference to output panel
        if (window.state?.outputPanel) {
            window.outputPanel = window.state.outputPanel;
        }
    };
}
