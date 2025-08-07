"""
NodeViewModel for BlockyHomework blockchain system.
Manages node state and coordinates between Model and View layers.
"""

from models.blockchain import Blockchain
from models.wallet import Wallet
from models.mempool import Mempool
from models.transaction import Transaction
from typing import List, Dict, Any

class NodeViewModel:
    def __init__(self, blockchain: Blockchain, wallet: Wallet):
        self.blockchain = blockchain
        self.wallet = wallet
        self.mempool = blockchain.mempool
        self.state = {
            'chain_display': self.format_chain(),
            'wallet_balance_display': self.format_balance(),
            'connected_nodes_display': [],
            'pending_transactions': self.format_pending_transactions()
        }

    def format_chain(self) -> List[Dict[str, Any]]:
        return [block.to_dict() for block in self.blockchain.chain]

    def format_balance(self) -> str:
        balance = self.wallet.get_balance(self.blockchain)
        return f"{balance:.3f} ZTL Coin"

    def format_pending_transactions(self) -> List[Dict[str, Any]]:
        return [tx.to_dict() for tx in self.mempool.get_transactions()]

    def create_new_transaction(self, recipient: str, amount: float) -> bool:
        tx = self.wallet.create_transaction(recipient, amount)
        return self.blockchain.add_transaction(tx)

    def mine_new_block(self) -> bool:
        block = self.blockchain.mine_block(self.wallet.address)
        if block:
            self.state['chain_display'] = self.format_chain()
            self.state['wallet_balance_display'] = self.format_balance()
            self.state['pending_transactions'] = self.format_pending_transactions()
            return True
        return False

    def synchronize_with_network(self, nodes: List[str]) -> None:
        self.state['connected_nodes_display'] = nodes

    def get_chain_display(self) -> List[Dict[str, Any]]:
        return self.state['chain_display']

    def get_wallet_balance_display(self) -> str:
        return self.state['wallet_balance_display']

    def get_connected_nodes_display(self) -> List[str]:
        return self.state['connected_nodes_display']

    def get_pending_transactions(self) -> List[Dict[str, Any]]:
        return self.state['pending_transactions'] 