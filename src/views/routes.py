"""
Flask routes for BlockyHomework blockchain system.
Defines all UI routes and API endpoints.
"""

from flask import Flask, render_template, jsonify, request, make_response
from datetime import datetime
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from models.blockchain import Blockchain
from models.wallet import Wallet
from models.transaction import Transaction
from viewmodels.node_viewmodel import NodeViewModel
from viewmodels.blockchain_viewmodel import BlockchainViewModel
from viewmodels.wallet_viewmodel import WalletViewModel
from networking.p2p_manager import P2PManager
from simulation.attack_simulator import AttackSimulator

# Initialize core components
blockchain = Blockchain()
wallet = Wallet()
p2p_manager = P2PManager()
attack_simulator = AttackSimulator()

# Initialize ViewModels
node_viewmodel = NodeViewModel(blockchain, wallet)
blockchain_viewmodel = BlockchainViewModel(blockchain)
wallet_viewmodel = WalletViewModel(wallet, blockchain)

def init_routes(app: Flask):
    """Initialize all routes for the Flask application."""
    
    # ===== UI ROUTES =====
    
    @app.route('/')
    def dashboard():
        """Main dashboard page"""
        return render_template('dashboard.html')
    
    @app.route('/transactions')
    def transactions():
        """Transactions page"""
        return render_template('transactions.html')
    
    @app.route('/mining')
    def mining():
        """Mining page"""
        return render_template('mining.html')
    
    @app.route('/network')
    def network():
        """Network page"""
        return render_template('network.html')
    
    @app.route('/simulation')
    def simulation():
        """Simulation page"""
        return render_template('simulation.html')
    
    @app.route('/home')
    def home():
        """Home page - BlockyHomework introduction"""
        return render_template('home.html')
    
    # ===== API ROUTES =====
    
    @app.route('/api/blockchain/status')
    def get_blockchain_status():
        """Get blockchain status"""
        try:
            return jsonify({
                'chain_length': blockchain.get_chain_length(),
                'difficulty': blockchain.difficulty,
                'pending_transactions': len(blockchain.mempool.transactions),
                'block_reward': blockchain.block_reward,
                'is_valid': blockchain.validate_chain()
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/blockchain/chain')
    def get_chain():
        """Get full blockchain"""
        try:
            chain_data = blockchain_viewmodel.get_chain_display()
            return jsonify({
                'chain': chain_data,
                'length': len(chain_data)
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/blockchain/block/<int:index>')
    def get_block_by_index(index):
        """Get block by index"""
        try:
            block = blockchain.get_block_by_index(index)
            if block:
                return jsonify(block.to_dict())
            else:
                return jsonify({'error': 'Block not found'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/blockchain/block/hash/<block_hash>')
    def get_block_by_hash(block_hash):
        """Get block by hash"""
        try:
            block = blockchain.get_block_by_hash(block_hash)
            if block:
                return jsonify(block.to_dict())
            else:
                return jsonify({'error': 'Block not found'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/wallet/balance')
    def get_wallet_balance():
        """Get wallet balance"""
        try:
            balance = wallet_viewmodel.get_wallet_balance_display()
            address = wallet_viewmodel.get_address_display()
            return jsonify({
                'address': address,
                'balance': balance,
                'balance_numeric': wallet.get_balance(blockchain)
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/wallet/address')
    def get_wallet_address():
        """Get wallet address"""
        try:
            return jsonify({
                'address': wallet_viewmodel.get_address_display(),
                'public_key': wallet.public_key
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/wallet/history')
    def get_wallet_history():
        """Get wallet transaction history"""
        try:
            history = wallet_viewmodel.get_transaction_history()
            return jsonify({
                'transactions': history,
                'count': len(history)
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/transactions/create', methods=['POST'])
    def create_transaction():
        """Create a new transaction"""
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            recipient = data.get('recipient')
            amount = data.get('amount')
            
            if not recipient or not amount:
                return jsonify({'error': 'Missing recipient or amount'}), 400
            
            try:
                amount = float(amount)
                if amount <= 0:
                    return jsonify({'error': 'Amount must be positive'}), 400
            except ValueError:
                return jsonify({'error': 'Invalid amount format'}), 400
            
            # Create transaction
            transaction = wallet.create_transaction(recipient, amount)
            
            # Add to mempool
            if blockchain.add_transaction(transaction):
                return jsonify({
                    'success': True,
                    'transaction': transaction.to_dict(),
                    'message': 'Transaction created successfully'
                })
            else:
                return jsonify({'error': 'Failed to add transaction to mempool'}), 400
                
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/transactions/pending')
    def get_pending_transactions():
        """Get pending transactions from mempool"""
        try:
            pending = node_viewmodel.get_pending_transactions()
            return jsonify({
                'transactions': pending,
                'count': len(pending)
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/transactions/<transaction_hash>')
    def get_transaction_by_hash(transaction_hash):
        """Get transaction by hash"""
        try:
            # Check mempool first
            tx = blockchain.mempool.get_transaction_by_hash(transaction_hash)
            if tx:
                return jsonify({
                    'transaction': tx.to_dict(),
                    'status': 'pending'
                })
            
            # Check blockchain
            tx = blockchain.get_transaction_by_hash(transaction_hash)
            if tx:
                return jsonify({
                    'transaction': tx.to_dict(),
                    'status': 'confirmed'
                })
            
            return jsonify({'error': 'Transaction not found'}), 404
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/mining/status')
    def get_mining_status():
        """Get mining status"""
        try:
            status = blockchain_viewmodel.get_mining_status_display()
            return jsonify({
                'is_mining': False,  # TODO: Implement actual mining status
                'difficulty': status['difficulty'],
                'block_reward': status['block_reward'],
                'chain_length': status['chain_length']
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/mining/start', methods=['POST'])
    def start_mining():
        """Start mining"""
        try:
            # TODO: Implement actual mining start
            return jsonify({
                'success': True,
                'message': 'Mining started successfully'
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/mining/stop', methods=['POST'])
    def stop_mining():
        """Stop mining"""
        try:
            # TODO: Implement actual mining stop
            return jsonify({
                'success': True,
                'message': 'Mining stopped successfully'
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/mining/mine-block', methods=['POST'])
    def mine_block():
        """Mine a single block"""
        try:
            block = blockchain.mine_block(wallet.address)
            if block:
                return jsonify({
                    'success': True,
                    'block': block.to_dict(),
                    'message': f'Block #{block.index} mined successfully'
                })
            else:
                return jsonify({'error': 'No transactions to mine'}), 400
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/network/status')
    def get_network_status():
        """Get network status"""
        try:
            return jsonify({
                'connected_nodes': len(p2p_manager.connected_peers),
                'total_peers': len(p2p_manager.peers),
                'network_status': 'connected' if p2p_manager.is_running else 'disconnected',
                'node_id': p2p_manager.node_id,
                'port': p2p_manager.port
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/network/peers')
    def get_network_peers():
        """Get connected peers"""
        try:
            peers = list(p2p_manager.connected_peers)
            return jsonify({
                'peers': peers,
                'count': len(peers)
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/network/connect', methods=['POST'])
    def connect_to_peer():
        """Connect to a peer"""
        try:
            data = request.get_json()
            peer_address = data.get('address')
            
            if not peer_address:
                return jsonify({'error': 'Peer address required'}), 400
            
            # TODO: Implement actual peer connection
            return jsonify({
                'success': True,
                'message': f'Connected to {peer_address}'
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # ===== SIMULATION ROUTES =====
    
    @app.route('/api/simulation/status')
    def get_simulation_status():
        """Get attack simulation status"""
        try:
            return jsonify({
                'is_running': attack_simulator.is_running,
                'current_scenario': attack_simulator.current_scenario,
                'attack_progress': attack_simulator.attack_progress
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/simulation/start', methods=['POST'])
    def start_simulation():
        """Start attack simulation"""
        try:
            data = request.get_json()
            scenario = data.get('scenario', '51_percent_attack')
            
            # TODO: Implement actual simulation start
            return jsonify({
                'success': True,
                'message': f'Simulation {scenario} started'
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/simulation/stop', methods=['POST'])
    def stop_simulation():
        """Stop attack simulation"""
        try:
            # TODO: Implement actual simulation stop
            return jsonify({
                'success': True,
                'message': 'Simulation stopped'
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # ===== UTILITY ROUTES =====
    
    @app.route('/sitemap.xml')
    def sitemap():
        """Generate sitemap.xml for SEO"""
        sitemap_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>{request.url_root}home</loc>
        <lastmod>{datetime.now().strftime('%Y-%m-%d')}</lastmod>
        <changefreq>weekly</changefreq>
        <priority>1.0</priority>
    </url>
    <url>
        <loc>{request.url_root}</loc>
        <lastmod>{datetime.now().strftime('%Y-%m-%d')}</lastmod>
        <changefreq>daily</changefreq>
        <priority>0.9</priority>
    </url>
    <url>
        <loc>{request.url_root}transactions</loc>
        <lastmod>{datetime.now().strftime('%Y-%m-%d')}</lastmod>
        <changefreq>daily</changefreq>
        <priority>0.8</priority>
    </url>
    <url>
        <loc>{request.url_root}mining</loc>
        <lastmod>{datetime.now().strftime('%Y-%m-%d')}</lastmod>
        <changefreq>daily</changefreq>
        <priority>0.8</priority>
    </url>
    <url>
        <loc>{request.url_root}network</loc>
        <lastmod>{datetime.now().strftime('%Y-%m-%d')}</lastmod>
        <changefreq>weekly</changefreq>
        <priority>0.7</priority>
    </url>
    <url>
        <loc>{request.url_root}simulation</loc>
        <lastmod>{datetime.now().strftime('%Y-%m-%d')}</lastmod>
        <changefreq>weekly</changefreq>
        <priority>0.7</priority>
    </url>
</urlset>'''
        
        response = make_response(sitemap_xml)
        response.headers["Content-Type"] = "application/xml"
        return response
    
    @app.route('/robots.txt')
    def robots():
        """Generate robots.txt for SEO"""
        robots_txt = f'''User-agent: *
Allow: /

# Sitemap
Sitemap: {request.url_root}sitemap.xml

# Crawl-delay
Crawl-delay: 1'''
        
        response = make_response(robots_txt)
        response.headers["Content-Type"] = "text/plain"
        return response
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors"""
        return jsonify({'error': 'Endpoint not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors"""
        return jsonify({'error': 'Internal server error'}), 500 