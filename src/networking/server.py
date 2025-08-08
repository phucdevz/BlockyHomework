"""
BlockchainServer for BlockyHomework blockchain system.
HTTP server implementation with Flask/FastAPI.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import threading
import time
import logging
from typing import Dict, Any, Optional, List
import json
from datetime import datetime

# Import constants and models
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from config.constants import DEFAULT_PORT, ENDPOINTS, API_BASE
from src.models.blockchain import Blockchain
from src.models.transaction import Transaction
from src.models.wallet import Wallet


class BlockchainServer:
    """
    HTTP server for blockchain node communication.
    Provides REST API endpoints for blockchain operations.
    """
    
    def __init__(self, host: str = "localhost", port: int = DEFAULT_PORT, 
                 blockchain: Blockchain = None):
        """Initialize the blockchain server."""
        self.host = host
        self.port = port
        self.blockchain = blockchain or Blockchain()
        
        # Initialize Flask app
        self.app = Flask(__name__)
        CORS(self.app)  # Enable CORS for all domains
        
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Server state
        self.is_running = False
        self.server_thread = None
        self.connected_nodes = set()
        
        # Setup routes
        self._setup_routes()
        self._setup_error_handlers()
    
    def _setup_routes(self):
        """Setup all API routes."""
        
        # Blockchain endpoints
        self.app.route('/api/blockchain/status', methods=['GET'])(self.get_blockchain_status)
        self.app.route('/api/chain', methods=['GET'])(self.get_full_chain)
        self.app.route('/api/chain/validate', methods=['GET'])(self.validate_chain)
        
        # Transaction endpoints
        self.app.route('/api/transactions/create', methods=['POST'])(self.create_transaction)
        self.app.route('/api/transactions/pending', methods=['GET'])(self.get_pending_transactions)
        self.app.route('/api/transactions/history', methods=['GET'])(self.get_transaction_history)
        
        # Mining endpoints
        self.app.route('/api/mining/status', methods=['GET'])(self.get_mining_status)
        self.app.route('/api/mining/start', methods=['POST'])(self.start_mining)
        self.app.route('/api/mining/stop', methods=['POST'])(self.stop_mining)
        self.app.route('/api/mining/mine-block', methods=['POST'])(self.mine_block)
        
        # Wallet endpoints
        self.app.route('/api/wallet/balance', methods=['GET'])(self.get_wallet_balance)
        self.app.route('/api/wallet/create', methods=['POST'])(self.create_wallet)
        
        # Network endpoints
        self.app.route('/api/network/status', methods=['GET'])(self.get_network_status)
        self.app.route('/api/nodes/register', methods=['POST'])(self.register_node)
        self.app.route('/api/nodes/list', methods=['GET'])(self.get_nodes)
        self.app.route('/api/consensus', methods=['GET'])(self.consensus_resolve)
        
        # Health check
        self.app.route('/api/health', methods=['GET'])(self.health_check)
        
        # Information endpoints
        self.app.route('/api/info', methods=['GET'])(self.get_server_info)
    
    def _setup_error_handlers(self):
        """Setup error handling middleware."""
        
        @self.app.errorhandler(400)
        def bad_request(error):
            return jsonify({
                'error': 'Bad Request',
                'message': 'Invalid request format or parameters',
                'status': 400,
                'timestamp': datetime.now().isoformat()
            }), 400
        
        @self.app.errorhandler(404)
        def not_found(error):
            return jsonify({
                'error': 'Not Found',
                'message': 'The requested resource was not found',
                'status': 404,
                'timestamp': datetime.now().isoformat()
            }), 404
        
        @self.app.errorhandler(500)
        def internal_error(error):
            return jsonify({
                'error': 'Internal Server Error',
                'message': 'An internal server error occurred',
                'status': 500,
                'timestamp': datetime.now().isoformat()
            }), 500
    
    # API Endpoint Implementations
    
    def get_blockchain_status(self):
        """Get current blockchain status."""
        try:
            return jsonify({
                'success': True,
                'data': {
                    'chain_length': self.blockchain.get_chain_length(),
                    'latest_block': self.blockchain.get_latest_block().to_dict(),
                    'difficulty': self.blockchain.difficulty,
                    'mempool_size': self.blockchain.mempool.get_transaction_count(),
                    'is_valid': self.blockchain.validate_chain()
                },
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            self.logger.error(f"Error getting blockchain status: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    def get_full_chain(self):
        """Get the complete blockchain."""
        try:
            chain_data = []
            for block in self.blockchain.chain:
                chain_data.append(block.to_dict())
            
            return jsonify({
                'success': True,
                'data': {
                    'chain': chain_data,
                    'length': len(chain_data)
                },
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            self.logger.error(f"Error getting full chain: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    def validate_chain(self):
        """Validate the blockchain."""
        try:
            is_valid = self.blockchain.validate_chain()
            return jsonify({
                'success': True,
                'data': {
                    'is_valid': is_valid,
                    'chain_length': self.blockchain.get_chain_length()
                },
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            self.logger.error(f"Error validating chain: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    def create_transaction(self):
        """Create a new transaction."""
        try:
            data = request.get_json()
            
            if not data or 'sender' not in data or 'recipient' not in data or 'amount' not in data:
                return jsonify({
                    'success': False,
                    'error': 'Missing required fields: sender, recipient, amount'
                }), 400
            
            # Create transaction
            transaction = Transaction(
                sender=data['sender'],
                recipient=data['recipient'],
                amount=float(data['amount'])
            )
            
            # Add to blockchain
            success = self.blockchain.add_transaction(transaction)
            
            if success:
                return jsonify({
                    'success': True,
                    'data': {
                        'transaction': transaction.to_dict(),
                        'message': 'Transaction created successfully'
                    },
                    'timestamp': datetime.now().isoformat()
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Failed to add transaction to mempool'
                }), 400
                
        except Exception as e:
            self.logger.error(f"Error creating transaction: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    def get_pending_transactions(self):
        """Get pending transactions from mempool."""
        try:
            pending = self.blockchain.mempool.get_pending_transactions()
            transactions_data = [tx.to_dict() for tx in pending]
            
            return jsonify({
                'success': True,
                'data': {
                    'transactions': transactions_data,
                    'count': len(transactions_data)
                },
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            self.logger.error(f"Error getting pending transactions: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    def get_transaction_history(self):
        """Get transaction history."""
        try:
            address = request.args.get('address')
            if not address:
                return jsonify({
                    'success': False,
                    'error': 'Address parameter required'
                }), 400
            
            # Get transactions from all blocks
            transactions = []
            for block in self.blockchain.chain:
                for tx in block.transactions:
                    if tx.sender == address or tx.recipient == address:
                        transactions.append(tx.to_dict())
            
            return jsonify({
                'success': True,
                'data': {
                    'transactions': transactions,
                    'count': len(transactions)
                },
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            self.logger.error(f"Error getting transaction history: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    def get_mining_status(self):
        """Get current mining status."""
        try:
            return jsonify({
                'success': True,
                'data': {
                    'is_mining': hasattr(self, '_mining_thread') and self._mining_thread and self._mining_thread.is_alive(),
                    'difficulty': self.blockchain.difficulty,
                    'block_reward': self.blockchain.block_reward,
                    'pending_transactions': self.blockchain.mempool.get_transaction_count()
                },
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            self.logger.error(f"Error getting mining status: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    def start_mining(self):
        """Start mining process."""
        try:
            if hasattr(self, '_mining_thread') and self._mining_thread and self._mining_thread.is_alive():
                return jsonify({
                    'success': False,
                    'error': 'Mining already in progress'
                }), 400
            
            # Start mining in background thread
            self._mining_thread = threading.Thread(target=self._mine_continuously)
            self._mining_active = True
            self._mining_thread.start()
            
            return jsonify({
                'success': True,
                'data': {
                    'message': 'Mining started successfully',
                    'status': 'mining'
                },
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            self.logger.error(f"Error starting mining: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    def stop_mining(self):
        """Stop mining process."""
        try:
            if not hasattr(self, '_mining_thread') or not self._mining_thread or not self._mining_thread.is_alive():
                return jsonify({
                    'success': False,
                    'error': 'Mining is not currently active'
                }), 400
            
            self._mining_active = False
            if self._mining_thread:
                self._mining_thread.join(timeout=5)
            
            return jsonify({
                'success': True,
                'data': {
                    'message': 'Mining stopped successfully',
                    'status': 'stopped'
                },
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            self.logger.error(f"Error stopping mining: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    def mine_block(self):
        """Mine a single block."""
        try:
            # Check if there are pending transactions
            if self.blockchain.mempool.get_transaction_count() == 0:
                return jsonify({
                    'success': False,
                    'error': 'No pending transactions to mine'
                }), 400
            
            # Mine the block
            new_block = self.blockchain.mine_block("miner_address")
            
            if new_block:
                return jsonify({
                    'success': True,
                    'data': {
                        'block': new_block.to_dict(),
                        'message': 'Block mined successfully'
                    },
                    'timestamp': datetime.now().isoformat()
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Failed to mine block'
                }), 500
                
        except Exception as e:
            self.logger.error(f"Error mining block: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    def get_wallet_balance(self):
        """Get wallet balance."""
        try:
            address = request.args.get('address')
            if not address:
                return jsonify({
                    'success': False,
                    'error': 'Address parameter required'
                }), 400
            
            balance = self.blockchain.get_balance(address)
            
            return jsonify({
                'success': True,
                'data': {
                    'address': address,
                    'balance': balance
                },
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            self.logger.error(f"Error getting wallet balance: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    def create_wallet(self):
        """Create a new wallet."""
        try:
            wallet = Wallet()
            
            return jsonify({
                'success': True,
                'data': {
                    'wallet': wallet.to_dict(),
                    'message': 'Wallet created successfully'
                },
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            self.logger.error(f"Error creating wallet: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    def get_network_status(self):
        """Get network status."""
        try:
            return jsonify({
                'success': True,
                'data': {
                    'connected_nodes': list(self.connected_nodes),
                    'node_count': len(self.connected_nodes),
                    'server_host': self.host,
                    'server_port': self.port,
                    'uptime': time.time() - getattr(self, 'start_time', time.time())
                },
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            self.logger.error(f"Error getting network status: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    def register_node(self):
        """Register a new node."""
        try:
            data = request.get_json()
            
            if not data or 'node_url' not in data:
                return jsonify({
                    'success': False,
                    'error': 'Missing required field: node_url'
                }), 400
            
            node_url = data['node_url']
            self.connected_nodes.add(node_url)
            
            return jsonify({
                'success': True,
                'data': {
                    'node_url': node_url,
                    'message': 'Node registered successfully',
                    'total_nodes': len(self.connected_nodes)
                },
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            self.logger.error(f"Error registering node: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    def get_nodes(self):
        """Get list of connected nodes."""
        try:
            return jsonify({
                'success': True,
                'data': {
                    'nodes': list(self.connected_nodes),
                    'count': len(self.connected_nodes)
                },
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            self.logger.error(f"Error getting nodes: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    def consensus_resolve(self):
        """Resolve conflicts using consensus algorithm."""
        try:
            # TODO: Implement consensus resolution with other nodes
            return jsonify({
                'success': True,
                'data': {
                    'message': 'Consensus resolved',
                    'chain_length': self.blockchain.get_chain_length(),
                    'replaced': False
                },
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            self.logger.error(f"Error resolving consensus: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    def health_check(self):
        """Health check endpoint."""
        try:
            return jsonify({
                'success': True,
                'data': {
                    'status': 'healthy',
                    'server': 'BlockyHomework Blockchain Server',
                    'version': '1.0.0',
                    'uptime': time.time() - getattr(self, 'start_time', time.time())
                },
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            self.logger.error(f"Error in health check: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    def get_server_info(self):
        """Get server information."""
        try:
            return jsonify({
                'success': True,
                'data': {
                    'server_name': 'BlockyHomework Blockchain Server',
                    'version': '1.0.0',
                    'host': self.host,
                    'port': self.port,
                    'blockchain': {
                        'chain_length': self.blockchain.get_chain_length(),
                        'difficulty': self.blockchain.difficulty,
                        'block_reward': self.blockchain.block_reward
                    },
                    'network': {
                        'connected_nodes': len(self.connected_nodes),
                        'uptime': time.time() - getattr(self, 'start_time', time.time())
                    }
                },
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            self.logger.error(f"Error getting server info: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    # Helper Methods
    
    def _mine_continuously(self):
        """Continuously mine blocks in background."""
        while getattr(self, '_mining_active', False):
            try:
                if self.blockchain.mempool.get_transaction_count() > 0:
                    self.blockchain.mine_block("miner_address")
                    self.logger.info("New block mined successfully")
                else:
                    time.sleep(1)
            except Exception as e:
                self.logger.error(f"Error in continuous mining: {str(e)}")
                time.sleep(1)
    
    def start_server(self, debug: bool = False, threaded: bool = True):
        """Start the blockchain server."""
        try:
            self.start_time = time.time()
            self.is_running = True
            
            self.logger.info(f"Starting BlockyHomework Blockchain Server on {self.host}:{self.port}")
            
            self.app.run(
                host=self.host,
                port=self.port,
                debug=debug,
                threaded=threaded,
                use_reloader=False
            )
            
        except Exception as e:
            self.logger.error(f"Error starting server: {str(e)}")
            self.is_running = False
            raise
    
    def stop_server(self):
        """Stop the blockchain server."""
        try:
            self.is_running = False
            
            # Stop mining if active
            if hasattr(self, '_mining_active'):
                self._mining_active = False
            
            if hasattr(self, '_mining_thread') and self._mining_thread:
                self._mining_thread.join(timeout=5)
            
            self.logger.info("BlockyHomework Blockchain Server stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping server: {str(e)}")
            raise
    
    def get_status(self) -> Dict[str, Any]:
        """Get current server status."""
        return {
            'is_running': self.is_running,
            'host': self.host,
            'port': self.port,
            'connected_nodes': len(self.connected_nodes),
            'blockchain_length': self.blockchain.get_chain_length(),
            'pending_transactions': self.blockchain.mempool.get_transaction_count(),
            'uptime': time.time() - getattr(self, 'start_time', time.time()) if hasattr(self, 'start_time') else 0
        }


# Standalone server runner
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='BlockyHomework Blockchain Server')
    parser.add_argument('--host', default='localhost', help='Server host')
    parser.add_argument('--port', type=int, default=DEFAULT_PORT, help='Server port')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    # Create and start server
    server = BlockchainServer(host=args.host, port=args.port)
    
    try:
        server.start_server(debug=args.debug)
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.stop_server()
