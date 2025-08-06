/**
 * BLOCKYHOMEWORK - MODERN JAVASCRIPT APPLICATION
 * Designed with 30+ years of Frontend Development Experience
 * Modern, Responsive, Accessible, and Performance-Optimized
 */

// ===== GLOBAL CONFIGURATION =====
const CONFIG = {
    API_BASE_URL: '/api',
    UPDATE_INTERVAL: 5000,
    ANIMATION_DURATION: 300,
    DEBOUNCE_DELAY: 250,
    MAX_RETRIES: 3,
    RETRY_DELAY: 1000
};

// ===== UTILITY FUNCTIONS =====
class Utils {
    static debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    static throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }

    static formatNumber(num) {
        return new Intl.NumberFormat().format(num);
    }

    static formatCurrency(amount) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD'
        }).format(amount);
    }

    static formatHash(hash, length = 8) {
        if (!hash) return 'N/A';
        return `${hash.substring(0, length)}...${hash.substring(hash.length - length)}`;
    }

    static formatAddress(address, length = 6) {
        if (!address) return 'N/A';
        return `${address.substring(0, length)}...${address.substring(address.length - length)}`;
    }

    static formatTimestamp(timestamp) {
        return new Date(timestamp * 1000).toLocaleString();
    }

    static animateElement(element, animation, duration = CONFIG.ANIMATION_DURATION) {
        element.style.animation = `${animation} ${duration}ms ease-out`;
        setTimeout(() => {
            element.style.animation = '';
        }, duration);
    }

    static showNotification(message, type = 'info', duration = 5000) {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type} fade-in`;
        notification.innerHTML = `
            <div class="notification-content">
                <span class="notification-message">${message}</span>
                <button class="notification-close" onclick="this.parentElement.parentElement.remove()">×</button>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.classList.add('fade-out');
            setTimeout(() => notification.remove(), 300);
        }, duration);
    }

    static createLoadingSpinner(container) {
        const spinner = document.createElement('div');
        spinner.className = 'loading-spinner';
        spinner.innerHTML = `
            <div class="spinner-ring"></div>
            <div class="spinner-text">Loading...</div>
        `;
        container.appendChild(spinner);
        return spinner;
    }

    static removeLoadingSpinner(spinner) {
        if (spinner && spinner.parentNode) {
            spinner.remove();
        }
    }
}

// ===== API SERVICE =====
class ApiService {
    constructor() {
        this.baseURL = CONFIG.API_BASE_URL;
        this.retryCount = 0;
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            this.retryCount = 0;
            return data;
        } catch (error) {
            console.error(`API Error (${endpoint}):`, error);
            
            if (this.retryCount < CONFIG.MAX_RETRIES) {
                this.retryCount++;
                await new Promise(resolve => setTimeout(resolve, CONFIG.RETRY_DELAY * this.retryCount));
                return this.request(endpoint, options);
            }
            
            throw error;
        }
    }

    // Blockchain API methods
    async getChain() {
        return this.request('/chain');
    }

    async getTransactions() {
        return this.request('/transactions');
    }

    async createTransaction(transactionData) {
        return this.request('/transactions/new', {
            method: 'POST',
            body: JSON.stringify(transactionData)
        });
    }

    async mineBlock() {
        return this.request('/mine', {
            method: 'POST'
        });
    }

    async getWalletBalance(address) {
        return this.request(`/wallet/balance/${address}`);
    }

    async getNetworkStatus() {
        return this.request('/network/status');
    }

    async getMiningStatus() {
        return this.request('/mining/status');
    }
}

// ===== STATE MANAGEMENT =====
class AppState {
    constructor() {
        this.state = {
            blockchain: {
                chain: [],
                length: 0,
                difficulty: 0,
                lastBlock: null
            },
            wallet: {
                address: null,
                balance: 0,
                transactions: []
            },
            network: {
                nodes: [],
                connected: 0,
                status: 'disconnected'
            },
            mining: {
                isActive: false,
                currentBlock: null,
                progress: 0
            },
            transactions: {
                pending: [],
                confirmed: []
            }
        };
        this.listeners = new Map();
    }

    subscribe(key, callback) {
        if (!this.listeners.has(key)) {
            this.listeners.set(key, new Set());
        }
        this.listeners.get(key).add(callback);
        
        return () => {
            this.listeners.get(key).delete(callback);
        };
    }

