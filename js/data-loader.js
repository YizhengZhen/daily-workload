// Data loading utilities for Daily Research Tracker
class DataLoader {
    constructor() {
        this.baseUrl = window.location.origin + window.location.pathname;
        this.dataCache = {};
    }

    async loadDateIndex() {
        try {
            const response = await fetch(`${this.baseUrl}data/index.json`);
            if (!response.ok) throw new Error('Failed to load date index');
            return await response.json();
        } catch (error) {
            console.error('Error loading date index:', error);
            return { dates: [], latest: '' };
        }
    }

    async loadDateData(date) {
        // Check cache first
        if (this.dataCache[date]) {
            return this.dataCache[date];
        }

        try {
            const response = await fetch(`${this.baseUrl}data/${date}.json`);
            if (!response.ok) throw new Error(`Failed to load data for ${date}`);
            const data = await response.json();
            this.dataCache[date] = data;
            return data;
        } catch (error) {
            console.error(`Error loading data for ${date}:`, error);
            return [];
        }
    }

    async loadLatestData() {
        const index = await this.loadDateIndex();
        if (index.latest) {
            return await this.loadDateData(index.latest);
        }
        return [];
    }
}

// Initialize global data loader
window.dataLoader = new DataLoader();