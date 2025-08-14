# BlockyHomework API Reference

## Overview

BlockyHomework provides a comprehensive REST API for interacting with the blockchain system. All API endpoints return JSON responses and use standard HTTP status codes.

## Base URL

```
http://localhost:5000
```

## Authentication

Currently, the API does not require authentication. All endpoints are publicly accessible.

## Response Format

All API responses follow this standard format:

### Success Response
```json
{
  "success": true,
  "data": { ... },
  "message": "Operation completed successfully"
}
```

### Error Response
```json
{
  "success": false,
  "error": "Error description",
  "code": "ERROR_CODE"
}
```

## Blockchain Endpoints

### Get Blockchain Status

**GET** `/api/blockchain/status`

Returns the current status of the blockchain.

**Response:**
```json
{
  "chain_length": 5,
  "difficulty": 4,
  "pending_transactions": 3,
  "block_reward": 10.0,
  "is_valid": true
}
```

### Get Full Blockchain

**GET** `/api/blockchain/chain`

Returns the complete blockchain data.

**Response:**
```json
{
  "chain": [
    {
      "index": 0,
      "timestamp": 1640995200.0,
      "transactions": [...],
      "proof": 100,
      "previous_hash": "0000000000000000000000000000000000000000000000000000000000000000",
      "hash": "abc123..."
    }
  ],
  "length": 5
}
```

### Get Block by Index

**GET** `/api/blockchain/block/{index}`

Returns a specific block by its index.

**Parameters:**
- `index` (integer): Block index

**Response:**
```json
{
  "index": 1,
  "timestamp": 1640995260.0,
  "transactions": [...],
  "proof": 12345,
  "previous_hash": "abc123...",
  "hash": "def456..."
}
```

### Get Block by Hash

**GET** `/api/blockchain/block/hash/{block_hash}`

Returns a specific block by its hash.

**Parameters:**
- `block_hash` (string): Block hash

**Response:** Same as Get Block by Index

## Wallet Endpoints

### Get Wallet Balance

**GET** `/api/wallet/balance`

Returns the current wallet balance and address.

**Response:**
```json
{
  "address": "abc123...",
  "balance": "25.500 ZTL Coin",
  "balance_numeric": 25.5
}
```

### Get Wallet Address

**GET** `/api/wallet/address`

Returns the wallet address and public key.

**Response:**
```json
{
  "address": "abc123...",
  "public_key": "def456..."
}
```

### Get Wallet History

**GET** `/api/wallet/history`

Returns the transaction history for the wallet.

**Response:**
```json
{
  "transactions": [
    {
      "sender": "abc123...",
      "recipient": "def456...",
      "amount": 10.0,
      "timestamp": 1640995200.0,
      "hash": "ghi789..."
    }
  ],
  "count": 5
}
```

## Transaction Endpoints

### Create Transaction

**POST** `/api/transactions/create`

Creates a new transaction.

**Request Body:**
```json
{
  "recipient": "def456...",
  "amount": 25.5
}
```

**Response:**
```json
{
  "success": true,
  "transaction": {
    "sender": "abc123...",
    "recipient": "def456...",
    "amount": 25.5,
    "timestamp": 1640995200.0,
    "hash": "ghi789...",
    "signature": "jkl012..."
  },
  "message": "Transaction created successfully"
}
```

### Get Pending Transactions

**GET** `/api/transactions/pending`

Returns all pending transactions in the mempool.

**Response:**
```json
{
  "transactions": [
    {
      "sender": "abc123...",
      "recipient": "def456...",
      "amount": 10.0,
      "timestamp": 1640995200.0,
      "hash": "ghi789..."
    }
  ],
  "count": 3
}
```

### Get Transaction by Hash

**GET** `/api/transactions/{transaction_hash}`

Returns a specific transaction by its hash.

**Parameters:**
- `transaction_hash` (string): Transaction hash

**Response:**
```json
{
  "transaction": {
    "sender": "abc123...",
    "recipient": "def456...",
    "amount": 10.0,
    "timestamp": 1640995200.0,
    "hash": "ghi789...",
    "signature": "jkl012..."
  },
  "status": "confirmed"
}
```

## Mining Endpoints

### Get Mining Status

**GET** `/api/mining/status`

Returns the current mining status.

**Response:**
```json
{
  "is_mining": false,
  "difficulty": 4,
  "block_reward": 10.0,
  "chain_length": 5
}
```

### Start Mining

**POST** `/api/mining/start`

Starts the mining process.

**Response:**
```json
{
  "success": true,
  "message": "Mining started successfully"
}
```

### Stop Mining

**POST** `/api/mining/stop`

Stops the mining process.

**Response:**
```json
{
  "success": true,
  "message": "Mining stopped successfully"
}
```

### Mine Single Block

**POST** `/api/mining/mine-block`