    notify(key, data) {
        if (this.listeners.has(key)) {
            this.listeners.get(key).forEach(callback => {
                try {
                    callback(data);
                } catch (error) {
                    console.error('State listener error:', error);
                }
            });
        }
    }

    update(key, data) {
        this.state[key] = { ...this.state[key], ...data };
        this.notify(key, this.state[key]);
    }

    get(key) {
        return this.state[key];
    }
}

// ===== UI COMPONENTS =====
class UIComponents {
    static createCard(title, content, className = '') {
        return `
            <div class="card ${className} fade-in">
                <div class="card-header">
                    <h3 class="card-title">${title}</h3>
                </div>
                <div class="card-content">
                    ${content}
                </div>
            </div>
        `;
    }

    static createStatCard(number, label, icon = '', trend = null) {
        const trendClass = trend > 0 ? 'trend-up' : trend < 0 ? 'trend-down' : '';
        const trendIcon = trend > 0 ? '↗' : trend < 0 ? '↘' : '';
        
        return `
            <div class="stat-card scale-in">
                ${icon ? `<div class="stat-icon">${icon}</div>` : ''}
                <div class="stat-number ${trendClass}">
                    ${Utils.formatNumber(number)}
                    ${trendIcon ? `<span class="trend-icon">${trendIcon}</span>` : ''}
                </div>
                <div class="stat-label">${label}</div>
            </div>
        `;
    }

    static createButton(text, onClick, className = 'btn-primary', disabled = false) {
        return `
            <button class="btn ${className}" onclick="${onClick}" ${disabled ? 'disabled' : ''}>
                ${text}
            </button>
        `;
    }

    static createProgressBar(progress, label = '') {
        return `
            <div class="progress-container">
                ${label ? `<div class="progress-label">${label}</div>` : ''}
                <div class="progress">
                    <div class="progress-bar" style="width: ${progress}%"></div>
                </div>
                <div class="progress-text">${progress}%</div>
            </div>
        `;
    }

    static createTable(headers, data, className = '') {
        const headerRow = headers.map(header => `<th>${header}</th>`).join('');
        const dataRows = data.map(row => 
            `<tr>${row.map(cell => `<td>${cell}</td>`).join('')}</tr>`
        ).join('');

        return `
            <div class="table-container">
                <table class="table ${className}">
                    <thead>
                        <tr>${headerRow}</tr>
                    </thead>
                    <tbody>
                        ${dataRows}
                    </tbody>
                </table>
            </div>
        `;
    }
}

// ===== DASHBOARD MANAGER =====
class DashboardManager {
    constructor(apiService, appState) {
        this.api = apiService;
        this.state = appState;
        this.updateInterval = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.startAutoUpdate();
        this.loadInitialData();
    }

