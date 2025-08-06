"""
Constants for BlockyHomework blockchain system.
"""

# Blockchain Constants
GENESIS_BLOCK_HASH = "0000000000000000000000000000000000000000000000000000000000000000"
MINING_DIFFICULTY = 4
BLOCK_REWARD = 10.0

# Network Constants
DEFAULT_PORT = 5000
MAX_CONNECTIONS = 10
CONNECTION_TIMEOUT = 5000

# Security Constants
HASH_ALGORITHM = "sha256"
SIGNATURE_ALGORITHM = "ecdsa"

# UI Constants
REFRESH_INTERVAL = 5000
ANIMATION_DURATION = 300

# API Endpoints
API_BASE = "/api"
ENDPOINTS = {
    "blockchain_status": f"{API_BASE}/blockchain/status",
    "wallet_balance": f"{API_BASE}/wallet/balance",
    "mining_status": f"{API_BASE}/mining/status",
    "network_status": f"{API_BASE}/network/status",
    "create_transaction": f"{API_BASE}/transactions/create",
    "start_mining": f"{API_BASE}/mining/start",
    "stop_mining": f"{API_BASE}/mining/stop",
    "mine_block": f"{API_BASE}/mining/mine-block"
} 