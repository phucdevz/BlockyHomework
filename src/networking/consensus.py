"""
ConsensusManager for BlockyHomework blockchain system.
Nakamoto consensus implementation.
"""

import threading
import time
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

# Import blockchain components
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.models.blockchain import Blockchain
from src.models.block import Block
from src.models.transaction import Transaction
from .client import BlockchainClient


class ConsensusManager:
    """
    Manages blockchain consensus using the Nakamoto Consensus (Longest Chain Rule).
    Handles fork resolution, chain replacement, and network synchronization.
    """
    
    def __init__(self, blockchain: Blockchain, client: BlockchainClient):
        """Initialize the consensus manager."""
        self.blockchain = blockchain
        self.client = client
        
        # Configure logging
        self.logger = logging.getLogger(__name__)
        
        # Consensus state
        self.is_syncing = False
        self.last_sync_time = 0
        self.sync_interval = 30  # seconds
        self.consensus_threshold = 0.51  # 51% majority
        
        # Fork detection and resolution
        self.known_forks = {}
        self.fork_resolution_in_progress = False
        
        # Synchronization thread
        self.sync_thread = None
        self.sync_active = False
        
        # Statistics
        self.stats = {
            'sync_attempts': 0,
            'successful_syncs': 0,
            'failed_syncs': 0,
            'forks_detected': 0,
            'forks_resolved': 0,
            'chain_replacements': 0,
            'last_sync_time': None
        }
    
    def start_consensus(self):
        """Start the consensus management process."""
        if self.sync_active:
            self.logger.warning("Consensus manager is already running")
            return
        
        try:
            self.sync_active = True
            
            # Start synchronization thread
            self.sync_thread = threading.Thread(target=self._consensus_loop)
            self.sync_thread.start()
            
            self.logger.info("Consensus manager started")
            
        except Exception as e:
            self.logger.error(f"Error starting consensus manager: {str(e)}")
            self.sync_active = False
            raise
    
    def stop_consensus(self):
        """Stop the consensus management process."""
        if not self.sync_active:
            return
        
        try:
            self.sync_active = False
            
            # Stop synchronization thread
            if self.sync_thread:
                self.sync_thread.join(timeout=10)
            
            self.logger.info("Consensus manager stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping consensus manager: {str(e)}")
    
    def _consensus_loop(self):
        """Main consensus management loop."""
        while self.sync_active:
            try:
                # Perform consensus check
                self._perform_consensus_check()
                
                # Sleep until next check
                time.sleep(self.sync_interval)
                
            except Exception as e:
                self.logger.error(f"Error in consensus loop: {str(e)}")
                time.sleep(self.sync_interval)
    
    def _perform_consensus_check(self):
        """Perform a consensus check with the network."""
        if self.is_syncing:
            return
        
        try:
            self.is_syncing = True
            self.stats['sync_attempts'] += 1
            
            # Get network status
            network_status = self.client.get_network_status()
            if not network_status or not network_status.get('success'):
                self.stats['failed_syncs'] += 1
                return
            
            # Get connected nodes
            nodes_response = self.client.get_nodes()
            if not nodes_response or not nodes_response.get('success'):
                self.stats['failed_syncs'] += 1
                return
            
            connected_nodes = nodes_response.get('data', {}).get('nodes', [])
            
            if not connected_nodes:
                self.logger.info("No connected nodes for consensus check")
                return
            
            # Collect blockchain information from peers
            peer_chains = self._collect_peer_chains(connected_nodes)
            
            # Analyze consensus
            consensus_result = self._analyze_consensus(peer_chains)
            
            # Apply consensus decision
            if consensus_result['action'] == 'replace_chain':
                self._replace_local_chain(consensus_result['new_chain'])
            elif consensus_result['action'] == 'resolve_fork':
                self._resolve_fork(consensus_result['fork_info'])
            
            self.stats['successful_syncs'] += 1
            self.stats['last_sync_time'] = datetime.now().isoformat()
            self.last_sync_time = time.time()
            
        except Exception as e:
            self.logger.error(f"Error in consensus check: {str(e)}")
            self.stats['failed_syncs'] += 1
        finally:
            self.is_syncing = False
    
    def _collect_peer_chains(self, peer_nodes: List[str]) -> List[Dict[str, Any]]:
        """Collect blockchain information from peer nodes."""
        peer_chains = []
        
        for node_url in peer_nodes:
            try:
                # Connect to peer
                if self.client.connect(node_url):
                    # Get blockchain status
                    status_response = self.client.get_blockchain_status()
                    
                    if status_response and status_response.get('success'):
                        status_data = status_response.get('data', {})
                        
                        # Get full chain
                        chain_response = self.client.get_full_chain()
                        
                        if chain_response and chain_response.get('success'):
                            chain_data = chain_response.get('data', {})
                            
                            peer_info = {
                                'node_url': node_url,
                                'chain_length': status_data.get('chain_length', 0),
                                'latest_block_hash': status_data.get('latest_block', {}).get('hash', ''),
                                'difficulty': status_data.get('difficulty', 0),
                                'is_valid': status_data.get('is_valid', False),
                                'chain': chain_data.get('chain', []),
                                'response_time': time.time()
                            }
                            
                            peer_chains.append(peer_info)
                            
            except Exception as e:
                self.logger.warning(f"Failed to collect chain from peer {node_url}: {str(e)}")
        
        return peer_chains
    
    def _analyze_consensus(self, peer_chains: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze consensus based on peer chain information."""
        if not peer_chains:
            return {'action': 'no_action', 'reason': 'no_peers'}
        
        # Get local chain info
        local_length = self.blockchain.get_chain_length()
        local_hash = self.blockchain.get_latest_block().hash
        
        # Group chains by length and latest hash
        chain_groups = {}
        
        for peer_info in peer_chains:
            if not peer_info['is_valid']:
                continue
            
            key = (peer_info['chain_length'], peer_info['latest_block_hash'])
            if key not in chain_groups:
                chain_groups[key] = []
            chain_groups[key].append(peer_info)
        
        # Find the longest valid chain(s)
        if not chain_groups:
            return {'action': 'no_action', 'reason': 'no_valid_peers'}
        
        longest_length = max(chain_groups.keys(), key=lambda x: x[0])[0]
        longest_chains = [(k, v) for k, v in chain_groups.items() if k[0] == longest_length]
        
        # Consensus decision logic
        if longest_length > local_length:
            # Network has a longer chain
            if len(longest_chains) == 1:
                # Clear consensus on longer chain
                chain_key, chain_group = longest_chains[0]
                return {
                    'action': 'replace_chain',
                    'reason': 'longer_chain_consensus',
                    'new_chain': chain_group[0]['chain'],
                    'new_length': longest_length,
                    'consensus_size': len(chain_group)
                }
            else:
                # Multiple longest chains - fork detected
                self.stats['forks_detected'] += 1
                return {
                    'action': 'resolve_fork',
                    'reason': 'multiple_longest_chains',
                    'fork_info': {
                        'chains': longest_chains,
                        'fork_length': longest_length
                    }
                }
        
        elif longest_length == local_length:
            # Same length - check for consensus on hash
            local_key = (local_length, local_hash)
            
            if local_key in chain_groups:
                # Our chain matches some peers
                our_group_size = len(chain_groups[local_key])
                total_peers = len(peer_chains)
                
                if our_group_size / total_peers >= self.consensus_threshold:
                    # We have consensus
                    return {
                        'action': 'no_action',
                        'reason': 'local_chain_has_consensus',
                        'consensus_size': our_group_size,
                        'total_peers': total_peers
                    }
                else:
                    # No clear consensus
                    if len(longest_chains) == 1:
                        # Replace with the chain that has most support
                        chain_key, chain_group = max(longest_chains, key=lambda x: len(x[1]))
                        return {
                            'action': 'replace_chain',
                            'reason': 'peer_consensus_override',
                            'new_chain': chain_group[0]['chain'],
                            'new_length': longest_length,
                            'consensus_size': len(chain_group)
                        }
            else:
                # Our chain doesn't match any peers
                chain_key, chain_group = max(longest_chains, key=lambda x: len(x[1]))
                return {
                    'action': 'replace_chain',
                    'reason': 'local_chain_diverged',
                    'new_chain': chain_group[0]['chain'],
                    'new_length': longest_length,
                    'consensus_size': len(chain_group)
                }
        
        else:
            # Local chain is longer than network
            return {
                'action': 'no_action',
                'reason': 'local_chain_longer',
                'local_length': local_length,
                'network_length': longest_length
            }
        
        return {'action': 'no_action', 'reason': 'no_consensus_needed'}
    
    def _replace_local_chain(self, new_chain_data: List[Dict[str, Any]]):
        """Replace the local blockchain with a new chain."""
        try:
            # Validate the new chain
            if not self._validate_chain_data(new_chain_data):
                self.logger.error("New chain validation failed")
                return False
            
            # Create new blockchain from data
            new_blockchain = self._reconstruct_blockchain(new_chain_data)
            
            if not new_blockchain:
                self.logger.error("Failed to reconstruct blockchain from peer data")
                return False
            
            # Validate the reconstructed chain
            if not new_blockchain.validate_chain():
                self.logger.error("Reconstructed chain validation failed")
                return False
            
            # Replace local chain
            old_length = self.blockchain.get_chain_length()
            self.blockchain.replace_chain(new_blockchain.chain)
            new_length = self.blockchain.get_chain_length()
            
            self.stats['chain_replacements'] += 1
            self.logger.info(f"Chain replaced: {old_length} -> {new_length} blocks")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error replacing local chain: {str(e)}")
            return False
    
    def _resolve_fork(self, fork_info: Dict[str, Any]):
        """Resolve a detected fork."""
        try:
            if self.fork_resolution_in_progress:
                return
            
            self.fork_resolution_in_progress = True
            
            # Analyze fork chains
            chains = fork_info['chains']
            
            # Choose the chain with the most peer support
            best_chain = max(chains, key=lambda x: len(x[1]))
            chain_key, chain_group = best_chain
            
            # Replace with the best chain
            success = self._replace_local_chain(chain_group[0]['chain'])
            
            if success:
                self.stats['forks_resolved'] += 1
                self.logger.info(f"Fork resolved: selected chain with {len(chain_group)} peer support")
            
        except Exception as e:
            self.logger.error(f"Error resolving fork: {str(e)}")
        finally:
            self.fork_resolution_in_progress = False
    
    def _validate_chain_data(self, chain_data: List[Dict[str, Any]]) -> bool:
        """Validate chain data received from peers."""
        try:
            if not chain_data or not isinstance(chain_data, list):
                return False
            
            # Basic validation
            if len(chain_data) == 0:
                return False
            
            # Check if first block is genesis
            first_block = chain_data[0]
            if first_block.get('index') != 0:
                return False
            
            # Check sequential indices
            for i, block_data in enumerate(chain_data):
                if block_data.get('index') != i:
                    return False
                
                # Check previous hash linkage
                if i > 0:
                    prev_block = chain_data[i - 1]
                    if block_data.get('previous_hash') != prev_block.get('hash'):
                        return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating chain data: {str(e)}")
            return False
    
    def _reconstruct_blockchain(self, chain_data: List[Dict[str, Any]]) -> Optional[Blockchain]:
        """Reconstruct a blockchain from chain data."""
        try:
            # Create new blockchain
            new_blockchain = Blockchain()
            new_blockchain.chain = []  # Clear genesis block
            
            # Reconstruct blocks
            for block_data in chain_data:
                # Reconstruct transactions
                transactions = []
                for tx_data in block_data.get('transactions', []):
                    transaction = Transaction.from_dict(tx_data)
                    transactions.append(transaction)
                
                # Create block
                block = Block(
                    index=block_data.get('index'),
                    timestamp=block_data.get('timestamp'),
                    transactions=transactions,
                    previous_hash=block_data.get('previous_hash'),
                    nonce=block_data.get('nonce', 0)
                )
                
                # Set the hash (should match the data)
                block.hash = block_data.get('hash')
                
                new_blockchain.chain.append(block)
            
            return new_blockchain
            
        except Exception as e:
            self.logger.error(f"Error reconstructing blockchain: {str(e)}")
            return None
    
    # Public Interface Methods
    
    def force_sync(self) -> bool:
        """Force an immediate consensus check."""
        try:
            self._perform_consensus_check()
            return True
        except Exception as e:
            self.logger.error(f"Error in forced sync: {str(e)}")
            return False
    
    def is_synced_with_network(self, peer_nodes: List[str] = None) -> Tuple[bool, Dict[str, Any]]:
        """Check if local chain is synced with the network."""
        try:
            if peer_nodes is None:
                # Get connected nodes
                nodes_response = self.client.get_nodes()
                if not nodes_response or not nodes_response.get('success'):
                    return False, {'error': 'Failed to get connected nodes'}
                
                peer_nodes = nodes_response.get('data', {}).get('nodes', [])
            
            if not peer_nodes:
                return True, {'reason': 'no_peers_to_check'}
            
            # Collect peer chains
            peer_chains = self._collect_peer_chains(peer_nodes)
            
            if not peer_chains:
                return True, {'reason': 'no_valid_peer_chains'}
            
            # Check consensus
            local_length = self.blockchain.get_chain_length()
            local_hash = self.blockchain.get_latest_block().hash
            
            # Find peers with same chain
            matching_peers = 0
            for peer_info in peer_chains:
                if (peer_info['chain_length'] == local_length and 
                    peer_info['latest_block_hash'] == local_hash):
                    matching_peers += 1
            
            total_peers = len(peer_chains)
            consensus_ratio = matching_peers / total_peers if total_peers > 0 else 0
            
            is_synced = consensus_ratio >= self.consensus_threshold
            
            sync_info = {
                'local_length': local_length,
                'local_hash': local_hash,
                'matching_peers': matching_peers,
                'total_peers': total_peers,
                'consensus_ratio': consensus_ratio,
                'threshold': self.consensus_threshold
            }
            
            return is_synced, sync_info
            
        except Exception as e:
            self.logger.error(f"Error checking network sync: {str(e)}")
            return False, {'error': str(e)}
    
    def get_consensus_stats(self) -> Dict[str, Any]:
        """Get consensus manager statistics."""
        stats = self.stats.copy()
        stats.update({
            'is_syncing': self.is_syncing,
            'sync_active': self.sync_active,
            'last_sync_ago': time.time() - self.last_sync_time if self.last_sync_time > 0 else None,
            'sync_interval': self.sync_interval,
            'consensus_threshold': self.consensus_threshold,
            'fork_resolution_active': self.fork_resolution_in_progress
        })
        return stats
    
    def set_sync_interval(self, interval: int):
        """Set the consensus check interval."""
        self.sync_interval = max(interval, 10)  # Minimum 10 seconds
        self.logger.info(f"Sync interval set to {self.sync_interval} seconds")
    
    def set_consensus_threshold(self, threshold: float):
        """Set the consensus threshold."""
        self.consensus_threshold = max(0.1, min(threshold, 1.0))  # Between 10% and 100%
        self.logger.info(f"Consensus threshold set to {self.consensus_threshold}")


# Example usage
if __name__ == "__main__":
    # Create blockchain and client
    blockchain = Blockchain()
    client = BlockchainClient()
    
    # Create consensus manager
    consensus = ConsensusManager(blockchain, client)
    
    # Start consensus
    consensus.start_consensus()
    
    try:
        # Keep running
        while True:
            stats = consensus.get_consensus_stats()
            print(f"Consensus stats: {stats}")
            
            # Check sync status
            is_synced, sync_info = consensus.is_synced_with_network()
            print(f"Synced: {is_synced}, Info: {sync_info}")
            
            time.sleep(60)
            
    except KeyboardInterrupt:
        print("Stopping consensus manager...")
        consensus.stop_consensus()
