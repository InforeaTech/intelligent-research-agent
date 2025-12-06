/**
 * Module Registry
 * Manages registration and retrieval of research modules.
 */
const ModuleRegistry = {
    modules: new Map(),

    /**
     * Register a new module.
     * @param {Object} config - Module configuration
     */
    register(config) {
        if (!config.id || !config.name) {
            console.error('Module registration failed: Missing id or name');
            return;
        }
        this.modules.set(config.id, config);
        console.log(`Module registered: ${config.name}`);
    },

    /**
     * Get a module by ID.
     * @param {string} id 
     */
    get(id) {
        return this.modules.get(id);
    },

    /**
     * Get all registered modules.
     * @returns {Array} List of modules
     */
    getAll() {
        return Array.from(this.modules.values());
    }
};

window.ModuleRegistry = ModuleRegistry;