    setupEventListeners() {
        // Navigation active state
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
                e.target.classList.add('active');
            });
        });

        // Navbar scroll effect
        window.addEventListener('scroll', Utils.throttle(() => {
            const navbar = document.querySelector('.navbar');
            if (window.scrollY > 50) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        }, 100));
    }

    async loadInitialData() {
        try {
            await Promise.all([
                this.updateBlockchainStats(),
                this.updateWalletInfo(),
                this.updateNetworkStatus(),
                this.updateMiningStatus()
            ]);
        } catch (error) {
            console.error('Failed to load initial data:', error);
            Utils.showNotification('Failed to load dashboard data', 'error');
        }
    }

    startAutoUpdate() {
        this.updateInterval = setInterval(() => {
            this.updateDashboard();
        }, CONFIG.UPDATE_INTERVAL);
    }

    stopAutoUpdate() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
    }

    async updateDashboard() {
        try {
            await this.updateBlockchainStats();
            await this.updateNetworkStatus();
            await this.updateMiningStatus();
        } catch (error) {
            console.error('Dashboard update failed:', error);
        }
    }

    async updateBlockchainStats() {
        try {
            const chainData = await this.api.getChain();
            const blockchain = this.state.get('blockchain');
            
            this.state.update('blockchain', {
                chain: chainData.chain || [],
                length: chainData.length || 0,
                difficulty: chainData.difficulty || 0,
                lastBlock: chainData.chain?.[chainData.chain.length - 1] || null
            });

            this.updateBlockchainUI();
        } catch (error) {
            console.error('Failed to update blockchain stats:', error);
        }
    }

    updateBlockchainUI() {
        const blockchain = this.state.get('blockchain');
        const statsContainer = document.getElementById('blockchain-stats');
        
        if (statsContainer) {
            statsContainer.innerHTML = `
                ${UIComponents.createStatCard(blockchain.length, 'Blocks in Chain', '🔗')}
                ${UIComponents.createStatCard(blockchain.difficulty, 'Current Difficulty', '⚡')}
                ${UIComponents.createStatCard(blockchain.chain.length > 0 ? blockchain.chain[blockchain.chain.length - 1].index : 0, 'Latest Block', '📦')}
                ${UIComponents.createStatCard(blockchain.chain.reduce((total, block) => total + block.transactions.length, 0), 'Total Transactions', '💸')}
            `;
        }
    }

    async updateWalletInfo() {
        // This would be implemented when wallet functionality is added
        const wallet = this.state.get('wallet');
        // Update wallet UI here
    }

    async updateNetworkStatus() {
        try {
            const networkData = await this.api.getNetworkStatus();
            this.state.update('network', {
                nodes: networkData.nodes || [],
                connected: networkData.connected || 0,
                status: networkData.status || 'disconnected'
            });

            this.updateNetworkUI();
        } catch (error) {
            console.error('Failed to update network status:', error);
        }
    }

    updateNetworkUI() {
        const network = this.state.get('network');
        const networkContainer = document.getElementById('network-status');
        
        if (networkContainer) {
            networkContainer.innerHTML = `
                ${UIComponents.createStatCard(network.connected, 'Connected Nodes', '🌐')}
                ${UIComponents.createStatCard(network.nodes.length, 'Total Nodes', '🖥️')}
                <div class="network-status-indicator">
                    <span class="status-dot ${network.status}"></span>
                    <span class="status-text">${network.status}</span>
                </div>
            `;
        }
    }

    async updateMiningStatus() {
        try {
            const miningData = await this.api.getMiningStatus();
            this.state.update('mining', {
                isActive: miningData.isActive || false,
                currentBlock: miningData.currentBlock || null,
                progress: miningData.progress || 0
            });

            this.updateMiningUI();
        } catch (error) {
            console.error('Failed to update mining status:', error);
        }
    }

    updateMiningUI() {
        const mining = this.state.get('mining');
        const miningContainer = document.getElementById('mining-status');
        
        if (miningContainer) {
            miningContainer.innerHTML = `
                <div class="mining-status">
                    <div class="mining-indicator ${mining.isActive ? 'active' : 'inactive'}"></div>
                    <div class="mining-info">
                        <div class="mining-status-text">${mining.isActive ? 'Mining Active' : 'Mining Inactive'}</div>
                        ${mining.isActive ? UIComponents.createProgressBar(mining.progress, 'Mining Progress') : ''}
                    </div>
                </div>
            `;
        }
    }
}

// ===== TRANSACTION MANAGER =====
class TransactionManager {
    constructor(apiService, appState) {
        this.api = apiService;
        this.state = appState;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadTransactions();
    }

    setupEventListeners() {
        const form = document.getElementById('transaction-form');
        if (form) {
            form.addEventListener('submit', Utils.debounce(this.handleTransactionSubmit.bind(this), CONFIG.DEBOUNCE_DELAY));
        }
    }

    async handleTransactionSubmit(event) {
        event.preventDefault();
        
        const formData = new FormData(event.target);
        const transactionData = {
            sender: formData.get('sender'),
            recipient: formData.get('recipient'),
            amount: parseFloat(formData.get('amount'))
        };

        const submitButton = event.target.querySelector('button[type="submit"]');
        const originalText = submitButton.textContent;
        
        try {
            submitButton.disabled = true;
            submitButton.textContent = 'Creating Transaction...';
            
            await this.api.createTransaction(transactionData);
            
            Utils.showNotification('Transaction created successfully!', 'success');
            event.target.reset();
            
            // Refresh transactions
            await this.loadTransactions();
            
        } catch (error) {
            console.error('Transaction creation failed:', error);
            Utils.showNotification('Failed to create transaction', 'error');
        } finally {
            submitButton.disabled = false;
            submitButton.textContent = originalText;
        }
    }

    async loadTransactions() {
        try {
            const transactions = await this.api.getTransactions();
            this.state.update('transactions', {
                pending: transactions.pending || [],
                confirmed: transactions.confirmed || []
            });

            this.updateTransactionsUI();
        } catch (error) {
            console.error('Failed to load transactions:', error);
        }
    }

