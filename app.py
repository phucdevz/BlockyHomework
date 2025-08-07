from flask import Flask, render_template, jsonify, request
import os
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

app = Flask(__name__, 
           template_folder='src/views/templates',
           static_folder='src/views/static')

# Import models
from models.blockchain import Blockchain
from models.wallet import Wallet

# Initialize blockchain
blockchain = Blockchain()
wallet = Wallet()

@app.route('/')
def dashboard():
    """Dashboard page"""
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

@app.route('/sitemap.xml')
def sitemap():
    """Generate sitemap.xml for SEO"""
    from flask import make_response
    from datetime import datetime
    
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
    from flask import make_response
    
    robots_txt = f'''User-agent: *
Allow: /

# Sitemap
Sitemap: {request.url_root}sitemap.xml

# Crawl-delay
Crawl-delay: 1'''
    
    response = make_response(robots_txt)
    response.headers["Content-Type"] = "text/plain"
    return response

# API Routes
@app.route('/api/blockchain/status')
def get_blockchain_status():
    """Get blockchain status"""
    return jsonify({
        'chain_length': blockchain.get_chain_length(),
        'difficulty': blockchain.difficulty,
        'pending_transactions': len(blockchain.mempool.transactions)
    })

@app.route('/api/wallet/balance')
def get_wallet_balance():
    """Get wallet balance"""
    balance = wallet.get_balance(blockchain)
    return jsonify({
        'address': wallet.address,
        'balance': balance
    })

@app.route('/api/mining/status')
def get_mining_status():
    """Get mining status"""
    return jsonify({
        'is_mining': False,
        'difficulty': blockchain.difficulty,
        'block_reward': blockchain.block_reward
    })

@app.route('/api/network/status')
def get_network_status():
    """Get network status"""
    return jsonify({
        'connected_nodes': 0,
        'network_status': 'disconnected',
        'sync_progress': 0
    })

@app.route('/api/transactions/create', methods=['POST'])
def create_transaction():
    """Create a new transaction"""
    data = request.get_json()
    
    if not data or 'recipient' not in data or 'amount' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        amount = float(data['amount'])
        if amount <= 0:
            return jsonify({'error': 'Amount must be positive'}), 400
            
        # Create transaction
        transaction = wallet.create_transaction(data['recipient'], amount)
        
        # Add to mempool
        if blockchain.add_transaction(transaction):
            return jsonify({
                'success': True,
                'transaction_hash': transaction.hash
            })
        else:
            return jsonify({'error': 'Failed to add transaction'}), 400
            
    except ValueError:
        return jsonify({'error': 'Invalid amount'}), 400

@app.route('/api/mining/start', methods=['POST'])
def start_mining():
    """Start mining"""
    return jsonify({'success': True, 'message': 'Mining started'})

@app.route('/api/mining/stop', methods=['POST'])
def stop_mining():
    """Stop mining"""
    return jsonify({'success': True, 'message': 'Mining stopped'})

@app.route('/api/mining/mine-block', methods=['POST'])
def mine_block():
    """Mine a single block"""
    try:
        block = blockchain.mine_block(wallet.address)
        if block:
            return jsonify({
                'success': True,
                'block_hash': block.hash,
                'block_index': block.index
            })
        else:
            return jsonify({'error': 'No transactions to mine'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting BlockyHomework Flask Server...")
    print("📱 Open your browser and go to: http://localhost:5000")
    print("🎨 The beautiful UI will now load with CSS and JS!")
    app.run(debug=True, host='0.0.0.0', port=5000) 