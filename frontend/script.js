// API Base URL - Automatically use same origin when served from API
const API_BASE_URL = window.location.origin === 'file://' 
    ? 'http://localhost:8000'  // Local file (development)
    : window.location.origin;  // Same origin (when served from FastAPI)

let companies = [];
let currentResearchId = null;
let statusPollInterval = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadCompanies();
    loadAlgorithm();
    loadCompaniesForSelect();
});

// Tab Navigation
function showTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab
    document.getElementById(`${tabName}-tab`).classList.add('active');
    event.target.classList.add('active');
}

// Load Companies
async function loadCompanies() {
    const topN = document.getElementById('top-n-select').value;
    const url = topN ? `${API_BASE_URL}/companies?top_n=${topN}` : `${API_BASE_URL}/companies`;
    
    document.getElementById('companies-loading').style.display = 'block';
    document.getElementById('companies-table-container').innerHTML = '';
    
    try {
        const response = await fetch(url);
        const data = await response.json();
        companies = data;
        displayCompanies(data);
    } catch (error) {
        document.getElementById('companies-table-container').innerHTML = 
            `<div class="error">Error loading companies: ${error.message}</div>`;
    } finally {
        document.getElementById('companies-loading').style.display = 'none';
    }
}

function displayCompanies(data) {
    const container = document.getElementById('companies-table-container');
    
    if (data.length === 0) {
        container.innerHTML = '<div class="loading">No companies found</div>';
        return;
    }
    
    let html = `
        <table>
            <thead>
                <tr>
                    <th>Rank</th>
                    <th>Company Name</th>
                    <th>Market Cap (Cr)</th>
                    <th>P/E Ratio</th>
                    <th>ROCE %</th>
                    <th>Investment Score</th>
                    <th>Action</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    data.forEach(company => {
        const rankClass = company.rank === 1 ? 'rank-1' : 
                         company.rank === 2 ? 'rank-2' : 
                         company.rank === 3 ? 'rank-3' : 'rank-other';
        
        html += `
            <tr>
                <td data-label="Rank"><span class="rank-badge ${rankClass}">${company.rank}</span></td>
                <td data-label="Company Name"><strong>${company.name}</strong></td>
                <td data-label="Market Cap (Cr)">${company.market_cap}</td>
                <td data-label="P/E Ratio">${company.pe_ratio}</td>
                <td data-label="ROCE %">${company.roce}</td>
                <td data-label="Investment Score">${parseFloat(company.investment_score).toFixed(4)}</td>
                <td data-label="Action"><button onclick="selectCompanyForResearch('${company.name}', ${company.rank})" class="btn-primary">Select</button></td>
            </tr>
        `;
    });
    
    html += `</tbody></table>`;
    container.innerHTML = html;
}

// Load Algorithm
async function loadAlgorithm() {
    try {
        const response = await fetch(`${API_BASE_URL}/scoring-algorithm`);
        const data = await response.json();
        displayAlgorithm(data);
    } catch (error) {
        document.getElementById('algorithm-content').innerHTML = 
            `<div class="error">Error loading algorithm: ${error.message}</div>`;
    }
}

function displayAlgorithm(data) {
    let html = `
        <div class="algorithm-section">
            <h3>Algorithm Description</h3>
            <p>${data.description}</p>
        </div>
        
        <div class="algorithm-section">
            <h3>Weight Distribution</h3>
            <div class="weights-grid">
    `;
    
    Object.entries(data.weights).forEach(([key, value]) => {
        const metric = data.metrics[key] || key;
        html += `
            <div class="weight-card">
                <h4>${key.replace(/_/g, ' ').toUpperCase()}</h4>
                <div class="weight">${(value * 100).toFixed(0)}%</div>
                <div class="description">${metric}</div>
            </div>
        `;
    });
    
    html += `</div></div>`;
    
    html += `
        <div class="algorithm-section">
            <h3>Processing Steps</h3>
            <ul class="process-list">
    `;
    
    data.process.forEach(step => {
        html += `<li>${step}</li>`;
    });
    
    html += `</ul></div>`;
    
    document.getElementById('algorithm-content').innerHTML = html;
}

// Load Companies for Select
async function loadCompaniesForSelect() {
    try {
        const response = await fetch(`${API_BASE_URL}/companies?top_n=100`);
        const data = await response.json();
        
        const select = document.getElementById('company-select');
        data.forEach(company => {
            const option = document.createElement('option');
            option.value = company.name;
            option.textContent = `${company.rank}. ${company.name}`;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading companies for select:', error);
    }
}

function updateCompanyName() {
    const select = document.getElementById('company-select');
    const input = document.getElementById('company-name-input');
    input.value = select.value;
}

function updateCompanySelect() {
    const select = document.getElementById('company-select');
    const input = document.getElementById('company-name-input');
    select.value = input.value;
}

function selectCompanyForResearch(companyName, rank) {
    showTab('research');
    document.getElementById('company-select').value = companyName;
    document.getElementById('company-name-input').value = companyName;
}

// Start Research
async function startResearch() {
    const companyName = document.getElementById('company-name-input').value.trim();
    const companySelect = document.getElementById('company-select').value;
    
    if (!companyName && !companySelect) {
        alert('Please select or enter a company name');
        return;
    }
    
    const selectedCompany = companyName || companySelect;
    
    // Find rank if company is in the list
    const company = companies.find(c => c.name === selectedCompany);
    const companyRank = company ? company.rank : null;
    
    try {
        document.getElementById('start-research-btn').disabled = true;
        document.getElementById('start-research-btn').textContent = 'Starting...';
        
        const response = await fetch(`${API_BASE_URL}/research/start`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                company_name: selectedCompany,
                company_rank: companyRank
            })
        });
        
        const data = await response.json();
        currentResearchId = data.research_id;
        
        // Show status container
        document.getElementById('research-status-container').style.display = 'block';
        document.getElementById('research-id-display').textContent = `Research ID: ${data.research_id}`;
        
        // Start polling for status
        startStatusPolling(data.research_id);
        
    } catch (error) {
        alert(`Error starting research: ${error.message}`);
    } finally {
        document.getElementById('start-research-btn').disabled = false;
        document.getElementById('start-research-btn').textContent = '🚀 Start Research';
    }
}

// Poll for Status
function startStatusPolling(researchId) {
    if (statusPollInterval) {
        clearInterval(statusPollInterval);
    }
    
    statusPollInterval = setInterval(async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/research/status/${researchId}`);
            const status = await response.json();
            
            updateStatusDisplay(status);
            
            if (status.status === 'completed' || status.status === 'error') {
                clearInterval(statusPollInterval);
                
                if (status.status === 'completed') {
                    loadResults(researchId);
                }
            }
        } catch (error) {
            console.error('Error polling status:', error);
        }
    }, 2000); // Poll every 2 seconds
}