    updateTransactionsUI() {
        const transactions = this.state.get('transactions');
        
        // Update pending transactions
        const pendingContainer = document.getElementById('pending-transactions');
        if (pendingContainer) {
            if (transactions.pending.length === 0) {
                pendingContainer.innerHTML = '<p class="no-data">No pending transactions</p>';
            } else {
                const headers = ['Hash', 'From', 'To', 'Amount', 'Status'];
                const data = transactions.pending.map(tx => [
                    Utils.formatHash(tx.hash),
                    Utils.formatAddress(tx.sender),
                    Utils.formatAddress(tx.recipient),
                    Utils.formatCurrency(tx.amount),
                    '<span class="badge badge-warning">Pending</span>'
                ]);
                
                pendingContainer.innerHTML = UIComponents.createTable(headers, data);
            }
        }

        // Update confirmed transactions
        const confirmedContainer = document.getElementById('confirmed-transactions');
        if (confirmedContainer) {
            if (transactions.confirmed.length === 0) {
                confirmedContainer.innerHTML = '<p class="no-data">No confirmed transactions</p>';
            } else {
                const headers = ['Hash', 'From', 'To', 'Amount', 'Block', 'Status'];
                const data = transactions.confirmed.map(tx => [
                    Utils.formatHash(tx.hash),
                    Utils.formatAddress(tx.sender),
                    Utils.formatAddress(tx.recipient),
                    Utils.formatCurrency(tx.amount),
                    tx.blockIndex || 'N/A',
                    '<span class="badge badge-success">Confirmed</span>'
                ]);
                
                confirmedContainer.innerHTML = UIComponents.createTable(headers, data);
            }
        }
    }
}

// ===== MINING MANAGER =====
class MiningManager {
    constructor(apiService, appState) {
        this.api = apiService;
        this.state = appState;
        this.isMining = false;
        this.init();
    }

    init() {
        this.setupEventListeners();
    }

    setupEventListeners() {
        const startButton = document.getElementById('start-mining');
        const stopButton = document.getElementById('stop-mining');
        const mineButton = document.getElementById('mine-block');

        if (startButton) {
            startButton.addEventListener('click', this.startMining.bind(this));
        }
        
        if (stopButton) {
            stopButton.addEventListener('click', this.stopMining.bind(this));
        }
        
        if (mineButton) {
            mineButton.addEventListener('click', this.mineSingleBlock.bind(this));
        }
    }

    async startMining() {
        if (this.isMining) return;
        
        try {
            this.isMining = true;
            Utils.showNotification('Mining started', 'success');
            
            // Update UI
            const startButton = document.getElementById('start-mining');
            const stopButton = document.getElementById('stop-mining');
            
            if (startButton) startButton.disabled = true;
            if (stopButton) stopButton.disabled = false;
            
            // Start mining loop
            this.miningLoop();
            
        } catch (error) {
            console.error('Failed to start mining:', error);
            Utils.showNotification('Failed to start mining', 'error');
            this.isMining = false;
        }
    }

    async stopMining() {
        this.isMining = false;
        Utils.showNotification('Mining stopped', 'info');
        
        // Update UI
        const startButton = document.getElementById('start-mining');
        const stopButton = document.getElementById('stop-mining');
        
        if (startButton) startButton.disabled = false;
        if (stopButton) stopButton.disabled = true;
    }

    async mineSingleBlock() {
        const mineButton = document.getElementById('mine-block');
        const originalText = mineButton.textContent;
        
        try {
            mineButton.disabled = true;
            mineButton.textContent = 'Mining...';
            
            const result = await this.api.mineBlock();
            
            Utils.showNotification(`Block mined! Hash: ${Utils.formatHash(result.hash)}`, 'success');
            
            // Refresh blockchain data
            window.dashboardManager?.updateBlockchainStats();
            
        } catch (error) {
            console.error('Mining failed:', error);
            Utils.showNotification('Mining failed', 'error');
        } finally {
            mineButton.disabled = false;
            mineButton.textContent = originalText;
        }
    }

    async miningLoop() {
        while (this.isMining) {
            try {
                await this.mineSingleBlock();
                await new Promise(resolve => setTimeout(resolve, 1000)); // Wait 1 second between blocks
            } catch (error) {
                console.error('Mining loop error:', error);
                break;
            }
        }
    }
}

// ===== NETWORK MANAGER =====
class NetworkManager {
    constructor(apiService, appState) {
        this.api = apiService;
        this.state = appState;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadNetworkData();
    }

