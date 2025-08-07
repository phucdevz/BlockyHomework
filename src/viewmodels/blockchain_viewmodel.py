"""
BlockchainViewModel for BlockyHomework blockchain system.
Manages blockchain display and transaction list formatting.
"""

from models.blockchain import Blockchain
from typing import List, Dict, Any

class BlockchainViewModel:
    def __init__(self, blockchain: Blockchain):
        self.blockchain = blockchain
        self.state = {
            'chain_display': self.format_chain_for_ui(),
            'transaction_list': self.format_transaction_list(),
            'mining_status': self.get_mining_status(),
            'network_state': None
        }

    def format_chain_for_ui(self) -> List[Dict[str, Any]]:
        return [block.to_dict() for block in self.blockchain.chain]

    def format_transaction_list(self) -> List[Dict[str, Any]]:
        txs = []
        for block in self.blockchain.chain:
            for tx in block.transactions:
                txs.append(tx.to_dict())
        return txs

    def get_mining_status(self) -> Dict[str, Any]:
        return {
            'difficulty': self.blockchain.difficulty,
            'block_reward': self.blockchain.block_reward,
            'chain_length': len(self.blockchain.chain)
        }

    def set_network_state(self, state: Any):
        self.state['network_state'] = state

    def get_chain_display(self) -> List[Dict[str, Any]]:
        return self.state['chain_display']

    def get_transaction_list(self) -> List[Dict[str, Any]]:
        return self.state['transaction_list']

    def get_mining_status_display(self) -> Dict[str, Any]:
        return self.state['mining_status']

    def get_network_state(self) -> Any:
        return self.state['network_state'] 