function updateStatusDisplay(status) {
    // Update progress bar
    const progress = (status.progress.current / status.progress.total) * 100;
    document.getElementById('progress-fill').style.width = `${progress}%`;
    document.getElementById('progress-fill').textContent = `${Math.round(progress)}%`;
    
    // Show detailed message if available
    let message = status.progress.message;
    if (status.progress.details) {
        const details = status.progress.details;
        if (details.subtopic) {
            message = `[${details.category?.replace(/_/g, ' ').toUpperCase() || ''}] ${details.message || 'Processing...'}`;
        } else if (details.category) {
            message = details.message || `Processing ${details.category.replace(/_/g, ' ').title()}...`;
        }
    }
    document.getElementById('progress-text').textContent = message;
    
    // Update steps
    const stepsContainer = document.getElementById('steps-container');
    const steps = [
        { id: 'company_selected', name: 'Company Selection', message: 'Company selected and validated' },
        { id: 'research_agent', name: 'Research Agent', message: 'Gathering evidence from web sources' },
        { id: 'report_generation', name: 'Report Generation', message: 'Creating analyst report' },
        { id: 'validation', name: 'Validation', message: 'Validating buy/avoid decision' },
        { id: 'completed', name: 'Completed', message: 'Research completed successfully' }
    ];
    
    // Map step IDs to indices for checking previous steps
    const stepIndexMap = {
        'company_selected': 0,
        'research_agent': 1,
        'report_generation': 2,
        'validation': 3,
        'completed': 4
    };
    
    let html = '';
    steps.forEach((step, index) => {
        let stepStatus = 'pending';
        let stepMessage = step.message;
        const currentStepIndex = stepIndexMap[status.current_step] || -1;
        
        // Mark previous steps as completed when a new step starts
        if (currentStepIndex > index) {
            stepStatus = 'completed';
        } else if (status.current_step === step.id) {
            stepStatus = 'active';
            // Show detailed progress if available
            if (status.progress.details) {
                const details = status.progress.details;
                if (details.subtopic && step.id === 'research_agent') {
                    stepMessage = `Searching: ${details.subtopic} (${details.subtopic_number}/${details.total_subtopics})`;
                    if (details.results_found !== undefined) {
                        stepMessage += ` - Found ${details.results_found} results`;
                    }
                }
            }
        } else if (status.current_step === 'completed' && index < 4) {
            stepStatus = 'completed';
        } else if (status.current_step === 'error') {
            if (index >= status.progress.current - 1) {
                stepStatus = 'error';
                if (status.error) {
                    stepMessage = `Error: ${status.error}`;
                }
            } else if (index < status.progress.current - 1) {
                stepStatus = 'completed';
            }
        }
        
        html += `
            <div class="step-item ${stepStatus}">
                <div class="step-header">
                    <span class="step-title">${step.name}</span>
                    <span class="step-status ${stepStatus}">${stepStatus.charAt(0).toUpperCase() + stepStatus.slice(1)}</span>
                </div>
                <div class="step-message">${stepMessage}</div>
                ${status.progress.details && status.progress.details.error ? `<div class="step-error" style="color: #dc3545; margin-top: 5px; font-size: 0.85em;">⚠️ ${status.progress.details.error}</div>` : ''}
            </div>
        `;
    });
    
    stepsContainer.innerHTML = html;
    
    // Show detailed progress if available
    if (status.progress.details) {
        updateDetailedProgress(status.progress.details);
    }
}

