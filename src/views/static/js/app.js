// BlockyHomework - Main JavaScript Application

// Global variables
let isMining = false;
let isSimulating = false;
let miningInterval = null;
let simulationInterval = null;

// API endpoints
const API_ENDPOINTS = {
    TRANSACTIONS: '/api/transactions/new',
    CHAIN: '/api/chain',
    MINE: '/api/mine',
    WALLET_BALANCE: '/api/wallet/balance/',
    NODES: '/api/nodes/list',
    SIMULATION: '/api/simulation'
};

// Utility functions
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

function formatBalance(balance) {
    return parseFloat(balance).toFixed(2) + ' PyCoin';
}

function formatHash(hash) {
    return hash.substring(0, 8) + '...';
}

// API functions
async function apiCall(endpoint, method = 'GET', data = null) {
    try {
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            }
        };
        
        if (data) {
            options.body = JSON.stringify(data);
        }
        
        const response = await fetch(endpoint, options);
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.message || 'API call failed');
        }
        
        return result;
    } catch (error) {
        console.error('API Error:', error);
        showNotification(error.message, 'error');
        throw error;
    }
}

// Dashboard functions
function refreshData() {
    Promise.all([
        apiCall(API_ENDPOINTS.CHAIN),
        apiCall(API_ENDPOINTS.WALLET_BALANCE + 'current'),
        apiCall('/api/transactions/pending'),
        apiCall(API_ENDPOINTS.NODES)
    ]).then(([chain, balance, pending, nodes]) => {
        updateDashboard(chain, balance, pending, nodes);
    }).catch(error => {
        console.error('Failed to refresh data:', error);
    });
}

function updateDashboard(chain, balance, pending, nodes) {
    // Update chain length
    const chainLengthElement = document.querySelector('.stat-card:nth-child(1) p');
    if (chainLengthElement) {
        chainLengthElement.textContent = chain.length || 0;
    }
    
    // Update wallet balance
    const balanceElement = document.querySelector('.stat-card:nth-child(2) p');
    if (balanceElement) {
        balanceElement.textContent = formatBalance(balance.balance || 0);
    }
    
    // Update pending transactions
    const pendingElement = document.querySelector('.stat-card:nth-child(3) p');
    if (pendingElement) {
        pendingElement.textContent = pending.length || 0;
    }
    
    // Update connected nodes
    const nodesElement = document.querySelector('.stat-card:nth-child(4) p');
    if (nodesElement) {
        nodesElement.textContent = nodes.length || 0;
    }
    
    // Update recent blocks
    updateRecentBlocks(chain);
}

function updateRecentBlocks(chain) {
    const blocksList = document.querySelector('.blocks-list');
    if (!blocksList) return;
    
    blocksList.innerHTML = '';
    const recentBlocks = chain.slice(-5).reverse();
    
    recentBlocks.forEach(block => {
        const blockElement = document.createElement('div');
        blockElement.className = 'block-item';
        blockElement.innerHTML = `
            <span class="block-index">#${block.index}</span>
            <span class="block-hash">${formatHash(block.hash)}</span>
            <span class="block-transactions">${block.transactions.length} tx</span>
        `;
        blocksList.appendChild(blockElement);
    });
}

// Transaction functions
function createTransaction() {
    const recipient = document.getElementById('recipient')?.value;
    const amount = document.getElementById('amount')?.value;
    
    if (!recipient || !amount) {
        showNotification('Please fill in all fields', 'error');
        return;
    }
    
    const transactionData = {
        recipient: recipient,
        amount: parseFloat(amount)
    };
    
    apiCall(API_ENDPOINTS.TRANSACTIONS, 'POST', transactionData)
        .then(result => {
            showNotification('Transaction created successfully!', 'success');
            document.getElementById('transaction-form')?.reset();
            refreshData();
        })
        .catch(error => {
            showNotification('Failed to create transaction', 'error');
        });
}

// Mining functions
function startMining() {
    if (isMining) return;
    
    isMining = true;
    updateMiningStatus('active');
    
    miningInterval = setInterval(() => {
        mineBlock();
    }, 1000);
    
    showNotification('Mining started', 'success');
}

function stopMining() {
    if (!isMining) return;
    
    isMining = false;
    clearInterval(miningInterval);
    updateMiningStatus('inactive');
    
    showNotification('Mining stopped', 'info');
}

function mineBlock() {
    apiCall(API_ENDPOINTS.MINE, 'POST')
        .then(result => {
            showNotification(`Block mined! Hash: ${formatHash(result.hash)}`, 'success');
            refreshData();
            updateMiningProgress(result);
        })
        .catch(error => {
            console.error('Mining failed:', error);
        });
}

function mineSingleBlock() {
    mineBlock();
}

function updateMiningStatus(status) {
    const statusElement = document.querySelector('.status-indicator');
    if (statusElement) {
        statusElement.className = `status-indicator ${status}`;
        statusElement.querySelector('.status-text').textContent = status.charAt(0).toUpperCase() + status.slice(1);
    }
}

