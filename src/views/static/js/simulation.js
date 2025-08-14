/**
 * SIMULATION PAGE - JAVASCRIPT MODULE
 * Handles attack simulation and blockchain security testing
 */

class SimulationManager {
    constructor() {
        this.isRunning = false;
        this.simulationData = {
            currentScenario: null,
            attackProgress: 0,
            attackType: '51-percent',
            attackPower: 51,
            attackDuration: 10,
            networkSize: 100
        };
        this.simulationInterval = null;
        this.updateInterval = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadSimulationStatus();
        this.startAutoUpdate();
    }

    setupEventListeners() {
        // Simulation control buttons
        const startBtn = document.getElementById('start-simulation');
        const stopBtn = document.getElementById('stop-simulation');
        const resetBtn = document.getElementById('reset-simulation');

        if (startBtn) {
            startBtn.addEventListener('click', () => this.startSimulation());
        }

        if (stopBtn) {
            stopBtn.addEventListener('click', () => this.stopSimulation());
        }

        if (resetBtn) {
            resetBtn.addEventListener('click', () => this.resetSimulation());
        }

        // Configuration inputs
        const attackTypeSelect = document.getElementById('attack-type');
        const attackPowerRange = document.getElementById('attack-power');
        const attackDurationInput = document.getElementById('attack-duration');
        const networkSizeInput = document.getElementById('network-size');

        if (attackTypeSelect) {
            attackTypeSelect.addEventListener('change', (e) => {
                this.simulationData.attackType = e.target.value;
            });
        }

        if (attackPowerRange) {
            attackPowerRange.addEventListener('input', (e) => {
                this.simulationData.attackPower = parseInt(e.target.value);
                const valueDisplay = document.getElementById('attack-power-value');
                if (valueDisplay) {
                    valueDisplay.textContent = `${e.target.value}%`;
                }
            });
        }

        if (attackDurationInput) {
            attackDurationInput.addEventListener('input', (e) => {
                this.simulationData.attackDuration = parseInt(e.target.value);
            });
        }

        if (networkSizeInput) {
            networkSizeInput.addEventListener('input', (e) => {
                this.simulationData.networkSize = parseInt(e.target.value);
            });
        }
    }

    async loadSimulationStatus() {
        try {
            const response = await fetch('/api/simulation/status');
            const data = await response.json();

            this.simulationData.isRunning = data.is_running || false;
            this.simulationData.currentScenario = data.current_scenario;
            this.simulationData.attackProgress = data.attack_progress || 0;

            this.updateSimulationDisplay();
        } catch (error) {
            console.error('Error loading simulation status:', error);
        }
    }

    updateSimulationDisplay() {
        this.updateSimulationIndicator();
        this.updateAttackProgress();
        this.updateChainComparison();
    }

    updateSimulationIndicator() {
        const indicator = document.querySelector('.simulation-indicator');
        const indicatorText = document.querySelector('.indicator-text');

        if (indicator && indicatorText) {
            if (this.isRunning) {
                indicator.classList.remove('inactive');
                indicator.classList.add('active');
                indicatorText.textContent = 'Simulation Active';
            } else {
                indicator.classList.remove('active');
                indicator.classList.add('inactive');
                indicatorText.textContent = 'Simulation Inactive';
            }
        }
    }

    updateAttackProgress() {
        const progressBar = document.getElementById('attack-progress-bar');
        const progressText = document.getElementById('attack-progress-text');
        const progressContainer = document.getElementById('simulation-progress');

        if (progressBar) {
            progressBar.style.width = `${this.simulationData.attackProgress}%`;
        }

        if (progressText) {
            progressText.textContent = `${Math.round(this.simulationData.attackProgress)}%`;
        }

        if (progressContainer) {
            progressContainer.style.display = this.isRunning ? 'block' : 'none';
        }
    }

    updateChainComparison() {
        this.renderLegitimateChain();
        this.renderAttackChain();
    }

    renderLegitimateChain() {
        const container = document.getElementById('legitimate-chain');
        if (!container) return;

        // Simulate legitimate chain data
        const chainData = this.generateChainData('legitimate');
        const chainHTML = chainData.map(block => this.createChainBlock(block, 'legitimate')).join('');
        container.innerHTML = chainHTML;
    }

    renderAttackChain() {
        const container = document.getElementById('attack-chain');
        if (!container) return;

        // Simulate attack chain data
        const chainData = this.generateChainData('attack');
        const chainHTML = chainData.map(block => this.createChainBlock(block, 'attack')).join('');
        container.innerHTML = chainHTML;
    }

    generateChainData(type) {
        const baseLength = 5;
        const attackLength = this.isRunning ? Math.floor(this.simulationData.attackProgress / 20) : 0;
        
        const length = type === 'attack' ? attackLength : baseLength;
        const blocks = [];

        for (let i = 0; i < length; i++) {
            blocks.push({
                index: i,
                hash: `hash_${type}_${i}`,
                timestamp: Date.now() - (length - i) * 60000,
                transactions: Math.floor(Math.random() * 10) + 1,
                difficulty: 4
            });
        }

        return blocks;
    }

