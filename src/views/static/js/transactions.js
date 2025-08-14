/**
 * TRANSACTIONS PAGE - JAVASCRIPT MODULE
 * Handles transaction creation, management, and display
 */

class TransactionManager {
    constructor() {
        this.transactions = [];
        this.pendingTransactions = [];
        this.confirmedTransactions = [];
        this.updateInterval = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadTransactionData();
        this.startAutoUpdate();
    }

    setupEventListeners() {
        // Transaction form submission
        const form = document.getElementById('transaction-form');
        if (form) {
            form.addEventListener('submit', (e) => this.handleTransactionSubmit(e));
        }

        // Form reset
        const resetBtn = document.querySelector('button[type="reset"]');
        if (resetBtn) {
            resetBtn.addEventListener('click', () => this.resetForm());
        }

        // Auto-fill sender address
        this.loadWalletAddress();
    }

    async loadWalletAddress() {
        try {
            const response = await fetch('/api/wallet/address');
            const data = await response.json();
            
            if (data.address) {
                const senderInput = document.getElementById('sender');
                if (senderInput) {
                    senderInput.value = data.address;
                    senderInput.readOnly = true;
                }
            }
        } catch (error) {
            console.error('Error loading wallet address:', error);
        }
    }

    async handleTransactionSubmit(event) {
        event.preventDefault();
        
        const form = event.target;
        const formData = new FormData(form);
        
        const transactionData = {
            recipient: formData.get('recipient'),
            amount: parseFloat(formData.get('amount'))
        };

        // Validate form data
        if (!this.validateTransactionData(transactionData)) {
            return;
        }

        try {
            // Show loading state
            this.showLoadingState();
            
            const response = await fetch('/api/transactions/create', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(transactionData)
            });

            const result = await response.json();

            if (result.success) {
                Utils.showNotification('Transaction created successfully!', 'success');
                this.resetForm();
                this.loadTransactionData(); // Refresh data
            } else {
                Utils.showNotification(result.error || 'Failed to create transaction', 'error');
            }
        } catch (error) {
            console.error('Error creating transaction:', error);
            Utils.showNotification('Network error occurred', 'error');
        } finally {
            this.hideLoadingState();
        }
    }

    validateTransactionData(data) {
        if (!data.recipient || data.recipient.trim() === '') {
            Utils.showNotification('Recipient address is required', 'error');
            return false;
        }

        if (!data.amount || data.amount <= 0) {
            Utils.showNotification('Amount must be greater than 0', 'error');
            return false;
        }

        if (data.amount < 0.001) {
            Utils.showNotification('Minimum transaction amount is 0.001 ZTL Coin', 'error');
            return false;
        }

        return true;
    }

    resetForm() {
        const form = document.getElementById('transaction-form');
        if (form) {
            form.reset();
            this.loadWalletAddress(); // Re-fill sender address
        }
    }

    showLoadingState() {
        const submitBtn = document.querySelector('#transaction-form button[type="submit"]');
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="btn-icon">⏳</span> Creating...';
        }
    }

    hideLoadingState() {
        const submitBtn = document.querySelector('#transaction-form button[type="submit"]');
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = 'Create Transaction';
        }
    }

    async loadTransactionData() {
        try {
            await Promise.all([
                this.loadPendingTransactions(),
                this.loadConfirmedTransactions(),
                this.loadTransactionStatistics()
            ]);
        } catch (error) {
            console.error('Error loading transaction data:', error);
        }
    }

    async loadPendingTransactions() {
        try {
            const response = await fetch('/api/transactions/pending');
            const data = await response.json();
            
            this.pendingTransactions = data.transactions || [];
            this.renderPendingTransactions();
        } catch (error) {
            console.error('Error loading pending transactions:', error);
            this.showError('pending-transactions', 'Failed to load pending transactions');
        }
    }

    async loadConfirmedTransactions() {
        try {
            const response = await fetch('/api/wallet/history');
            const data = await response.json();
            
            this.confirmedTransactions = data.transactions || [];
            this.renderConfirmedTransactions();
        } catch (error) {
            console.error('Error loading confirmed transactions:', error);
            this.showError('confirmed-transactions', 'Failed to load confirmed transactions');
        }
    }

    async loadTransactionStatistics() {
        try {
            const pendingCount = this.pendingTransactions.length;
            const confirmedCount = this.confirmedTransactions.length;
            const totalCount = pendingCount + confirmedCount;

            // Update statistics
            this.updateStat('total-transactions', totalCount);
            this.updateStat('pending-count', pendingCount);
            this.updateStat('confirmed-count', confirmedCount);
            
            // Calculate average fee (placeholder)
            this.updateStat('average-fee', '0.001 ZTL');
        } catch (error) {
            console.error('Error loading transaction statistics:', error);
        }
    }

    renderPendingTransactions() {
        const container = document.getElementById('pending-transactions');
        if (!container) return;

        if (this.pendingTransactions.length === 0) {
            container.innerHTML = '<p class="no-data">No pending transactions</p>';
            return;
        }

        const transactionsHTML = this.pendingTransactions.map(tx => this.createTransactionCard(tx, 'pending')).join('');
        container.innerHTML = transactionsHTML;
    }

    renderConfirmedTransactions() {
        const container = document.getElementById('confirmed-transactions');
        if (!container) return;

        if (this.confirmedTransactions.length === 0) {
            container.innerHTML = '<p class="no-data">No confirmed transactions</p>';
            return;
        }

        const transactionsHTML = this.confirmedTransactions.map(tx => this.createTransactionCard(tx, 'confirmed')).join('');
        container.innerHTML = transactionsHTML;
    }

    createTransactionCard(transaction, status) {
        const timestamp = new Date(transaction.timestamp * 1000).toLocaleString();
        const amount = parseFloat(transaction.amount).toFixed(3);
        const hash = Utils.formatHash(transaction.hash);
        const sender = Utils.formatAddress(transaction.sender);
        const recipient = Utils.formatAddress(transaction.recipient);

        return `
            <div class="transaction-card ${status}">
                <div class="transaction-header">
                    <span class="transaction-status ${status}">${status.toUpperCase()}</span>
                    <span class="transaction-amount">${amount} ZTL</span>
                </div>
                <div class="transaction-details">
                    <div class="transaction-addresses">
                        <div class="address-line">
                            <span class="address-label">From:</span>
                            <span class="address-value">${sender}</span>
                        </div>
                        <div class="address-line">
                            <span class="address-label">To:</span>
                            <span class="address-value">${recipient}</span>
                        </div>
                    </div>
                    <div class="transaction-meta">
                        <span class="transaction-hash">Hash: ${hash}</span>
                        <span class="transaction-time">${timestamp}</span>
                    </div>
                </div>
            </div>
        `;
    }

    updateStat(elementId, value) {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = value;
        }
    }

    showError(containerId, message) {
        const container = document.getElementById(containerId);
        if (container) {
            container.innerHTML = `<p class="error-message">${message}</p>`;
        }
    }

    startAutoUpdate() {
        this.updateInterval = setInterval(() => {
            this.loadTransactionData();
        }, 10000); // Update every 10 seconds
    }

    stopAutoUpdate() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
    }

    destroy() {
        this.stopAutoUpdate();
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.transactionManager = new TransactionManager();
});
