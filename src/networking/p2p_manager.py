"""
P2PManager for BlockyHomework blockchain system.
Peer-to-peer network management.
"""

import threading
import time
import logging
import json
from typing import Dict, Any, List, Optional, Set, Callable
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# Import networking components
from .client import BlockchainClient, NodeDiscovery

# Import constants
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from config.constants import DEFAULT_PORT, MAX_CONNECTIONS


class P2PManager:
    """
    Peer-to-peer network manager for blockchain nodes.
    Handles node discovery, communication, and network topology.
    """
    
    def __init__(self, node_id: str = None, port: int = DEFAULT_PORT):
        """Initialize the P2P manager."""
        self.node_id = node_id or self._generate_node_id()
        self.port = port
        self.host = "localhost"
        
        # Configure logging
        self.logger = logging.getLogger(__name__)
        
        # Network state
        self.is_running = False
        self.peers = {}  # node_id -> peer_info
        self.connected_peers = set()
        self.blacklisted_peers = set()
        
        # Network components
        self.client = BlockchainClient()
        self.discovery = NodeDiscovery(self.client)
        
        # Threading
        self.executor = ThreadPoolExecutor(max_workers=MAX_CONNECTIONS)
        self.management_thread = None
        self.heartbeat_thread = None
        
        # Event callbacks
        self.on_peer_connected = None
        self.on_peer_disconnected = None
        self.on_message_received = None
        
        # Network statistics
        self.stats = {
            'messages_sent': 0,
            'messages_received': 0,
            'connections_made': 0,
            'connections_lost': 0,
            'start_time': None
        }
    
    def _generate_node_id(self) -> str:
        """Generate a unique node ID."""
        import uuid
        return f"node_{uuid.uuid4().hex[:8]}"
    
    def start(self, seed_nodes: List[str] = None):
        """Start the P2P network manager."""
        if self.is_running:
            self.logger.warning("P2P manager is already running")
            return
        
        try:
            self.is_running = True
            self.stats['start_time'] = time.time()
            
            # Initialize discovery with seed nodes
            if seed_nodes:
                self.discovery.add_seed_nodes(seed_nodes)
            
            # Start network management threads
            self._start_management_threads()
            
            # Start node discovery
            self.discovery.start_discovery(interval=30)
            
            self.logger.info(f"P2P Manager started for node {self.node_id} on port {self.port}")
            
        except Exception as e:
            self.logger.error(f"Error starting P2P manager: {str(e)}")
            self.is_running = False
            raise
    
    def stop(self):
        """Stop the P2P network manager."""
        if not self.is_running:
            return
        
        try:
            self.is_running = False
            
            # Stop discovery
            self.discovery.stop_discovery()
            
            # Disconnect from all peers
            self._disconnect_all_peers()
            
            # Stop threads
            if self.management_thread:
                self.management_thread.join(timeout=5)
            
            if self.heartbeat_thread:
                self.heartbeat_thread.join(timeout=5)
            
            # Shutdown executor
            self.executor.shutdown(wait=True)
            
            self.logger.info(f"P2P Manager stopped for node {self.node_id}")
            
        except Exception as e:
            self.logger.error(f"Error stopping P2P manager: {str(e)}")
    
    def _start_management_threads(self):
        """Start background management threads."""
        # Network management thread
        self.management_thread = threading.Thread(target=self._network_management_loop)
        self.management_thread.start()
        
        # Heartbeat thread
        self.heartbeat_thread = threading.Thread(target=self._heartbeat_loop)
        self.heartbeat_thread.start()
    
    def _network_management_loop(self):
        """Main network management loop."""
        while self.is_running:
            try:
                # Get active nodes from discovery
                active_nodes = self.discovery.get_active_nodes()
                
                # Connect to new peers
                self._connect_to_new_peers(active_nodes)
                
                # Clean up dead connections
                self._cleanup_dead_connections()
                
                # Update network topology
                self._update_network_topology()
                
                # Sleep before next cycle
                time.sleep(10)
                
            except Exception as e:
                self.logger.error(f"Error in network management loop: {str(e)}")
                time.sleep(10)
    
    def _heartbeat_loop(self):
        """Heartbeat loop to maintain connections."""
        while self.is_running:
            try:
                # Send heartbeat to all connected peers
                self._send_heartbeat_to_peers()
                
                # Sleep before next heartbeat
                time.sleep(30)
                
            except Exception as e:
                self.logger.error(f"Error in heartbeat loop: {str(e)}")
                time.sleep(30)
    
    def _connect_to_new_peers(self, active_nodes: List[str]):
        """Connect to new peers."""
        for node_url in active_nodes:
            if len(self.connected_peers) >= MAX_CONNECTIONS:
                break
            
            # Skip if already connected or blacklisted
            node_id = self._extract_node_id(node_url)
            if node_id in self.connected_peers or node_id in self.blacklisted_peers:
                continue
            
            # Try to connect
            self._connect_to_peer(node_url)
    
    def _connect_to_peer(self, node_url: str) -> bool:
        """Connect to a specific peer."""
        try:
            # Test connection
            is_reachable, response_time = self.client.ping_node(node_url)
            
            if is_reachable:
                # Get node info
                if self.client.connect(node_url):
                    server_info = self.client.get_server_info()
                    
                    if server_info and server_info.get('success'):
                        node_data = server_info.get('data', {})
                        node_id = node_data.get('server_name', self._extract_node_id(node_url))
                        
                        # Add peer
                        peer_info = {
                            'node_id': node_id,
                            'url': node_url,
                            'host': self._extract_host(node_url),
                            'port': self._extract_port(node_url),
                            'response_time': response_time,
                            'connected_at': time.time(),
                            'last_heartbeat': time.time(),
                            'status': 'connected'
                        }
                        
                        self.peers[node_id] = peer_info
                        self.connected_peers.add(node_id)
                        
                        # Register ourselves with the peer
                        self.client.register_node(f"http://{self.host}:{self.port}")
                        
                        # Call callback
                        if self.on_peer_connected:
                            self.on_peer_connected(peer_info)
                        
                        self.stats['connections_made'] += 1
                        self.logger.info(f"Connected to peer: {node_id} at {node_url}")
                        
                        return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error connecting to peer {node_url}: {str(e)}")
            return False
    
    def _disconnect_from_peer(self, node_id: str):
        """Disconnect from a specific peer."""
        try:
            if node_id in self.connected_peers:
                peer_info = self.peers.get(node_id)
                
                self.connected_peers.remove(node_id)
                
                if peer_info:
                    # Call callback
                    if self.on_peer_disconnected:
                        self.on_peer_disconnected(peer_info)
                    
                    self.stats['connections_lost'] += 1
                    self.logger.info(f"Disconnected from peer: {node_id}")
                
        except Exception as e:
            self.logger.error(f"Error disconnecting from peer {node_id}: {str(e)}")
    
    def _disconnect_all_peers(self):
        """Disconnect from all peers."""
        for node_id in list(self.connected_peers):
            self._disconnect_from_peer(node_id)
    
    def _cleanup_dead_connections(self):
        """Clean up dead or unresponsive connections."""
        current_time = time.time()
        dead_peers = []
        
        for node_id, peer_info in self.peers.items():
            # Check if peer is responsive
            last_heartbeat = peer_info.get('last_heartbeat', 0)
            if current_time - last_heartbeat > 120:  # 2 minutes timeout
                dead_peers.append(node_id)
        
        # Disconnect dead peers
        for node_id in dead_peers:
            self._disconnect_from_peer(node_id)
            if node_id in self.peers:
                del self.peers[node_id]
    
    def _send_heartbeat_to_peers(self):
        """Send heartbeat to all connected peers."""
        for node_id in list(self.connected_peers):
            try:
                peer_info = self.peers.get(node_id)
                if peer_info:
                    # Send heartbeat
                    if self.client.connect(peer_info['url']):
                        health_response = self.client.health_check()
                        
                        if health_response and health_response.get('success'):
                            peer_info['last_heartbeat'] = time.time()
                            peer_info['status'] = 'connected'
                        else:
                            peer_info['status'] = 'unresponsive'
                    else:
                        peer_info['status'] = 'disconnected'
                        
            except Exception as e:
                self.logger.warning(f"Heartbeat failed for peer {node_id}: {str(e)}")
    
    def _update_network_topology(self):
        """Update network topology information."""
        # Get network status from all connected peers
        for node_id in list(self.connected_peers):
            try:
                peer_info = self.peers.get(node_id)
                if peer_info and peer_info['status'] == 'connected':
                    if self.client.connect(peer_info['url']):
                        network_status = self.client.get_network_status()
                        
                        if network_status and network_status.get('success'):
                            peer_nodes = network_status.get('data', {}).get('connected_nodes', [])
                            peer_info['known_peers'] = peer_nodes
                            
            except Exception as e:
                self.logger.warning(f"Failed to update topology for peer {node_id}: {str(e)}")
    
    # Broadcasting Methods
    
    def broadcast_message(self, message_type: str, data: Dict[str, Any]) -> int:
        """Broadcast a message to all connected peers."""
        message = {
            'type': message_type,
            'data': data,
            'sender': self.node_id,
            'timestamp': datetime.now().isoformat()
        }
        
        successful_broadcasts = 0
        
        for node_id in list(self.connected_peers):
            try:
                if self._send_message_to_peer(node_id, message):
                    successful_broadcasts += 1
                    
            except Exception as e:
                self.logger.error(f"Error broadcasting to peer {node_id}: {str(e)}")
        
        self.stats['messages_sent'] += successful_broadcasts
        return successful_broadcasts
    
    def broadcast_transaction(self, transaction_data: Dict[str, Any]) -> int:
        """Broadcast a new transaction to the network."""
        return self.broadcast_message('new_transaction', transaction_data)
    
    def broadcast_block(self, block_data: Dict[str, Any]) -> int:
        """Broadcast a new block to the network."""
        return self.broadcast_message('new_block', block_data)
    
    def broadcast_chain_update(self, chain_data: Dict[str, Any]) -> int:
        """Broadcast a chain update to the network."""
        return self.broadcast_message('chain_update', chain_data)
    
    def _send_message_to_peer(self, node_id: str, message: Dict[str, Any]) -> bool:
        """Send a message to a specific peer."""
        try:
            peer_info = self.peers.get(node_id)
            if not peer_info or peer_info['status'] != 'connected':
                return False
            
            # For now, we'll use the existing API endpoints to send messages
            message_type = message.get('type')
            data = message.get('data')
            
            if self.client.connect(peer_info['url']):
                if message_type == 'new_transaction':
                    # Send transaction via API
                    response = self.client.create_transaction(
                        sender=data.get('sender'),
                        recipient=data.get('recipient'),
                        amount=data.get('amount')
                    )
                    return response and response.get('success')
                
                elif message_type == 'new_block':
                    # For blocks, we might trigger mining or sync
                    response = self.client.consensus_resolve()
                    return response and response.get('success')
                
                elif message_type == 'chain_update':
                    # Trigger consensus resolution
                    response = self.client.consensus_resolve()
                    return response and response.get('success')
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error sending message to peer {node_id}: {str(e)}")
            return False
    
    # Utility Methods
    
    def _extract_node_id(self, node_url: str) -> str:
        """Extract node ID from URL."""
        return f"node_{hash(node_url) % 10000:04d}"
    
    def _extract_host(self, node_url: str) -> str:
        """Extract host from URL."""
        from urllib.parse import urlparse
        parsed = urlparse(node_url)
        return parsed.hostname or 'localhost'
    
    def _extract_port(self, node_url: str) -> int:
        """Extract port from URL."""
        from urllib.parse import urlparse
        parsed = urlparse(node_url)
        return parsed.port or DEFAULT_PORT
    
    # Network Information Methods
    
    def get_network_status(self) -> Dict[str, Any]:
        """Get current network status."""
        return {
            'node_id': self.node_id,
            'is_running': self.is_running,
            'connected_peers': len(self.connected_peers),
            'total_known_peers': len(self.peers),
            'peer_list': list(self.connected_peers),
            'blacklisted_peers': len(self.blacklisted_peers),
            'stats': self.stats.copy(),
            'uptime': time.time() - self.stats['start_time'] if self.stats['start_time'] else 0
        }
    
    def get_peer_info(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific peer."""
        return self.peers.get(node_id)
    
    def get_all_peers(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all peers."""
        return self.peers.copy()
    
    def get_connected_peers(self) -> List[str]:
        """Get list of connected peer IDs."""
        return list(self.connected_peers)
    
    def blacklist_peer(self, node_id: str, reason: str = None):
        """Blacklist a peer."""
        self.blacklisted_peers.add(node_id)
        
        # Disconnect if currently connected
        if node_id in self.connected_peers:
            self._disconnect_from_peer(node_id)
        
        self.logger.info(f"Blacklisted peer {node_id}: {reason}")
    
    def unblacklist_peer(self, node_id: str):
        """Remove a peer from blacklist."""
        self.blacklisted_peers.discard(node_id)
        self.logger.info(f"Removed peer {node_id} from blacklist")
    
    # Event Handler Registration
    
    def set_on_peer_connected(self, callback: Callable[[Dict[str, Any]], None]):
        """Set callback for when a peer connects."""
        self.on_peer_connected = callback
    
    def set_on_peer_disconnected(self, callback: Callable[[Dict[str, Any]], None]):
        """Set callback for when a peer disconnects."""
        self.on_peer_disconnected = callback
    
    def set_on_message_received(self, callback: Callable[[str, Dict[str, Any]], None]):
        """Set callback for when a message is received."""
        self.on_message_received = callback


class NetworkTopology:
    """Network topology manager for visualizing and analyzing the P2P network."""
    
    def __init__(self, p2p_manager: P2PManager):
        """Initialize network topology manager."""
        self.p2p_manager = p2p_manager
        self.logger = logging.getLogger(__name__)
    
    def get_topology_graph(self) -> Dict[str, Any]:
        """Get network topology as a graph structure."""
        nodes = []
        edges = []
        
        # Add this node
        self_node = {
            'id': self.p2p_manager.node_id,
            'label': f"Node {self.p2p_manager.node_id}",
            'type': 'self',
            'status': 'online'
        }
        nodes.append(self_node)
        
        # Add connected peers
        for peer_id, peer_info in self.p2p_manager.get_all_peers().items():
            peer_node = {
                'id': peer_id,
                'label': f"Node {peer_id}",
                'type': 'peer',
                'status': peer_info.get('status', 'unknown'),
                'response_time': peer_info.get('response_time', 0),
                'connected_at': peer_info.get('connected_at', 0)
            }
            nodes.append(peer_node)
            
            # Add edge if connected
            if peer_id in self.p2p_manager.connected_peers:
                edge = {
                    'from': self.p2p_manager.node_id,
                    'to': peer_id,
                    'type': 'connection',
                    'weight': 1 / (peer_info.get('response_time', 1) + 0.001)
                }
                edges.append(edge)
        
        return {
            'nodes': nodes,
            'edges': edges,
            'stats': {
                'total_nodes': len(nodes),
                'total_edges': len(edges),
                'connected_nodes': len(self.p2p_manager.connected_peers) + 1
            }
        }
    
    def analyze_network_health(self) -> Dict[str, Any]:
        """Analyze the health of the network."""
        total_peers = len(self.p2p_manager.peers)
        connected_peers = len(self.p2p_manager.connected_peers)
        
        # Calculate connectivity ratio
        connectivity_ratio = connected_peers / max(total_peers, 1)
        
        # Calculate average response time
        response_times = [
            peer_info.get('response_time', 0)
            for peer_info in self.p2p_manager.peers.values()
            if peer_info.get('response_time', 0) > 0
        ]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # Determine health status
        if connectivity_ratio >= 0.8 and avg_response_time < 1.0:
            health_status = 'excellent'
        elif connectivity_ratio >= 0.6 and avg_response_time < 2.0:
            health_status = 'good'
        elif connectivity_ratio >= 0.4 and avg_response_time < 5.0:
            health_status = 'fair'
        else:
            health_status = 'poor'
        
        return {
            'health_status': health_status,
            'connectivity_ratio': connectivity_ratio,
            'average_response_time': avg_response_time,
            'total_peers': total_peers,
            'connected_peers': connected_peers,
            'blacklisted_peers': len(self.p2p_manager.blacklisted_peers),
            'uptime': time.time() - self.p2p_manager.stats['start_time'] if self.p2p_manager.stats['start_time'] else 0
        }


# Example usage
if __name__ == "__main__":
    # Create P2P manager
    p2p = P2PManager(node_id="test_node", port=5001)
    
    # Set up event handlers
    def on_peer_connected(peer_info):
        print(f"Peer connected: {peer_info['node_id']}")
    
    def on_peer_disconnected(peer_info):
        print(f"Peer disconnected: {peer_info['node_id']}")
    
    p2p.set_on_peer_connected(on_peer_connected)
    p2p.set_on_peer_disconnected(on_peer_disconnected)
    
    # Start P2P network
    seed_nodes = ["http://localhost:5000"]
    p2p.start(seed_nodes)
    
    try:
        # Keep running
        while True:
            status = p2p.get_network_status()
            print(f"Network status: {status['connected_peers']} peers connected")
            time.sleep(30)
            
    except KeyboardInterrupt:
        print("Stopping P2P manager...")
        p2p.stop()