    createChainBlock(block, type) {
        const timestamp = new Date(block.timestamp).toLocaleString();
        const hash = Utils.formatHash(block.hash);

        return `
            <div class="chain-block ${type}">
                <div class="block-header">
                    <span class="block-index">Block #${block.index}</span>
                    <span class="block-type ${type}">${type.toUpperCase()}</span>
                </div>
                <div class="block-content">
                    <div class="block-hash">${hash}</div>
                    <div class="block-time">${timestamp}</div>
                    <div class="block-transactions">${block.transactions} transactions</div>
                </div>
            </div>
        `;
    }

    async startSimulation() {
        if (this.isRunning) {
            Utils.showNotification('Simulation is already running', 'warning');
            return;
        }

        try {
            const startBtn = document.getElementById('start-simulation');
            if (startBtn) {
                startBtn.disabled = true;
                startBtn.innerHTML = '<span class="btn-icon">⏳</span> Starting...';
            }

            const response = await fetch('/api/simulation/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    scenario: this.simulationData.attackType,
                    attack_power: this.simulationData.attackPower,
                    duration: this.simulationData.attackDuration,
                    network_size: this.simulationData.networkSize
                })
            });

            const result = await response.json();

            if (result.success) {
                this.isRunning = true;
                this.simulationData.attackProgress = 0;
                this.updateSimulationDisplay();
                this.updateSimulationControls();
                this.startAttackProgress();
                Utils.showNotification('Attack simulation started!', 'success');
            } else {
                Utils.showNotification(result.error || 'Failed to start simulation', 'error');
            }
        } catch (error) {
            console.error('Error starting simulation:', error);
            Utils.showNotification('Network error occurred', 'error');
        } finally {
            const startBtn = document.getElementById('start-simulation');
            if (startBtn) {
                startBtn.disabled = false;
                startBtn.innerHTML = '<span class="btn-icon">⚔️</span> Start Attack';
            }
        }
    }

    async stopSimulation() {
        if (!this.isRunning) {
            Utils.showNotification('Simulation is not running', 'warning');
            return;
        }

        try {
            const response = await fetch('/api/simulation/stop', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            const result = await response.json();

            if (result.success) {
                this.isRunning = false;
                this.stopAttackProgress();
                this.updateSimulationDisplay();
                this.updateSimulationControls();
                Utils.showNotification('Attack simulation stopped!', 'success');
            } else {
                Utils.showNotification(result.error || 'Failed to stop simulation', 'error');
            }
        } catch (error) {
            console.error('Error stopping simulation:', error);
            Utils.showNotification('Network error occurred', 'error');
        }
    }

    resetSimulation() {
        this.isRunning = false;
        this.simulationData.attackProgress = 0;
        this.stopAttackProgress();
        this.updateSimulationDisplay();
        this.updateSimulationControls();
        Utils.showNotification('Simulation reset successfully!', 'success');
    }

    updateSimulationControls() {
        const startBtn = document.getElementById('start-simulation');
        const stopBtn = document.getElementById('stop-simulation');
        const resetBtn = document.getElementById('reset-simulation');

        if (startBtn) {
            startBtn.disabled = this.isRunning;
        }

        if (stopBtn) {
            stopBtn.disabled = !this.isRunning;
        }

        if (resetBtn) {
            resetBtn.disabled = this.isRunning;
        }
    }

    startAttackProgress() {
        this.simulationInterval = setInterval(() => {
            this.simulationData.attackProgress += Math.random() * 5;
            if (this.simulationData.attackProgress > 100) {
                this.simulationData.attackProgress = 100;
                this.stopSimulation();
            }
            
            this.updateAttackProgress();
            this.updateChainComparison();
        }, 1000);
    }

    stopAttackProgress() {
        if (this.simulationInterval) {
            clearInterval(this.simulationInterval);
            this.simulationInterval = null;
        }
    }

    updateAttackMetrics() {
        // Update attack success probability
        const successProbability = this.calculateSuccessProbability();
        this.updateStat('attack-success-probability', `${successProbability.toFixed(1)}%`);

        // Update network impact
        const networkImpact = this.calculateNetworkImpact();
        this.updateStat('network-impact', `${networkImpact.toFixed(1)}%`);

        // Update time to success
        const timeToSuccess = this.calculateTimeToSuccess();
        this.updateStat('time-to-success', `${timeToSuccess.toFixed(1)} minutes`);
    }

    calculateSuccessProbability() {
        const baseProbability = this.simulationData.attackPower;
        const networkFactor = this.simulationData.networkSize / 100;
        return Math.min(95, baseProbability * networkFactor);
    }

    calculateNetworkImpact() {
        return this.simulationData.attackProgress * 0.8;
    }

    calculateTimeToSuccess() {
        const baseTime = this.simulationData.attackDuration;
        const powerFactor = (100 - this.simulationData.attackPower) / 100;
        return baseTime * powerFactor;
    }

    updateStat(elementId, value) {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = value;
        }
    }

    startAutoUpdate() {
        this.updateInterval = setInterval(() => {
            this.loadSimulationStatus();
            this.updateAttackMetrics();
        }, 5000); // Update every 5 seconds
    }

    stopAutoUpdate() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
    }

    destroy() {
        this.stopSimulation();
        this.stopAutoUpdate();
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.simulationManager = new SimulationManager();
});
