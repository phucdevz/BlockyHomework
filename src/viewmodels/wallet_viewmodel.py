"""
WalletViewModel for BlockyHomework blockchain system.
Manages wallet display and balance formatting.
"""

from models.wallet import Wallet
from models.blockchain import Blockchain
from typing import List, Dict, Any

class WalletViewModel:
    def __init__(self, wallet: Wallet, blockchain: Blockchain):
        self.wallet = wallet
        self.blockchain = blockchain
        self.state = {
            'wallet_balance_display': self.format_balance_for_display(),
            'transaction_history': self.format_transaction_history(),
            'address_display': self.format_address()
        }

    def format_balance_for_display(self) -> str:
        balance = self.wallet.get_balance(self.blockchain)
        return f"{balance:.3f} ZTL Coin"

    def format_transaction_history(self) -> List[Dict[str, Any]]:
        history = self.wallet.get_transaction_history(self.blockchain)
        return [tx.to_dict() for tx in history]

    def format_address(self) -> str:
        return self.wallet.address

    def get_wallet_balance_display(self) -> str:
        return self.state['wallet_balance_display']

    def get_transaction_history(self) -> List[Dict[str, Any]]:
        return self.state['transaction_history']

    def get_address_display(self) -> str:
        return self.state['address_display'] 