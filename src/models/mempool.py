from typing import List, Dict, Any, Optional
from .transaction import Transaction


class Mempool:
    def __init__(self):
        self.transactions = []
        self.max_size = 1000
    
    def add_transaction(self, transaction: Transaction) -> bool:
        if not transaction.is_valid():
            return False
        
        if len(self.transactions) >= self.max_size:
            return False
        
        if transaction.hash in [tx.hash for tx in self.transactions]:
            return False
        
        self.transactions.append(transaction)
        return True
    
    def remove_transaction(self, transaction_hash: str) -> bool:
        for i, transaction in enumerate(self.transactions):
            if transaction.hash == transaction_hash:
                del self.transactions[i]
                return True
        return False
    
    def get_transactions(self, limit: int = None) -> List[Transaction]:
        if limit is None:
            return self.transactions.copy()
        return self.transactions[:limit]
    
    def get_transaction_by_hash(self, transaction_hash: str) -> Optional[Transaction]:
        for transaction in self.transactions:
            if transaction.hash == transaction_hash:
                return transaction
        return None
    
    def clear_transactions(self, transaction_hashes: List[str]):
        self.transactions = [tx for tx in self.transactions if tx.hash not in transaction_hashes]
    
    def get_pending_transactions(self) -> List[Transaction]:
        return self.transactions.copy()
    
    def get_transaction_count(self) -> int:
        return len(self.transactions)
    
    def is_full(self) -> bool:
        return len(self.transactions) >= self.max_size
    
    def calculate_fee(self, transaction: Transaction) -> float:
        return max(0.001, transaction.amount * 0.001)
    
    def prioritize_transactions(self) -> List[Transaction]:
        sorted_transactions = sorted(
            self.transactions,
            key=lambda tx: (self.calculate_fee(tx), tx.timestamp),
            reverse=True
        )
        return sorted_transactions
    
    def get_transactions_for_block(self, max_transactions: int = 100) -> List[Transaction]:
        prioritized = self.prioritize_transactions()
        return prioritized[:max_transactions]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'transactions': [tx.to_dict() for tx in self.transactions],
            'max_size': self.max_size,
            'current_size': len(self.transactions)
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Mempool':
        mempool = cls()
        mempool.max_size = data.get('max_size', 1000)
        
        for tx_data in data.get('transactions', []):
            transaction = Transaction.from_dict(tx_data)
            mempool.transactions.append(transaction)
        
        return mempool
    
    def __str__(self) -> str:
        return f"Mempool: {len(self.transactions)} transactions"
    
    def __repr__(self) -> str:
        return f"Mempool(transactions={len(self.transactions)}, max_size={self.max_size})" 