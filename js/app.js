// Main application logic for Daily Research Tracker
class ResearchTrackerApp {
    constructor() {
        this.currentData = [];
        this.filteredData = [];
        this.currentDate = '';
        this.filters = {
            search: '',
            source: '',
            minScore: 0,
            recommendedOnly: false
        };
        
        this.initializeElements();
        this.bindEvents();
        this.loadLatestData();
    }
    
    initializeElements() {
        // Core UI elements
        this.dateSelect = document.getElementById('date-select');
        this.searchBox = document.getElementById('search-box');
        this.sourceFilter = document.getElementById('source-filter');
        this.scoreFilter = document.getElementById('score-filter');
        this.recommendedToggle = document.getElementById('recommended-toggle');
        this.papersContainer = document.getElementById('papers-container');
        this.loadingElement = document.getElementById('loading');
        this.noResultsElement = document.getElementById('no-results');
        
        // Stats elements
        this.paperCountElement = document.getElementById('paper-count');
        this.recommendedCountElement = document.getElementById('recommended-count');
        this.avgScoreElement = document.getElementById('avg-score');
        this.updateTimeElement = document.getElementById('update-time');
        
        // Modal elements
        this.modal = document.getElementById('paper-modal');
        this.modalContent = document.getElementById('modal-content');
        this.closeModal = document.querySelector('.close');
    }
    
