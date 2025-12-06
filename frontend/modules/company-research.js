const CompanyResearchModule = {
    id: 'company-research',
    name: 'Company Analysis',
    icon: 'fa-solid fa-building',
    accentColor: 'var(--color-accent-purple)', // Purple
    description: 'Comprehensive analysis of financial health, competitors, and SWOT.',

    inputFields: [
        { id: 'companyName', label: 'Company Name', type: 'text', placeholder: 'e.g. Tesla, Inc.', required: true },
        { id: 'industry', label: 'Industry', type: 'text', placeholder: 'e.g. Automotive, Tech' },
        {
            id: 'focusAreas',
            label: 'Focus Areas (Select Multiple)',
            type: 'multiselect',
            options: [
                { value: 'Overview', label: 'Company Overview' },
                { value: 'Financials', label: 'Financial Performance' },
                { value: 'Competitors', label: 'Competitive Landscape' },
                { value: 'SWOT', label: 'SWOT Analysis' }
            ]
        },
        { id: 'bypassCache', label: 'Bypass Cache', type: 'checkbox' }
    ],

    outputTabs: [
        { id: 'analysis', label: 'Analysis Report', icon: 'fa-solid fa-chart-pie' }
    ],

    async handleSubmit(formData) {
        const requestBody = {
            company_name: formData.companyName,
            industry: formData.industry,
            focus_areas: formData.focusAreas, // Array
            api_key: formData.apiKey || "mock", // Default if missing/mock
            model_provider: formData.modelProvider,
            search_provider: formData.searchProvider,
            bypass_cache: formData.bypassCache
        };

        const response = await fetch('/api/research/company', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestBody)
        });

        if (!response.ok) throw new Error((await response.json()).detail || 'Analysis failed');
        return await response.json();
    },

    renderResults(data, panel) {
        panel.setContent('analysis', data.analysis);
    }
};

window.ModuleRegistry.register(CompanyResearchModule);