function updateDetailedProgress(details) {
    const container = document.getElementById('detailed-progress');
    const content = document.getElementById('detailed-progress-content');
    
    if (!details || (!details.category && !details.subtopic)) {
        container.style.display = 'none';
        return;
    }
    
    container.style.display = 'block';
    
    let html = '';
    
    if (details.category) {
        const categoryName = details.category.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        html += `<div class="detailed-progress-item ${details.error ? 'error' : 'active'}">`;
        html += `<div class="detailed-progress-category">📁 ${categoryName}`;
        if (details.category_number && details.total_categories) {
            html += ` <span style="color: #667eea;">(${details.category_number}/${details.total_categories})</span>`;
        }
        html += `</div>`;
        
        if (details.subtopic) {
            html += `<div class="detailed-progress-subtopic">`;
            html += `  🔍 ${details.subtopic}`;
            if (details.subtopic_number && details.total_subtopics) {
                html += ` <span style="color: #667eea;">(${details.subtopic_number}/${details.total_subtopics})</span>`;
            }
            html += `</div>`;
            
            if (details.results_found !== undefined) {
                html += `<div class="detailed-progress-stats">✓ Found ${details.results_found} results</div>`;
            }
        }
        
        if (details.error) {
            html += `<div style="color: #dc3545; margin-top: 5px;">⚠️ ${details.error}</div>`;
        }
        
        html += `</div>`;
    }
    
    content.innerHTML = html;
}

// Load Results
async function loadResults(researchId) {
    try {
        const response = await fetch(`${API_BASE_URL}/research/results/${researchId}`);
        const results = await response.json();
        
        displayResults(results);
        document.getElementById('results-container').style.display = 'block';
    } catch (error) {
        console.error('Error loading results:', error);
    }
}

function displayResults(results) {
    const summary = document.getElementById('results-summary');
    summary.innerHTML = `
        <h3>Research Complete!</h3>
        <div class="result-item">
            <strong>Recommendation:</strong> <span style="font-size: 1.2em; font-weight: bold;">${results.recommendation}</span>
        </div>
        <div class="result-item">
            <strong>Confidence:</strong> ${results.confidence}
        </div>
        <div class="result-item">
            <strong>Expected 3-Year Return:</strong> ${results.validation.expected_return_3y || 'N/A'}
        </div>
        <div class="result-item">
            <strong>Probability of 40%+ Return:</strong> ${results.validation.probability_40pct_return || 'N/A'}
        </div>
    `;
    
    // Display report preview
    const preview = document.getElementById('report-preview');
    preview.textContent = results.report.substring(0, 2000) + (results.report.length > 2000 ? '...' : '');
}

// Download Report
async function downloadReport() {
    if (!currentResearchId) return;
    
    try {
        const statusResponse = await fetch(`${API_BASE_URL}/research/status/${currentResearchId}`);
        const status = await statusResponse.json();
        
        const response = await fetch(`${API_BASE_URL}/reports/${encodeURIComponent(status.company_name)}`);
        const blob = await response.blob();
        
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${status.company_name}_Analyst_Report_${new Date().toISOString().split('T')[0]}.md`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    } catch (error) {
        alert(`Error downloading report: ${error.message}`);
    }
}

// View Report
async function viewReport() {
    if (!currentResearchId) return;
    
    try {
        const statusResponse = await fetch(`${API_BASE_URL}/research/status/${currentResearchId}`);
        const status = await statusResponse.json();
        
        const response = await fetch(`${API_BASE_URL}/research/results/${currentResearchId}`);
        const results = await response.json();
        
        const preview = document.getElementById('report-preview');
        
        // Get full report markdown from the report file
        const reportResponse = await fetch(`${API_BASE_URL}/reports/${encodeURIComponent(status.company_name)}`);
        const reportText = await reportResponse.text();
        
        // Convert markdown to HTML using marked.js
        if (typeof marked !== 'undefined') {
            preview.innerHTML = marked.parse(reportText);
        } else {
            // Fallback: display as plain text with basic formatting
            preview.textContent = reportText;
        }
        
        preview.style.display = 'block';
        preview.scrollTop = 0;
    } catch (error) {
        alert(`Error viewing report: ${error.message}`);
    }
}

