/**
 * Creates a research module selection card with Claude-style design.
 * @param {Object} module - Module configuration object
 * @returns {string} HTML string
 */
function createResearchCard(module) {
    const isComingSoon = module.comingSoon;
    const clickHandler = isComingSoon ? '' : `onclick="window.app.selectModule('${module.id}')"`;

    // Map module IDs to accent colors
    const accentMap = {
        'person-research': 'blue',
        'company-research': 'purple',
        'market-research': 'teal'
    };

    const accent = accentMap[module.id] || 'blue';

    return `
        <div class="research-card ${isComingSoon ? 'coming-soon' : ''}" 
             ${clickHandler}
             data-module-id="${module.id}"
             data-accent="${accent}"
             tabindex="${isComingSoon ? '-1' : '0'}"
             role="button"
             aria-label="${module.name}${isComingSoon ? ' - Coming Soon' : ''}">
            <div class="card-icon-wrapper">
                <i class="${module.icon}"></i>
            </div>
            <div class="card-content">
                <h3>${module.name}</h3>
                <p>${module.description}</p>
                ${isComingSoon ? '<span class="badge-coming-soon">Coming Soon</span>' : ''}
            </div>
        </div>
    `;
}

// Handle keyboard navigation for cards
document.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && e.target.classList.contains('research-card')) {
        e.target.click();
    }
});

window.createResearchCard = createResearchCard;
