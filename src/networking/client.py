"""
BlockchainClient for BlockyHomework blockchain system.
HTTP client for node communication.
"""

import requests
import json
import time
import logging
from typing import Dict, Any, Optional, List, Tuple
from urllib.parse import urljoin, urlparse
import threading
from datetime import datetime

# Import constants
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from config.constants import CONNECTION_TIMEOUT, DEFAULT_PORT, API_BASE


class BlockchainClient:
    """
    HTTP client for blockchain node communication.
    Handles requests to other blockchain nodes with retry mechanisms.
    """
    
    def __init__(self, node_url: str = None, timeout: int = CONNECTION_TIMEOUT):
        """Initialize the blockchain client."""
        self.node_url = node_url
        self.timeout = timeout / 1000  # Convert to seconds
        self.session = requests.Session()
        
        # Configure logging
        self.logger = logging.getLogger(__name__)
        
        # Connection state
        self.is_connected = False
        self.last_response_time = None
        self.connection_errors = 0
        self.max_retries = 3
        self.retry_delay = 1.0  # seconds
        
        # Request headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'BlockyHomework-Client/1.0.0'
        })
    
    def connect(self, node_url: str) -> bool:
        """Connect to a blockchain node."""
        try:
            self.node_url = node_url
            
            # Test connection with health check
            response = self._make_request('GET', '/api/health')
            
            if response and response.get('success'):
                self.is_connected = True
                self.connection_errors = 0
                self.logger.info(f"Successfully connected to node: {node_url}")
                return True
            else:
                self.is_connected = False
                self.logger.error(f"Failed to connect to node: {node_url}")
                return False
                
        except Exception as e:
            self.is_connected = False
            self.logger.error(f"Connection error to {node_url}: {str(e)}")
            return False
    
    def disconnect(self):
        """Disconnect from the current node."""
        self.is_connected = False
        self.node_url = None
        self.logger.info("Disconnected from node")
    
    def _make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None) -> Optional[Dict[str, Any]]:
        """Make HTTP request with retry mechanism."""
        if not self.node_url:
            self.logger.error("No node URL configured")
            return None
        
        url = urljoin(self.node_url, endpoint)
        
        for attempt in range(self.max_retries + 1):
            try:
                start_time = time.time()
                
                # Make the request
                if method.upper() == 'GET':
                    response = self.session.get(url, params=params, timeout=self.timeout)
                elif method.upper() == 'POST':
                    response = self.session.post(url, json=data, timeout=self.timeout)
                elif method.upper() == 'PUT':
                    response = self.session.put(url, json=data, timeout=self.timeout)
                elif method.upper() == 'DELETE':
                    response = self.session.delete(url, timeout=self.timeout)
                else:
                    self.logger.error(f"Unsupported HTTP method: {method}")
                    return None
                
                # Calculate response time
                self.last_response_time = time.time() - start_time
                
                # Check response status
                if response.status_code == 200:
                    self.connection_errors = 0
                    try:
                        return response.json()
                    except json.JSONDecodeError:
                        self.logger.error(f"Invalid JSON response from {url}")
                        return None
                else:
                    self.logger.warning(f"HTTP {response.status_code} from {url}: {response.text}")
                    if attempt < self.max_retries:
                        time.sleep(self.retry_delay * (attempt + 1))
                        continue
                    return None
                    
            except requests.exceptions.Timeout:
                self.connection_errors += 1
                self.logger.warning(f"Request timeout to {url} (attempt {attempt + 1})")
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay * (attempt + 1))
                    continue
                
            except requests.exceptions.ConnectionError:
                self.connection_errors += 1
                self.logger.warning(f"Connection error to {url} (attempt {attempt + 1})")
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay * (attempt + 1))
                    continue
                    
            except Exception as e:
                self.connection_errors += 1
                self.logger.error(f"Unexpected error requesting {url}: {str(e)}")
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay * (attempt + 1))
                    continue
        
        # All attempts failed
        self.is_connected = False
        return None
    
    # Blockchain API Methods
    
    def get_blockchain_status(self) -> Optional[Dict[str, Any]]:
        """Get blockchain status from the node."""
        return self._make_request('GET', '/api/blockchain/status')
    
    def get_full_chain(self) -> Optional[Dict[str, Any]]:
        """Get the complete blockchain from the node."""
        return self._make_request('GET', '/api/chain')
    
    def validate_chain(self) -> Optional[Dict[str, Any]]:
        """Validate the blockchain on the node."""
        return self._make_request('GET', '/api/chain/validate')
    
    def create_transaction(self, sender: str, recipient: str, amount: float) -> Optional[Dict[str, Any]]:
        """Create a new transaction on the node."""
        data = {
            'sender': sender,
            'recipient': recipient,
            'amount': amount
        }
        return self._make_request('POST', '/api/transactions/create', data=data)
    
    def get_pending_transactions(self) -> Optional[Dict[str, Any]]:
        """Get pending transactions from the node."""
        return self._make_request('GET', '/api/transactions/pending')
    
    def get_transaction_history(self, address: str) -> Optional[Dict[str, Any]]:
        """Get transaction history for an address."""
        params = {'address': address}
        return self._make_request('GET', '/api/transactions/history', params=params)
    
    def get_mining_status(self) -> Optional[Dict[str, Any]]:
        """Get mining status from the node."""
        return self._make_request('GET', '/api/mining/status')
    
    def start_mining(self) -> Optional[Dict[str, Any]]:
        """Start mining on the node."""
        return self._make_request('POST', '/api/mining/start')
    
    def stop_mining(self) -> Optional[Dict[str, Any]]:
        """Stop mining on the node."""
        return self._make_request('POST', '/api/mining/stop')
    
    def mine_block(self) -> Optional[Dict[str, Any]]:
        """Mine a single block on the node."""
        return self._make_request('POST', '/api/mining/mine-block')
    
    def get_wallet_balance(self, address: str) -> Optional[Dict[str, Any]]:
        """Get wallet balance from the node."""
        params = {'address': address}
        return self._make_request('GET', '/api/wallet/balance', params=params)
    
    def create_wallet(self) -> Optional[Dict[str, Any]]:
        """Create a new wallet on the node."""
        return self._make_request('POST', '/api/wallet/create')
    
    def get_network_status(self) -> Optional[Dict[str, Any]]:
        """Get network status from the node."""
        return self._make_request('GET', '/api/network/status')
    
    def register_node(self, node_url: str) -> Optional[Dict[str, Any]]:
        """Register a node with the target node."""
        data = {'node_url': node_url}
        return self._make_request('POST', '/api/nodes/register', data=data)
    
    def get_nodes(self) -> Optional[Dict[str, Any]]:
        """Get list of connected nodes."""
        return self._make_request('GET', '/api/nodes/list')
    
    def consensus_resolve(self) -> Optional[Dict[str, Any]]:
        """Resolve consensus conflicts with the node."""
        return self._make_request('GET', '/api/consensus')
    
    def health_check(self) -> Optional[Dict[str, Any]]:
        """Perform health check on the node."""
        return self._make_request('GET', '/api/health')
    
    def get_server_info(self) -> Optional[Dict[str, Any]]:
        """Get server information from the node."""
        return self._make_request('GET', '/api/info')
    
    # Node Discovery Methods
    
    def discover_nodes(self, initial_nodes: List[str] = None) -> List[str]:
        """Discover nodes in the network."""
        discovered_nodes = set()
        nodes_to_check = set(initial_nodes or [])
        checked_nodes = set()
        
        while nodes_to_check:
            node_url = nodes_to_check.pop()
            if node_url in checked_nodes:
                continue
            
            checked_nodes.add(node_url)
            
            # Try to connect to the node
            if self.connect(node_url):
                discovered_nodes.add(node_url)
                
                # Get nodes from this node
                nodes_response = self.get_nodes()
                if nodes_response and nodes_response.get('success'):
                    node_list = nodes_response.get('data', {}).get('nodes', [])
                    for discovered_node in node_list:
                        if discovered_node not in checked_nodes:
                            nodes_to_check.add(discovered_node)
        
        return list(discovered_nodes)
    
    def ping_node(self, node_url: str) -> Tuple[bool, float]:
        """Ping a node to check connectivity and response time."""
        try:
            original_url = self.node_url
            start_time = time.time()
            
            # Temporarily connect to the node
            if self.connect(node_url):
                response_time = time.time() - start_time
                
                # Restore original connection
                if original_url:
                    self.connect(original_url)
                else:
                    self.disconnect()
                
                return True, response_time
            else:
                return False, 0.0
                
        except Exception as e:
            self.logger.error(f"Error pinging node {node_url}: {str(e)}")
            return False, 0.0
    
    def find_fastest_node(self, node_urls: List[str]) -> Optional[str]:
        """Find the fastest responding node from a list."""
        fastest_node = None
        fastest_time = float('inf')
        
        for node_url in node_urls:
            is_reachable, response_time = self.ping_node(node_url)
            if is_reachable and response_time < fastest_time:
                fastest_time = response_time
                fastest_node = node_url
        
        return fastest_node
    
    # Connection Management
    
    def get_connection_status(self) -> Dict[str, Any]:
        """Get current connection status."""
        return {
            'is_connected': self.is_connected,
            'node_url': self.node_url,
            'connection_errors': self.connection_errors,
            'last_response_time': self.last_response_time,
            'timestamp': datetime.now().isoformat()
        }
    
    def set_timeout(self, timeout_ms: int):
        """Set request timeout."""
        self.timeout = timeout_ms / 1000
    
    def set_retry_policy(self, max_retries: int, retry_delay: float):
        """Set retry policy for failed requests."""
        self.max_retries = max_retries
        self.retry_delay = retry_delay
    
    def close(self):
        """Close the client session."""
        if self.session:
            self.session.close()
        self.disconnect()