Mines a single block with pending transactions.

**Response:**
```json
{
  "success": true,
  "block": {
    "index": 6,
    "timestamp": 1640995320.0,
    "transactions": [...],
    "proof": 54321,
    "previous_hash": "def456...",
    "hash": "ghi789..."
  },
  "message": "Block #6 mined successfully"
}
```

## Network Endpoints

### Get Network Status

**GET** `/api/network/status`

Returns the current network status.

**Response:**
```json
{
  "connected_nodes": 3,
  "total_peers": 5,
  "network_status": "connected",
  "node_id": "node_abc123",
  "port": 5000
}
```

### Get Connected Peers

**GET** `/api/network/peers`

Returns information about connected peers.

**Response:**
```json
{
  "peers": [
    {
      "node_id": "node_def456",
      "address": "192.168.1.100:5001",
      "version": "v1.0.0",
      "latency": 15,
      "block_count": 5
    }
  ],
  "count": 3
}
```

### Connect to Peer

**POST** `/api/network/connect`

Connects to a specific peer.

**Request Body:**
```json
{
  "address": "192.168.1.100:5001"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Connected to 192.168.1.100:5001"
}
```

## Simulation Endpoints

### Get Simulation Status

**GET** `/api/simulation/status`

Returns the current simulation status.

**Response:**
```json
{
  "is_running": false,
  "current_scenario": null,
  "attack_progress": 0
}
```

### Start Simulation

**POST** `/api/simulation/start`

Starts an attack simulation.

**Request Body:**
```json
{
  "scenario": "51_percent",
  "attack_power": 60,
  "duration": 10,
  "network_size": 100
}
```

**Response:**
```json
{
  "success": true,
  "message": "Simulation 51_percent started"
}
```

### Stop Simulation

**POST** `/api/simulation/stop`

Stops the current simulation.

**Response:**
```json
{
  "success": true,
  "message": "Simulation stopped"
}
```

## Error Codes

| Code | Description |
|------|-------------|
| 400 | Bad Request - Invalid parameters |
| 404 | Not Found - Resource not found |
| 500 | Internal Server Error - Server error |

## Rate Limiting

Currently, there are no rate limits implemented. However, it's recommended to:

- Limit requests to 100 requests per minute per client
- Implement exponential backoff for failed requests
- Cache responses when appropriate

## WebSocket Events (Future)

The following WebSocket events are planned for real-time updates:

- `blockchain_update` - New block mined
- `transaction_created` - New transaction created
- `mining_status` - Mining status changes
- `network_update` - Network topology changes
- `simulation_progress` - Attack simulation progress

## SDK Examples

### Python SDK Example

```python
import requests

class BlockyHomeworkClient:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
    
    def get_blockchain_status(self):
        response = requests.get(f"{self.base_url}/api/blockchain/status")
        return response.json()
    
    def create_transaction(self, recipient, amount):
        data = {"recipient": recipient, "amount": amount}
        response = requests.post(f"{self.base_url}/api/transactions/create", json=data)
        return response.json()
    
    def mine_block(self):
        response = requests.post(f"{self.base_url}/api/mining/mine-block")
        return response.json()

# Usage
client = BlockyHomeworkClient()
status = client.get_blockchain_status()
print(f"Chain length: {status['chain_length']}")
```

### JavaScript SDK Example

```javascript
class BlockyHomeworkClient {
    constructor(baseUrl = 'http://localhost:5000') {
        this.baseUrl = baseUrl;
    }
    
    async getBlockchainStatus() {
        const response = await fetch(`${this.baseUrl}/api/blockchain/status`);
        return await response.json();
    }
    
    async createTransaction(recipient, amount) {
        const response = await fetch(`${this.baseUrl}/api/transactions/create`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ recipient, amount })
        });
        return await response.json();
    }
    
    async mineBlock() {
        const response = await fetch(`${this.baseUrl}/api/mining/mine-block`, {
            method: 'POST'
        });
        return await response.json();
    }
}

// Usage
const client = new BlockyHomeworkClient();
client.getBlockchainStatus().then(status => {
    console.log(`Chain length: ${status.chain_length}`);
});
```

## Testing

You can test the API using curl:

```bash
# Get blockchain status
curl http://localhost:5000/api/blockchain/status

# Create a transaction
curl -X POST http://localhost:5000/api/transactions/create \
  -H "Content-Type: application/json" \
  -d '{"recipient": "def456...", "amount": 25.5}'

# Mine a block
curl -X POST http://localhost:5000/api/mining/mine-block
```

## Versioning

The API version is included in the URL path. Current version is v1:

```
http://localhost:5000/api/v1/blockchain/status
```

## Changelog

### v1.0.0 (Current)
- Initial API release
- Basic blockchain operations
- Wallet management
- Transaction creation and management
- Mining operations
- Network management
- Attack simulation
