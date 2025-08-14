/**
 * NETWORK PAGE - JAVASCRIPT MODULE
 * Handles P2P network management and visualization
 */

class NetworkManager {
    constructor() {
        this.networkData = {
            connectedNodes: 0,
            totalPeers: 0,
            networkStatus: 'disconnected',
            syncProgress: 0,
            peers: []
        };
        this.updateInterval = null;
        this.networkCanvas = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadNetworkData();
        this.startAutoUpdate();
        this.initNetworkVisualization();
    }

    setupEventListeners() {
        // Network action buttons
        const refreshBtn = document.getElementById('refresh-network');
        const discoverBtn = document.getElementById('discover-nodes');
        const syncBtn = document.getElementById('sync-chain');

        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.refreshNetwork());
        }

        if (discoverBtn) {
            discoverBtn.addEventListener('click', () => this.discoverNodes());
        }

        if (syncBtn) {
            syncBtn.addEventListener('click', () => this.syncChain());
        }

        // Peer connection form
        const connectForm = document.getElementById('connect-peer-form');
        if (connectForm) {
            connectForm.addEventListener('submit', (e) => this.handlePeerConnection(e));
        }
    }

    async loadNetworkData() {
        try {
            const [statusResponse, peersResponse] = await Promise.all([
                fetch('/api/network/status'),
                fetch('/api/network/peers')
            ]);

            const statusData = await statusResponse.json();
            const peersData = await peersResponse.json();

            this.networkData = {
                connectedNodes: statusData.connected_nodes || 0,
                totalPeers: statusData.total_peers || 0,
                networkStatus: statusData.network_status || 'disconnected',
                syncProgress: statusData.sync_progress || 0,
                peers: peersData.peers || []
            };

            this.updateNetworkDisplay();
        } catch (error) {
            console.error('Error loading network data:', error);
        }
    }

    updateNetworkDisplay() {
        // Update statistics
        this.updateStat('connected-nodes', this.networkData.connectedNodes);
        this.updateStat('total-peers', this.networkData.totalPeers);

        // Update network status
        this.updateNetworkStatus();

        // Update sync progress
        this.updateSyncProgress();

        // Update peer list
        this.renderPeerList();

        // Update network visualization
        this.updateNetworkVisualization();
    }

    updateNetworkStatus() {
        const statusDot = document.getElementById('network-status-dot');
        const statusText = document.getElementById('network-status-text');

        if (statusDot && statusText) {
            statusDot.className = `status-dot ${this.networkData.networkStatus}`;
            statusText.textContent = this.networkData.networkStatus.charAt(0).toUpperCase() + 
                                   this.networkData.networkStatus.slice(1);
        }
    }

    updateSyncProgress() {
        const progressBar = document.getElementById('sync-progress-bar');
        const progressText = document.getElementById('sync-progress-text');

        if (progressBar) {
            progressBar.style.width = `${this.networkData.syncProgress}%`;
        }

        if (progressText) {
            progressText.textContent = `${Math.round(this.networkData.syncProgress)}%`;
        }
    }

    renderPeerList() {
        const container = document.getElementById('network-nodes');
        if (!container) return;

        if (this.networkData.peers.length === 0) {
            container.innerHTML = '<p class="no-data">No connected peers</p>';
            return;
        }

        const peersHTML = this.networkData.peers.map(peer => this.createPeerCard(peer)).join('');
        container.innerHTML = peersHTML;
    }

    createPeerCard(peer) {
        return `
            <div class="peer-card">
                <div class="peer-header">
                    <span class="peer-id">${peer.node_id || 'Unknown'}</span>
                    <span class="peer-status connected">Connected</span>
                </div>
                <div class="peer-details">
                    <div class="peer-info">
                        <span class="peer-address">${peer.address || 'N/A'}</span>
                        <span class="peer-version">v1.0.0</span>
                    </div>
                    <div class="peer-stats">
                        <span class="peer-latency">Latency: ${peer.latency || 'N/A'}ms</span>
                        <span class="peer-blocks">Blocks: ${peer.block_count || 0}</span>
                    </div>
                </div>
            </div>
        `;
    }

    initNetworkVisualization() {
        const canvas = document.getElementById('network-canvas');
        if (!canvas) return;

        // Create a simple network visualization
        this.networkCanvas = canvas;
        this.updateNetworkVisualization();
    }

    updateNetworkVisualization() {
        if (!this.networkCanvas) return;

        // Simple network topology visualization
        const nodes = this.networkData.peers.length + 1; // +1 for current node
        const centerX = this.networkCanvas.offsetWidth / 2;
        const centerY = this.networkCanvas.offsetHeight / 2;
        const radius = Math.min(centerX, centerY) * 0.6;

        let visualizationHTML = `
            <div class="network-topology">
                <div class="node center-node" style="left: ${centerX}px; top: ${centerY}px;">
                    <div class="node-dot current"></div>
                    <div class="node-label">This Node</div>
                </div>
        `;

        // Add peer nodes
        this.networkData.peers.forEach((peer, index) => {
            const angle = (index / this.networkData.peers.length) * 2 * Math.PI;
            const x = centerX + radius * Math.cos(angle);
            const y = centerY + radius * Math.sin(angle);

            visualizationHTML += `
                <div class="node peer-node" style="left: ${x}px; top: ${y}px;">
                    <div class="node-dot peer"></div>
                    <div class="node-label">${peer.node_id || `Peer ${index + 1}`}</div>
                </div>
            `;
        });

        visualizationHTML += '</div>';
        this.networkCanvas.innerHTML = visualizationHTML;
    }

    async refreshNetwork() {
        try {
            const refreshBtn = document.getElementById('refresh-network');
            if (refreshBtn) {
                refreshBtn.disabled = true;
                refreshBtn.innerHTML = '<span class="btn-icon">⏳</span> Refreshing...';
            }

            await this.loadNetworkData();
            Utils.showNotification('Network refreshed successfully!', 'success');
        } catch (error) {
            console.error('Error refreshing network:', error);
            Utils.showNotification('Failed to refresh network', 'error');
        } finally {
            const refreshBtn = document.getElementById('refresh-network');
            if (refreshBtn) {
                refreshBtn.disabled = false;
                refreshBtn.innerHTML = '<span class="btn-icon">🔄</span> Refresh Network';
            }
        }
    }

    async discoverNodes() {
        try {
            const discoverBtn = document.getElementById('discover-nodes');
            if (discoverBtn) {
                discoverBtn.disabled = true;
                discoverBtn.innerHTML = '<span class="btn-icon">⏳</span> Discovering...';
            }

            // Simulate node discovery
            await new Promise(resolve => setTimeout(resolve, 2000));
            
            Utils.showNotification('Node discovery completed!', 'success');
        } catch (error) {
            console.error('Error discovering nodes:', error);
            Utils.showNotification('Failed to discover nodes', 'error');
        } finally {
            const discoverBtn = document.getElementById('discover-nodes');
            if (discoverBtn) {
                discoverBtn.disabled = false;
                discoverBtn.innerHTML = '<span class="btn-icon">🔍</span> Discover Nodes';
            }
        }
    }

    async syncChain() {
        try {
            const syncBtn = document.getElementById('sync-chain');
            if (syncBtn) {
                syncBtn.disabled = true;
                syncBtn.innerHTML = '<span class="btn-icon">⏳</span> Syncing...';
            }

            // Simulate chain synchronization
            let progress = 0;
            const syncInterval = setInterval(() => {
                progress += 10;
                this.networkData.syncProgress = progress;
                this.updateSyncProgress();

                if (progress >= 100) {
                    clearInterval(syncInterval);
                    Utils.showNotification('Blockchain synchronized successfully!', 'success');
                }
            }, 200);

        } catch (error) {
            console.error('Error syncing chain:', error);
            Utils.showNotification('Failed to sync blockchain', 'error');
        } finally {
            const syncBtn = document.getElementById('sync-chain');
            if (syncBtn) {
                syncBtn.disabled = false;
                syncBtn.innerHTML = '<span class="btn-icon">📡</span> Sync Blockchain';
            }
        }
    }

    async handlePeerConnection(event) {
        event.preventDefault();
        
        const form = event.target;
        const formData = new FormData(form);
        const peerAddress = formData.get('peer-address');

        if (!peerAddress) {
            Utils.showNotification('Peer address is required', 'error');
            return;
        }

        try {
            const response = await fetch('/api/network/connect', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ address: peerAddress })
            });

            const result = await response.json();

            if (result.success) {
                Utils.showNotification(`Connected to ${peerAddress}`, 'success');
                form.reset();
                this.loadNetworkData(); // Refresh network data
            } else {
                Utils.showNotification(result.error || 'Failed to connect to peer', 'error');
            }
        } catch (error) {
            console.error('Error connecting to peer:', error);
            Utils.showNotification('Network error occurred', 'error');
        }
    }

    updateStat(elementId, value) {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = value;
        }
    }

    startAutoUpdate() {
        this.updateInterval = setInterval(() => {
            this.loadNetworkData();
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
    window.networkManager = new NetworkManager();
});