    setupEventListeners() {
        const refreshButton = document.getElementById('refresh-network');
        if (refreshButton) {
            refreshButton.addEventListener('click', this.loadNetworkData.bind(this));
        }
    }

    async loadNetworkData() {
        try {
            const networkData = await this.api.getNetworkStatus();
            this.state.update('network', {
                nodes: networkData.nodes || [],
                connected: networkData.connected || 0,
                status: networkData.status || 'disconnected'
            });

            this.updateNetworkUI();
        } catch (error) {
            console.error('Failed to load network data:', error);
        }
    }

    updateNetworkUI() {
        const network = this.state.get('network');
        const nodesContainer = document.getElementById('network-nodes');
        
        if (nodesContainer) {
            if (network.nodes.length === 0) {
                nodesContainer.innerHTML = '<p class="no-data">No nodes connected</p>';
            } else {
                const nodeCards = network.nodes.map(node => `
                    <div class="node-item">
                        <div class="node-status ${node.status}"></div>
                        <div class="node-info">
                            <div class="node-address">${Utils.formatAddress(node.address)}</div>
                            <div class="node-details">
                                <span class="node-version">v${node.version}</span>
                                <span class="node-blocks">${node.blockCount} blocks</span>
                            </div>
                        </div>
                    </div>
                `).join('');
                
                nodesContainer.innerHTML = `
                    <div class="node-list">
                        ${nodeCards}
                    </div>
                `;
            }
        }
    }
}

// ===== SIMULATION MANAGER =====
class SimulationManager {
    constructor(apiService, appState) {
        this.api = apiService;
        this.state = appState;
        this.isSimulating = false;
        this.init();
    }

    init() {
        this.setupEventListeners();
    }

    setupEventListeners() {
        const startButton = document.getElementById('start-simulation');
        const stopButton = document.getElementById('stop-simulation');
        
        if (startButton) {
            startButton.addEventListener('click', this.startSimulation.bind(this));
        }
        
        if (stopButton) {
            stopButton.addEventListener('click', this.stopSimulation.bind(this));
        }
    }

    async startSimulation() {
        if (this.isSimulating) return;
        
        try {
            this.isSimulating = true;
            Utils.showNotification('Attack simulation started', 'warning');
            
            // Update UI
            const startButton = document.getElementById('start-simulation');
            const stopButton = document.getElementById('stop-simulation');
            
            if (startButton) startButton.disabled = true;
            if (stopButton) stopButton.disabled = false;
            
            // Start simulation
            this.simulationLoop();
            
        } catch (error) {
            console.error('Failed to start simulation:', error);
            Utils.showNotification('Failed to start simulation', 'error');
            this.isSimulating = false;
        }
    }

    async stopSimulation() {
        this.isSimulating = false;
        Utils.showNotification('Attack simulation stopped', 'info');
        
        // Update UI
        const startButton = document.getElementById('start-simulation');
        const stopButton = document.getElementById('stop-simulation');
        
        if (startButton) startButton.disabled = false;
        if (stopButton) stopButton.disabled = true;
    }

    async simulationLoop() {
        while (this.isSimulating) {
            try {
                // Simulate attack progress
                await new Promise(resolve => setTimeout(resolve, 2000));
                
                // Update simulation progress
                this.updateSimulationProgress();
                
            } catch (error) {
                console.error('Simulation loop error:', error);
                break;
            }
        }
    }

    updateSimulationProgress() {
        const progressContainer = document.getElementById('simulation-progress');
        if (progressContainer) {
            const progress = Math.random() * 100;
            progressContainer.innerHTML = UIComponents.createProgressBar(progress, 'Attack Progress');
        }
    }
}

// ===== MAIN APPLICATION =====
class BlockyHomeworkApp {
    constructor() {
        this.apiService = new ApiService();
        this.appState = new AppState();
        this.managers = {};
        this.init();
    }

    init() {
        // Initialize managers
        this.managers.dashboard = new DashboardManager(this.apiService, this.appState);
        this.managers.transactions = new TransactionManager(this.apiService, this.appState);
        this.managers.mining = new MiningManager(this.apiService, this.appState);
        this.managers.network = new NetworkManager(this.apiService, this.appState);
        this.managers.simulation = new SimulationManager(this.apiService, this.appState);

        // Make managers globally accessible for debugging
        window.dashboardManager = this.managers.dashboard;
        window.transactionManager = this.managers.transactions;
        window.miningManager = this.managers.mining;
        window.networkManager = this.managers.network;
        window.simulationManager = this.managers.simulation;

        // Setup global error handling
        this.setupErrorHandling();
        
        // Initialize page-specific functionality
        this.initializePage();
        
        console.log('BlockyHomework App initialized successfully!');
    }