    bindEvents() {
        // Date selection
        this.dateSelect.addEventListener('change', (e) => {
            if (e.target.value) {
                this.loadDateData(e.target.value);
            }
        });
        
        // Search input with debounce
        let searchTimeout;
        this.searchBox.addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                this.filters.search = e.target.value.toLowerCase();
                this.applyFilters();
            }, 300);
        });
        
        // Source filter
        this.sourceFilter.addEventListener('change', (e) => {
            this.filters.source = e.target.value;
            this.applyFilters();
        });
        
        // Score filter
        this.scoreFilter.addEventListener('change', (e) => {
            this.filters.minScore = parseInt(e.target.value) || 0;
            this.applyFilters();
        });
        
        // Recommended toggle
        this.recommendedToggle.addEventListener('click', () => {
            this.recommendedToggle.classList.toggle('active');
            this.filters.recommendedOnly = this.recommendedToggle.classList.contains('active');
            this.applyFilters();
        });
        
        // Modal close
        this.closeModal.addEventListener('click', () => {
            this.modal.style.display = 'none';
        });
        
        // Close modal when clicking outside
        window.addEventListener('click', (e) => {
            if (e.target === this.modal) {
                this.modal.style.display = 'none';
            }
        });
    }
    
    async loadLatestData() {
        try {
            this.showLoading();
            const index = await window.dataLoader.loadDateIndex();
            await this.populateDateSelect(index.dates);
            
            if (index.latest) {
                this.currentDate = index.latest;
                this.dateSelect.value = index.latest;
                await this.loadDateData(index.latest);
            }
        } catch (error) {
            console.error('Error loading latest data:', error);
            this.showError('Failed to load data. Please try again later.');
        }
    }
    
    async loadDateData(date) {
        try {
            this.showLoading();
            this.currentDate = date;
            this.currentData = await window.dataLoader.loadDateData(date);
            
            // Update filters
            this.updateSourceFilter();
            
            // Apply current filters
            this.applyFilters();
            
            // Update timestamp
            this.updateTimeElement.textContent = new Date().toLocaleString();
            
            this.hideLoading();
        } catch (error) {
            console.error(`Error loading data for ${date}:`, error);
            this.showError(`Failed to load data for ${date}`);
        }
    }
    
    async populateDateSelect(dates) {
        this.dateSelect.innerHTML = '';
        
        // Add default option
        const defaultOption = document.createElement('option');
        defaultOption.value = '';
        defaultOption.textContent = 'Select date...';
        this.dateSelect.appendChild(defaultOption);
        
        // Add date options
        dates.forEach(date => {
            const option = document.createElement('option');
            option.value = date;
            
            // Format date for display
            const dateObj = new Date(date);
            const today = new Date();
            const yesterday = new Date(today);
            yesterday.setDate(yesterday.getDate() - 1);
            
            let displayText = date;
            if (date === today.toISOString().split('T')[0]) {
                displayText = `${date} (Today)`;
            } else if (date === yesterday.toISOString().split('T')[0]) {
                displayText = `${date} (Yesterday)`;
            }
            
            option.textContent = displayText;
            this.dateSelect.appendChild(option);
        });
    }
    
    updateSourceFilter() {
        // Collect unique sources
        const sources = new Set();
        this.currentData.forEach(paper => {
            if (paper.source) {
                sources.add(paper.source);
            }
        });
        
        // Update source filter options
        this.sourceFilter.innerHTML = '<option value="">All Sources</option>';
        Array.from(sources).sort().forEach(source => {
            const option = document.createElement('option');
            option.value = source;
            option.textContent = source;
            this.sourceFilter.appendChild(option);
        });
        
        // Reset source filter
        this.sourceFilter.value = '';
        this.filters.source = '';
    }
    
    applyFilters() {
        this.filteredData = this.currentData.filter(paper => {
            // Search filter
            if (this.filters.search) {
                const searchStr = `${paper.title} ${paper.summary} ${paper.authors.join(' ')}`.toLowerCase();
                if (!searchStr.includes(this.filters.search)) {
                    return false;
                }
            }
            
            // Source filter
            if (this.filters.source && paper.source !== this.filters.source) {
                return false;
            }
            
            // Score filter
            if (this.filters.minScore > 0 && paper.score < this.filters.minScore) {
                return false;
            }
            
            // Recommended filter
            if (this.filters.recommendedOnly && !paper.recommendation) {
                return false;
            }
            
            return true;
        });
        
        this.updateStats();
        this.renderPapers();
    }
    
    updateStats() {
        const totalPapers = this.filteredData.length;
        const recommendedPapers = this.filteredData.filter(p => p.recommendation).length;
        const avgScore = this.filteredData.length > 0 
            ? (this.filteredData.reduce((sum, p) => sum + p.score, 0) / this.filteredData.length).toFixed(2)
            : '0.00';
        
        this.paperCountElement.textContent = totalPapers;
        this.recommendedCountElement.textContent = recommendedPapers;
        this.avgScoreElement.textContent = avgScore;
        
        // Show/hide no results message
        if (totalPapers === 0 && this.currentData.length > 0) {
            this.noResultsElement.style.display = 'block';
            this.papersContainer.style.display = 'none';
        } else {
            this.noResultsElement.style.display = 'none';
            this.papersContainer.style.display = 'grid';
        }
    }
    
    renderPapers() {
        this.papersContainer.innerHTML = '';
        
        this.filteredData.forEach(paper => {
            const paperCard = this.createPaperCard(paper);
            this.papersContainer.appendChild(paperCard);
        });
    }
    
    createPaperCard(paper) {
        const card = document.createElement('div');
        card.className = `paper-card ${paper.recommendation ? 'recommended' : ''}`;
        card.dataset.id = paper.id;
        
        // Header with title and score
        const header = document.createElement('div');
        header.className = 'paper-header';
        
        const title = document.createElement('div');
        title.className = 'paper-title';
        title.textContent = paper.title;
        
        const score = document.createElement('div');
        score.className = 'paper-score';
        score.textContent = paper.score.toFixed(1);
        
        header.appendChild(title);
        header.appendChild(score);
        
        // Meta info
        const meta = document.createElement('div');
        meta.className = 'paper-meta';
        
        const source = document.createElement('span');
        source.textContent = paper.source;
        
        const category = document.createElement('span');
        category.textContent = paper.category || 'General';
        
        const date = document.createElement('span');
        date.textContent = paper.published ? paper.published.split('T')[0] : 'Unknown date';
        
        meta.appendChild(source);
        meta.appendChild(category);
        meta.appendChild(date);
        
        // Summary
        const summary = document.createElement('div');
        summary.className = 'paper-summary';
        summary.textContent = paper.summary;
        
        // Actions
        const actions = document.createElement('div');
        actions.className = 'paper-actions';
        
        const viewBtn = document.createElement('a');
        viewBtn.className = 'btn btn-primary';
        viewBtn.href = paper.link;
        viewBtn.target = '_blank';
        viewBtn.innerHTML = '<i class="fas fa-external-link-alt"></i> View Paper';
        
        const detailsBtn = document.createElement('button');
        detailsBtn.className = 'btn btn-secondary';
        detailsBtn.innerHTML = '<i class="fas fa-info-circle"></i> Details';
        detailsBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            this.showPaperDetails(paper);
        });
        
        actions.appendChild(viewBtn);
        
        // Add PDF button for arXiv papers
        if (paper.pdf_link) {
            const pdfBtn = document.createElement('a');
            pdfBtn.className = 'btn btn-secondary';
            pdfBtn.href = paper.pdf_link;
            pdfBtn.target = '_blank';
            pdfBtn.innerHTML = '<i class="fas fa-file-pdf"></i> PDF';
            actions.appendChild(pdfBtn);
        }
        
        actions.appendChild(detailsBtn);
        
        // Assemble card
        card.appendChild(header);
        card.appendChild(meta);
        card.appendChild(summary);
        card.appendChild(actions);
        
        // Click to show details
        card.addEventListener('click', (e) => {
            if (!e.target.closest('.btn')) {
                this.showPaperDetails(paper);
            }
        });
        
        return card;
    }
    
    showPaperDetails(paper) {
        this.modalContent.innerHTML = '';
        
        // Create modal content
        const content = document.createElement('div');
        content.className = 'paper-details';
        
        // Title
        const title = document.createElement('h2');
        title.textContent = paper.title;
        
        // Score and recommendation badge
        const badge = document.createElement('div');
        badge.className = 'paper-badge';
        badge.innerHTML = `
            <span class="score-badge">Score: ${paper.score.toFixed(1)}/10</span>
            ${paper.recommendation ? '<span class="rec-badge">Recommended</span>' : ''}
        `;
        
        // Meta info
        const meta = document.createElement('div');
        meta.className = 'paper-detail-meta';
        meta.innerHTML = `
            <p><strong>Source:</strong> ${paper.source}</p>
            <p><strong>Category:</strong> ${paper.category || 'General'}</p>
            <p><strong>Published:</strong> ${paper.published || 'Unknown'}</p>
            ${paper.authors && paper.authors.length > 0 ? 
                `<p><strong>Authors:</strong> ${paper.authors.join(', ')}</p>` : ''}
        `;
        
        // Summary
        const summary = document.createElement('div');
        summary.className = 'paper-detail-summary';
        summary.innerHTML = `<h3>Summary</h3><p>${paper.summary}</p>`;
        
        // Links
        const links = document.createElement('div');
        links.className = 'paper-detail-links';
        links.innerHTML = `
            <a href="${paper.link}" target="_blank" class="btn btn-primary">
                <i class="fas fa-external-link-alt"></i> View Paper
            </a>
            ${paper.pdf_link ? 
                `<a href="${paper.pdf_link}" target="_blank" class="btn btn-secondary">
                    <i class="fas fa-file-pdf"></i> Download PDF
                </a>` : ''}
        `;
        
        // Assemble modal content
        content.appendChild(title);
        content.appendChild(badge);
        content.appendChild(meta);
        content.appendChild(summary);
        content.appendChild(links);
        
        this.modalContent.appendChild(content);
        this.modal.style.display = 'block';
    }
    
    showLoading() {
        this.loadingElement.style.display = 'block';
        this.papersContainer.style.display = 'none';
        this.noResultsElement.style.display = 'none';
    }
    
    hideLoading() {
        this.loadingElement.style.display = 'none';
        this.papersContainer.style.display = 'grid';
    }
    
    showError(message) {
        this.loadingElement.innerHTML = `<i class="fas fa-exclamation-triangle"></i> ${message}`;
        this.loadingElement.style.display = 'block';
        this.papersContainer.style.display = 'none';
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new ResearchTrackerApp();
});