class NodeDiscovery:
    """Advanced node discovery mechanisms."""
    
    def __init__(self, client: BlockchainClient):
        """Initialize node discovery."""
        self.client = client
        self.logger = logging.getLogger(__name__)
        self.known_nodes = set()
        self.active_nodes = set()
        self.discovery_thread = None
        self.discovery_active = False
    
    def add_seed_nodes(self, seed_nodes: List[str]):
        """Add seed nodes for discovery."""
        self.known_nodes.update(seed_nodes)
    
    def start_discovery(self, interval: int = 30):
        """Start continuous node discovery."""
        if self.discovery_active:
            return
        
        self.discovery_active = True
        self.discovery_thread = threading.Thread(
            target=self._discovery_loop,
            args=(interval,)
        )
        self.discovery_thread.start()
        self.logger.info("Started node discovery")
    
    def stop_discovery(self):
        """Stop continuous node discovery."""
        self.discovery_active = False
        if self.discovery_thread:
            self.discovery_thread.join(timeout=5)
        self.logger.info("Stopped node discovery")
    
    def _discovery_loop(self, interval: int):
        """Main discovery loop."""
        while self.discovery_active:
            try:
                # Discover new nodes
                discovered = self.client.discover_nodes(list(self.known_nodes))
                
                # Update known nodes
                self.known_nodes.update(discovered)
                
                # Test active nodes
                self._update_active_nodes()
                
                self.logger.info(f"Discovery cycle complete. Known: {len(self.known_nodes)}, Active: {len(self.active_nodes)}")
                
                # Wait for next cycle
                time.sleep(interval)
                
            except Exception as e:
                self.logger.error(f"Error in discovery loop: {str(e)}")
                time.sleep(interval)
    
    def _update_active_nodes(self):
        """Update the list of active nodes."""
        active = set()
        
        for node_url in self.known_nodes:
            is_reachable, _ = self.client.ping_node(node_url)
            if is_reachable:
                active.add(node_url)
        
        self.active_nodes = active
    
    def get_active_nodes(self) -> List[str]:
        """Get list of currently active nodes."""
        return list(self.active_nodes)
    
    def get_best_node(self) -> Optional[str]:
        """Get the best (fastest) active node."""
        if not self.active_nodes:
            return None
        
        return self.client.find_fastest_node(list(self.active_nodes))


# Utility functions
def create_client(node_url: str = None) -> BlockchainClient:
    """Create a new BlockchainClient instance."""
    client = BlockchainClient()
    if node_url:
        client.connect(node_url)
    return client


def test_node_connectivity(node_urls: List[str]) -> Dict[str, Dict[str, Any]]:
    """Test connectivity to multiple nodes."""
    client = BlockchainClient()
    results = {}
    
    for node_url in node_urls:
        is_reachable, response_time = client.ping_node(node_url)
        results[node_url] = {
            'reachable': is_reachable,
            'response_time': response_time,
            'timestamp': datetime.now().isoformat()
        }
    
    client.close()
    return results


# Example usage
if __name__ == "__main__":
    # Example: Create client and connect to a node
    client = create_client()
    
    # Connect to a node
    if client.connect("http://localhost:5000"):
        print("Connected successfully!")
        
        # Get blockchain status
        status = client.get_blockchain_status()
        print(f"Blockchain status: {status}")
        
        # Get network status
        network = client.get_network_status()
        print(f"Network status: {network}")
        
    client.close()