    setupErrorHandling() {
        window.addEventListener('error', (event) => {
            console.error('Global error:', event.error);
            Utils.showNotification('An unexpected error occurred', 'error');
        });

        window.addEventListener('unhandledrejection', (event) => {
            console.error('Unhandled promise rejection:', event.reason);
            Utils.showNotification('An unexpected error occurred', 'error');
        });
    }

    initializePage() {
        const currentPage = this.getCurrentPage();
        
        switch (currentPage) {
            case 'dashboard':
                this.managers.dashboard.loadInitialData();
                break;
            case 'transactions':
                this.managers.transactions.loadTransactions();
                break;
            case 'mining':
                this.managers.mining.updateMiningStatus();
                break;
            case 'network':
                this.managers.network.loadNetworkData();
                break;
            case 'simulation':
                // Simulation page specific initialization
                break;
        }
    }

    getCurrentPage() {
        const path = window.location.pathname;
        if (path === '/' || path === '/dashboard') return 'dashboard';
        if (path.includes('/transactions')) return 'transactions';
        if (path.includes('/mining')) return 'mining';
        if (path.includes('/network')) return 'network';
        if (path.includes('/simulation')) return 'simulation';
        return 'dashboard';
    }
}

// ===== INITIALIZATION =====
document.addEventListener('DOMContentLoaded', () => {
    // Initialize the application
    window.app = new BlockyHomeworkApp();
    
    // Add some CSS for notifications
    const style = document.createElement('style');
    style.textContent = `
        .notification {
            position: fixed;
            top: 20px;
            right: 20px;
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-lg);
            padding: var(--spacing-md);
            box-shadow: var(--shadow-lg);
            z-index: var(--z-modal);
            max-width: 400px;
            animation: slideIn 0.3s ease-out;
        }
        
        .notification-content {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: var(--spacing-md);
        }
        
        .notification-close {
            background: none;
            border: none;
            color: var(--text-muted);
            cursor: pointer;
            font-size: var(--font-size-lg);
            padding: 0;
        }
        
        .notification-close:hover {
            color: var(--text-primary);
        }
        
        .notification-success {
            border-left: 4px solid var(--success-color);
        }
        
        .notification-error {
            border-left: 4px solid var(--error-color);
        }
        
        .notification-warning {
            border-left: 4px solid var(--warning-color);
        }
        
        .notification-info {
            border-left: 4px solid var(--info-color);
        }
        
        .fade-out {
            animation: fadeOut 0.3s ease-out forwards;
        }
        
        @keyframes fadeOut {
            to { opacity: 0; transform: translateX(100%); }
        }
        
        .loading-spinner {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: var(--spacing-xl);
        }
        
        .spinner-ring {
            width: 40px;
            height: 40px;
            border: 3px solid var(--border-color);
            border-top: 3px solid var(--primary-color);
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .spinner-text {
            margin-top: var(--spacing-md);
            color: var(--text-muted);
        }
        
        .no-data {
            text-align: center;
            color: var(--text-muted);
            padding: var(--spacing-xl);
        }
    `;
    document.head.appendChild(style);
});

// ===== GLOBAL FUNCTIONS FOR TEMPLATES =====
window.createTransaction = async function() {
    const form = document.getElementById('transaction-form');
    if (form) {
        form.dispatchEvent(new Event('submit'));
    }
};

window.startMining = function() {
    if (window.miningManager) {
        window.miningManager.startMining();
    }
};

window.stopMining = function() {
    if (window.miningManager) {
        window.miningManager.stopMining();
    }
};

window.mineBlock = function() {
    if (window.miningManager) {
        window.miningManager.mineSingleBlock();
    }
};

window.startSimulation = function() {
    if (window.simulationManager) {
        window.simulationManager.startSimulation();
    }
};

window.stopSimulation = function() {
    if (window.simulationManager) {
        window.simulationManager.stopSimulation();
    }
};

window.refreshNetwork = function() {
    if (window.networkManager) {
        window.networkManager.loadNetworkData();
    }
}; 