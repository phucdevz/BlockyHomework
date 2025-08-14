/**
 * MINING PAGE - JAVASCRIPT MODULE
 * Handles mining operations, status, and statistics
 */

class MiningManager {
    constructor() {
        this.isMining = false;
        this.miningInterval = null;
        this.updateInterval = null;
        this.miningStats = {
            blocksMined: 0,
            totalRewards: 0,
            miningRate: 0,
            startTime: null
        };
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadMiningStatus();
        this.startAutoUpdate();
    }

    setupEventListeners() {
        // Mining control buttons
        const startBtn = document.getElementById('start-mining');
        const stopBtn = document.getElementById('stop-mining');
        const mineBlockBtn = document.getElementById('mine-block');

        if (startBtn) {
            startBtn.addEventListener('click', () => this.startMining());
        }

        if (stopBtn) {
            stopBtn.addEventListener('click', () => this.stopMining());
        }

        if (mineBlockBtn) {
            mineBlockBtn.addEventListener('click', () => this.mineSingleBlock());
        }

        // Range input for attack power
        const attackPowerRange = document.getElementById('attack-power');
        if (attackPowerRange) {
            attackPowerRange.addEventListener('input', (e) => {
                const value = e.target.value;
                const valueDisplay = document.getElementById('attack-power-value');
                if (valueDisplay) {
                    valueDisplay.textContent = `${value}%`;
                }
            });
        }
    }

    async loadMiningStatus() {
        try {
            const response = await fetch('/api/mining/status');
            const data = await response.json();

            this.updateMiningStatus(data);
            this.updateMiningStatistics();
        } catch (error) {
            console.error('Error loading mining status:', error);
        }
    }

    updateMiningStatus(data) {
        // Update difficulty and reward display
        const difficultyElement = document.getElementById('current-difficulty');
        const rewardElement = document.getElementById('block-reward');

        if (difficultyElement) {
            difficultyElement.textContent = data.difficulty || 0;
        }

        if (rewardElement) {
            rewardElement.textContent = `${data.block_reward || 10} ZTL Coin`;
        }

        // Update mining indicator
        this.updateMiningIndicator();
    }

    updateMiningIndicator() {
        const indicator = document.querySelector('.mining-indicator');
        const statusText = document.querySelector('.mining-status-text');

        if (indicator && statusText) {
            if (this.isMining) {
                indicator.classList.remove('inactive');
                indicator.classList.add('active');
                statusText.textContent = 'Mining Active';
            } else {
                indicator.classList.remove('active');
                indicator.classList.add('inactive');
                statusText.textContent = 'Mining Inactive';
            }
        }
    }