function updateMiningProgress(data) {
    const progressElement = document.querySelector('.progress-fill');
    const nonceElement = document.querySelector('.mining-progress p:nth-child(2)');
    const hashElement = document.querySelector('.mining-progress p:nth-child(3)');
    
    if (progressElement) {
        progressElement.style.width = '100%';
        setTimeout(() => {
            progressElement.style.width = '0%';
        }, 1000);
    }
    
    if (nonceElement) {
        nonceElement.textContent = `Nonce: ${data.proof || 'Calculating...'}`;
    }
    
    if (hashElement) {
        hashElement.textContent = `Current Hash: ${formatHash(data.hash || 'Calculating...')}`;
    }
}

// Network functions
function discoverNodes() {
    apiCall('/api/nodes/discover', 'POST')
        .then(result => {
            showNotification(`Discovered ${result.discovered} new nodes`, 'success');
            refreshData();
        })
        .catch(error => {
            showNotification('Failed to discover nodes', 'error');
        });
}

function syncWithNetwork() {
    apiCall('/api/nodes/sync', 'POST')
        .then(result => {
            showNotification('Network synchronization completed', 'success');
            refreshData();
        })
        .catch(error => {
            showNotification('Network synchronization failed', 'error');
        });
}

function broadcastTransaction() {
    apiCall('/api/transactions/broadcast', 'POST')
        .then(result => {
            showNotification('Transaction broadcasted to network', 'success');
        })
        .catch(error => {
            showNotification('Failed to broadcast transaction', 'error');
        });
}

function refreshNetwork() {
    refreshData();
    showNotification('Network data refreshed', 'info');
}

// Simulation functions
function startSimulation() {
    if (isSimulating) return;
    
    const attackType = document.getElementById('attack-type')?.value;
    const attackPower = document.getElementById('attack-power')?.value;
    const attackDuration = document.getElementById('attack-duration')?.value;
    
    const simulationData = {
        type: attackType,
        power: parseInt(attackPower),
        duration: parseInt(attackDuration)
    };
    
    apiCall('/api/simulation/start', 'POST', simulationData)
        .then(result => {
            isSimulating = true;
            updateSimulationStatus('running');
            startSimulationProgress();
            showNotification('Simulation started', 'success');
        })
        .catch(error => {
            showNotification('Failed to start simulation', 'error');
        });
}

function stopSimulation() {
    if (!isSimulating) return;
    
    apiCall('/api/simulation/stop', 'POST')
        .then(result => {
            isSimulating = false;
            clearInterval(simulationInterval);
            updateSimulationStatus('stopped');
            showNotification('Simulation stopped', 'info');
        })
        .catch(error => {
            showNotification('Failed to stop simulation', 'error');
        });
}

function resetSimulation() {
    apiCall('/api/simulation/reset', 'POST')
        .then(result => {
            isSimulating = false;
            clearInterval(simulationInterval);
            updateSimulationStatus('idle');
            showNotification('Simulation reset', 'info');
        })
        .catch(error => {
            showNotification('Failed to reset simulation', 'error');
        });
}

function startSimulationProgress() {
    let progress = 0;
    simulationInterval = setInterval(() => {
        progress += 1;
        updateSimulationProgress(progress);
        
        if (progress >= 100) {
            clearInterval(simulationInterval);
            isSimulating = false;
            updateSimulationStatus('completed');
        }
    }, 1000);
}

function updateSimulationStatus(status) {
    const statusElement = document.querySelector('.simulation-status .value');
    if (statusElement) {
        statusElement.textContent = status.charAt(0).toUpperCase() + status.slice(1);
        statusElement.className = `value ${status}`;
    }
}

function updateSimulationProgress(progress) {
    const progressElement = document.querySelector('.simulation-status .value:nth-child(2)');
    if (progressElement) {
        progressElement.textContent = `${progress}%`;
    }
}

// Event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Initialize dashboard
    refreshData();
    
    // Set up auto-refresh
    setInterval(refreshData, 5000);
    
    // Form submission handlers
    const transactionForm = document.getElementById('transaction-form');
    if (transactionForm) {
        transactionForm.addEventListener('submit', function(e) {
            e.preventDefault();
            createTransaction();
        });
    }
    
    // Attack power slider
    const attackPowerSlider = document.getElementById('attack-power');
    const powerDisplay = document.getElementById('power-display');
    if (attackPowerSlider && powerDisplay) {
        attackPowerSlider.addEventListener('input', function() {
            powerDisplay.textContent = this.value + '%';
        });
    }
});

// Global function exports for HTML onclick handlers
window.createTransaction = createTransaction;
window.mineBlock = mineBlock;
window.refreshData = refreshData;
window.startMining = startMining;
window.stopMining = stopMining;
window.mineSingleBlock = mineSingleBlock;
window.discoverNodes = discoverNodes;
window.syncWithNetwork = syncWithNetwork;
window.broadcastTransaction = broadcastTransaction;
window.refreshNetwork = refreshNetwork;
window.startSimulation = startSimulation;
window.stopSimulation = stopSimulation;
window.resetSimulation = resetSimulation; 