    async startMining() {
        if (this.isMining) {
            Utils.showNotification('Mining is already active', 'warning');
            return;
        }

        try {
            const response = await fetch('/api/mining/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            const result = await response.json();

            if (result.success) {
                this.isMining = true;
                this.miningStats.startTime = Date.now();
                this.updateMiningIndicator();
                this.updateMiningControls();
                this.startMiningProgress();
                Utils.showNotification('Mining started successfully!', 'success');
            } else {
                Utils.showNotification(result.error || 'Failed to start mining', 'error');
            }
        } catch (error) {
            console.error('Error starting mining:', error);
            Utils.showNotification('Network error occurred', 'error');
        }
    }

    async stopMining() {
        if (!this.isMining) {
            Utils.showNotification('Mining is not active', 'warning');
            return;
        }

        try {
            const response = await fetch('/api/mining/stop', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            const result = await response.json();

            if (result.success) {
                this.isMining = false;
                this.updateMiningIndicator();
                this.updateMiningControls();
                this.stopMiningProgress();
                Utils.showNotification('Mining stopped successfully!', 'success');
            } else {
                Utils.showNotification(result.error || 'Failed to stop mining', 'error');
            }
        } catch (error) {
            console.error('Error stopping mining:', error);
            Utils.showNotification('Network error occurred', 'error');
        }
    }

    async mineSingleBlock() {
        try {
            // Show loading state
            this.showMiningProgress();
            
            const response = await fetch('/api/mining/mine-block', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            const result = await response.json();

            if (result.success) {
                this.miningStats.blocksMined++;
                this.miningStats.totalRewards += 10; // Block reward
                this.updateMiningStatistics();
                this.hideMiningProgress();
                Utils.showNotification(`Block #${result.block.index} mined successfully!`, 'success');
            } else {
                this.hideMiningProgress();
                Utils.showNotification(result.error || 'Failed to mine block', 'error');
            }
        } catch (error) {
            console.error('Error mining block:', error);
            this.hideMiningProgress();
            Utils.showNotification('Network error occurred', 'error');
        }
    }

    updateMiningControls() {
        const startBtn = document.getElementById('start-mining');
        const stopBtn = document.getElementById('stop-mining');
        const mineBlockBtn = document.getElementById('mine-block');

        if (startBtn) {
            startBtn.disabled = this.isMining;
        }

        if (stopBtn) {
            stopBtn.disabled = !this.isMining;
        }

        if (mineBlockBtn) {
            mineBlockBtn.disabled = this.isMining;
        }
    }

    showMiningProgress() {
        const progressContainer = document.getElementById('mining-progress');
        if (progressContainer) {
            progressContainer.style.display = 'block';
        }
    }

    hideMiningProgress() {
        const progressContainer = document.getElementById('mining-progress');
        if (progressContainer) {
            progressContainer.style.display = 'none';
        }
    }

    startMiningProgress() {
        this.showMiningProgress();
        
        let progress = 0;
        this.miningInterval = setInterval(() => {
            progress += Math.random() * 10;
            if (progress > 100) progress = 100;
            
            this.updateProgressBar(progress);
            
            if (progress >= 100) {
                this.mineSingleBlock();
                progress = 0;
            }
        }, 1000);
    }

    stopMiningProgress() {
        if (this.miningInterval) {
            clearInterval(this.miningInterval);
            this.miningInterval = null;
        }
        this.hideMiningProgress();
    }

    updateProgressBar(progress) {
        const progressBar = document.getElementById('mining-progress-bar');
        const progressText = document.getElementById('mining-progress-text');

        if (progressBar) {
            progressBar.style.width = `${progress}%`;
        }

        if (progressText) {
            progressText.textContent = `${Math.round(progress)}%`;
        }
    }

    updateMiningStatistics() {
        // Calculate mining rate (blocks per hour)
        if (this.miningStats.startTime) {
            const elapsedHours = (Date.now() - this.miningStats.startTime) / (1000 * 60 * 60);
            this.miningStats.miningRate = elapsedHours > 0 ? this.miningStats.blocksMined / elapsedHours : 0;
        }

        // Update display
        this.updateStat('blocks-mined', this.miningStats.blocksMined);
        this.updateStat('mining-rate', this.miningStats.miningRate.toFixed(2));
        this.updateStat('total-rewards', `${this.miningStats.totalRewards} ZTL Coin`);
    }

    updateStat(elementId, value) {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = value;
        }
    }

    async loadRecentBlocks() {
        try {
            const response = await fetch('/api/blockchain/chain');
            const data = await response.json();

            if (data.chain && data.chain.length > 0) {
                const recentBlocks = data.chain.slice(-5); // Last 5 blocks
                this.renderRecentBlocks(recentBlocks);
            }
        } catch (error) {
            console.error('Error loading recent blocks:', error);
        }
    }

    renderRecentBlocks(blocks) {
        const container = document.getElementById('recent-blocks');
        if (!container) return;

        if (blocks.length === 0) {
            container.innerHTML = '<p class="no-data">No blocks mined yet</p>';
            return;
        }

        const blocksHTML = blocks.map(block => this.createBlockCard(block)).join('');
        container.innerHTML = blocksHTML;
    }

    createBlockCard(block) {
        const timestamp = new Date(block.timestamp * 1000).toLocaleString();
        const hash = Utils.formatHash(block.hash);
        const transactionCount = block.transactions ? block.transactions.length : 0;

        return `
            <div class="block-card">
                <div class="block-header">
                    <span class="block-index">Block #${block.index}</span>
                    <span class="block-hash">${hash}</span>
                </div>
                <div class="block-details">
                    <div class="block-info">
                        <span class="block-time">${timestamp}</span>
                        <span class="block-transactions">${transactionCount} transactions</span>
                    </div>
                    <div class="block-proof">
                        <span class="proof-label">Proof:</span>
                        <span class="proof-value">${block.proof}</span>
                    </div>
                </div>
            </div>
        `;
    }

    startAutoUpdate() {
        this.updateInterval = setInterval(() => {
            this.loadMiningStatus();
            this.loadRecentBlocks();
        }, 5000); // Update every 5 seconds
    }

    stopAutoUpdate() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
    }

    destroy() {
        this.stopMining();
        this.stopAutoUpdate();
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.miningManager = new MiningManager();
});
