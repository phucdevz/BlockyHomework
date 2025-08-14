"""
Integration tests for BlockyHomework system.
Tests complete system integration including ViewModels, networking, and simulation.
"""

import unittest
import time
import json
from unittest.mock import Mock, patch, MagicMock

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from models.blockchain import Blockchain
from models.wallet import Wallet
from models.transaction import Transaction
from viewmodels.node_viewmodel import NodeViewModel
from viewmodels.blockchain_viewmodel import BlockchainViewModel
from viewmodels.wallet_viewmodel import WalletViewModel
from simulation.attack_simulator import AttackSimulator
from simulation.scenario_generator import ScenarioGenerator, AttackType


class TestSystemIntegration(unittest.TestCase):
    """Integration tests for the complete system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.blockchain = Blockchain()
        self.wallet = Wallet()
        self.node_viewmodel = NodeViewModel(self.blockchain, self.wallet)
        self.blockchain_viewmodel = BlockchainViewModel(self.blockchain)
        self.wallet_viewmodel = WalletViewModel(self.wallet, self.blockchain)
        self.attack_simulator = AttackSimulator()
        self.scenario_generator = ScenarioGenerator()
    
    def test_complete_transaction_flow(self):
        """Test complete transaction flow from creation to mining."""
        # 1. Create transaction
        recipient = "recipient_address"
        amount = 25.0
        transaction = self.wallet.create_transaction(recipient, amount)
        
        # 2. Add to blockchain mempool
        success = self.blockchain.add_transaction(transaction)
        self.assertTrue(success)
        
        # 3. Verify transaction in mempool
        pending_transactions = self.node_viewmodel.get_pending_transactions()
        self.assertEqual(len(pending_transactions), 1)
        self.assertEqual(pending_transactions[0]['amount'], amount)
        
        # 4. Mine block
        block = self.blockchain.mine_block(self.wallet.address)
        self.assertIsNotNone(block)
        
        # 5. Verify transaction is now confirmed
        confirmed_transactions = self.wallet_viewmodel.get_transaction_history()
        self.assertGreater(len(confirmed_transactions), 0)
        
        # 6. Check wallet balance
        balance = self.wallet_viewmodel.get_wallet_balance_display()
        self.assertIn("ZTL Coin", balance)
    
    def test_blockchain_synchronization(self):
        """Test blockchain synchronization between nodes."""
        # Create two blockchains
        blockchain1 = Blockchain()
        blockchain2 = Blockchain()
        
        # Add transactions and mine blocks on first blockchain
        wallet1 = Wallet()
        for i in range(3):
            transaction = wallet1.create_transaction("recipient", 10.0)
            blockchain1.add_transaction(transaction)
            block = blockchain1.mine_block(wallet1.address)
            self.assertIsNotNone(block)
        
        # Verify blockchain1 has more blocks
        self.assertGreater(len(blockchain1.chain), len(blockchain2.chain))
        
        # Synchronize blockchain2 with blockchain1
        success = blockchain2.replace_chain(blockchain1.chain)
        self.assertTrue(success)
        
        # Verify both blockchains are now synchronized
        self.assertEqual(len(blockchain1.chain), len(blockchain2.chain))
        self.assertEqual(blockchain1.chain[-1].hash, blockchain2.chain[-1].hash)
    
    def test_viewmodel_data_binding(self):
        """Test data binding between models and viewmodels."""
        # Create initial state
        initial_chain_length = self.blockchain_viewmodel.get_chain_display()
        initial_balance = self.wallet_viewmodel.get_wallet_balance_display()
        
        # Add transaction and mine block
        transaction = self.wallet.create_transaction("recipient", 15.0)
        self.blockchain.add_transaction(transaction)
        block = self.blockchain.mine_block(self.wallet.address)
        
        # Verify viewmodels reflect changes
        updated_chain_length = self.blockchain_viewmodel.get_chain_display()
        updated_balance = self.wallet_viewmodel.get_wallet_balance_display()
        
        self.assertNotEqual(len(initial_chain_length), len(updated_chain_length))
        self.assertNotEqual(initial_balance, updated_balance)
    
    def test_attack_simulation_integration(self):
        """Test attack simulation integration."""
        # Create a basic 51% attack scenario
        scenario = self.scenario_generator.create_custom_scenario(
            name="Test 51% Attack",
            attack_type=AttackType.FIFTY_ONE_PERCENT,
            description="Test attack for integration",
            attack_power=60,
            duration=1,  # Short duration for testing
            network_size=50
        )
        
        # Run the scenario
        result = self.scenario_generator.run_scenario(scenario)
        
        # Verify results
        self.assertIsNotNone(result)
        self.assertIsInstance(result.success, bool)
        self.assertIsInstance(result.metrics, dict)
        self.assertIsInstance(result.duration, float)
        self.assertGreater(result.duration, 0)
    
    def test_multiple_scenario_execution(self):
        """Test execution of multiple scenarios."""
        scenarios = []
        
        # Create multiple scenarios
        for i in range(3):
            scenario = self.scenario_generator.create_custom_scenario(
                name=f"Test Scenario {i}",
                attack_type=AttackType.FIFTY_ONE_PERCENT,
                description=f"Test scenario {i}",
                attack_power=50 + i * 10,
                duration=1,
                network_size=50
            )
            scenarios.append(scenario)
        
        # Run all scenarios
        results = self.scenario_generator.run_scenario_batch(scenarios)
        
        # Verify results
        self.assertEqual(len(results), 3)
        for result in results:
            self.assertIsNotNone(result)
            self.assertIsInstance(result.success, bool)
    
    def test_comparison_report_generation(self):
        """Test comparison report generation."""
        # Create and run multiple scenarios
        scenarios = []
        for i in range(2):
            scenario = self.scenario_generator.create_custom_scenario(
                name=f"Comparison Test {i}",
                attack_type=AttackType.FIFTY_ONE_PERCENT,
                description=f"Comparison test {i}",
                attack_power=55 + i * 5,
                duration=1,
                network_size=50
            )
            scenarios.append(scenario)
        
        results = self.scenario_generator.run_scenario_batch(scenarios)
        
        # Generate comparison report
        report = self.scenario_generator.generate_comparison_report(results)
        
        # Verify report structure
        self.assertIn('summary', report)
        self.assertIn('attack_type_analysis', report)
        self.assertIn('detailed_results', report)
        self.assertIn('recommendations', report)
        
        # Verify summary data
        summary = report['summary']
        self.assertEqual(summary['total_scenarios'], 2)
        self.assertIn('success_rate', summary)
        self.assertIn('avg_duration', summary)
    
    def test_wallet_transaction_history(self):
        """Test wallet transaction history tracking."""
        # Create multiple transactions
        transactions = []
        for i in range(5):
            transaction = self.wallet.create_transaction(f"recipient_{i}", 10.0)
            self.blockchain.add_transaction(transaction)
            transactions.append(transaction)
        
        # Mine blocks to confirm transactions
        for i in range(2):
            block = self.blockchain.mine_block(self.wallet.address)
            self.assertIsNotNone(block)
        
        # Get transaction history
        history = self.wallet_viewmodel.get_transaction_history()
        
        # Verify history contains transactions
        self.assertGreater(len(history), 0)
        
        # Verify transaction details
        for tx in history:
            self.assertIn('sender', tx)
            self.assertIn('recipient', tx)
            self.assertIn('amount', tx)
            self.assertIn('timestamp', tx)
    
    def test_blockchain_validation_integration(self):
        """Test blockchain validation in integrated system."""
        # Create a valid blockchain with multiple blocks
        for i in range(3):
            transaction = self.wallet.create_transaction(f"recipient_{i}", 10.0)
            self.blockchain.add_transaction(transaction)
            block = self.blockchain.mine_block(self.wallet.address)
            self.assertIsNotNone(block)
        
        # Verify blockchain is valid
        self.assertTrue(self.blockchain.validate_chain())
        
        # Verify chain length
        chain_length = self.blockchain_viewmodel.get_chain_display()
        self.assertEqual(len(chain_length), 4)  # Genesis + 3 mined blocks
        
        # Verify mining status
        mining_status = self.blockchain_viewmodel.get_mining_status_display()
        self.assertIn('difficulty', mining_status)
        self.assertIn('block_reward', mining_status)
        self.assertIn('chain_length', mining_status)
    
    def test_mempool_integration(self):
        """Test mempool integration with blockchain."""
        # Add multiple transactions to mempool
        for i in range(10):
            transaction = self.wallet.create_transaction(f"recipient_{i}", 5.0)
            self.blockchain.add_transaction(transaction)
        
        # Verify transactions in mempool
        pending_transactions = self.node_viewmodel.get_pending_transactions()
        self.assertEqual(len(pending_transactions), 10)
        
        # Mine a block
        block = self.blockchain.mine_block(self.wallet.address)
        self.assertIsNotNone(block)
        
        # Verify some transactions were moved from mempool to block
        remaining_pending = self.node_viewmodel.get_pending_transactions()
        self.assertLess(len(remaining_pending), 10)
        
        # Verify block contains transactions
        block_data = block.to_dict()
        self.assertGreater(len(block_data['transactions']), 1)  # Including reward transaction
    
    def test_attack_simulator_metrics(self):
        """Test attack simulator metrics collection."""
        # Start a simple attack simulation
        self.attack_simulator.attack_type = "51_percent"
        self.attack_simulator.attack_power = 60
        self.attack_simulator.attack_duration = 1
        self.attack_simulator.network_size = 50
        
        # Run simulation
        success = self.attack_simulator.start_simulation()
        self.assertTrue(success)
        
        # Wait for simulation to complete
        while self.attack_simulator.is_running:
            time.sleep(0.1)
        
        # Get metrics
        metrics = self.attack_simulator.get_attack_metrics()
        
        # Verify metrics structure
        self.assertIn('attack_success', metrics)
        self.assertIn('blocks_mined_attack', metrics)
        self.assertIn('blocks_mined_legitimate', metrics)
        self.assertIn('attack_duration_actual', metrics)
        self.assertIn('network_impact', metrics)
        
        # Verify metrics are reasonable
        self.assertIsInstance(metrics['attack_success'], bool)
        self.assertGreaterEqual(metrics['blocks_mined_attack'], 0)
        self.assertGreaterEqual(metrics['blocks_mined_legitimate'], 0)
        self.assertGreaterEqual(metrics['attack_duration_actual'], 0)
    
    def test_scenario_export_import(self):
        """Test scenario export and import functionality."""
        # Create a custom scenario
        scenario = self.scenario_generator.create_custom_scenario(
            name="Export Test Scenario",
            attack_type=AttackType.DOUBLE_SPEND,
            description="Test scenario for export/import",
            attack_power=70,
            duration=2,
            network_size=100
        )
        
        # Export scenario to dict
        scenario_dict = {
            'name': scenario.name,
            'attack_type': scenario.attack_type.value,
            'description': scenario.description,
            'attack_power': scenario.attack_power,
            'duration': scenario.duration,
            'network_size': scenario.network_size,
            'parameters': scenario.parameters,
            'difficulty': scenario.difficulty,
            'success_criteria': scenario.success_criteria
        }
        
        # Import scenario from dict
        imported_scenario = self.scenario_generator.create_custom_scenario(
            name=scenario_dict['name'],
            attack_type=AttackType(scenario_dict['attack_type']),
            description=scenario_dict['description'],
            attack_power=scenario_dict['attack_power'],
            duration=scenario_dict['duration'],
            network_size=scenario_dict['network_size'],
            parameters=scenario_dict['parameters'],
            difficulty=scenario_dict['difficulty']
        )
        
        # Verify imported scenario matches original
        self.assertEqual(imported_scenario.name, scenario.name)
        self.assertEqual(imported_scenario.attack_type, scenario.attack_type)
        self.assertEqual(imported_scenario.attack_power, scenario.attack_power)
        self.assertEqual(imported_scenario.duration, scenario.duration)
    
    def test_error_handling_integration(self):
        """Test error handling in integrated system."""
        # Test invalid transaction creation
        invalid_transaction = Transaction("sender", "recipient", -5.0)  # Negative amount
        success = self.blockchain.add_transaction(invalid_transaction)
        self.assertFalse(success)
        
        # Test mining with no transactions
        block = self.blockchain.mine_block(self.wallet.address)
        self.assertIsNone(block)
        
        # Test invalid wallet operations
        with self.assertRaises(Exception):
            # Try to create transaction with invalid recipient
            self.wallet.create_transaction("", 10.0)
        
        # Test attack simulator error handling
        # Start simulation with invalid parameters
        self.attack_simulator.attack_power = 0
        success = self.attack_simulator.start_simulation()
        self.assertFalse(success)  # Should fail with invalid parameters


class TestPerformanceIntegration(unittest.TestCase):
    """Performance integration tests."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.blockchain = Blockchain()
        self.wallet = Wallet()
    
    def test_large_transaction_processing(self):
        """Test processing of large number of transactions."""
        start_time = time.time()
        
        # Add many transactions
        for i in range(100):
            transaction = self.wallet.create_transaction(f"recipient_{i}", 1.0)
            self.blockchain.add_transaction(transaction)
        
        # Mine blocks
        blocks_mined = 0
        while len(self.blockchain.mempool.transactions) > 0:
            block = self.blockchain.mine_block(self.wallet.address)
            if block:
                blocks_mined += 1
            else:
                break
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Verify performance is reasonable
        self.assertLess(processing_time, 30)  # Should complete within 30 seconds
        self.assertGreater(blocks_mined, 0)
        
        # Verify all transactions were processed
        total_transactions = sum(len(block.transactions) for block in self.blockchain.chain)
        self.assertGreaterEqual(total_transactions, 100)
    
    def test_concurrent_operations(self):
        """Test concurrent operations on blockchain."""
        import threading
        
        results = []
        errors = []
        
        def mine_blocks():
            try:
                for i in range(5):
                    transaction = self.wallet.create_transaction(f"recipient_{i}", 5.0)
                    self.blockchain.add_transaction(transaction)
                    block = self.blockchain.mine_block(self.wallet.address)
                    if block:
                        results.append(block.index)
            except Exception as e:
                errors.append(str(e))
        
        # Start multiple threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=mine_blocks)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify no errors occurred
        self.assertEqual(len(errors), 0)
        
        # Verify some blocks were mined
        self.assertGreater(len(results), 0)
    
    def test_memory_usage(self):
        """Test memory usage with large blockchain."""
        import gc
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Create large blockchain
        for i in range(50):
            for j in range(10):
                transaction = self.wallet.create_transaction(f"recipient_{i}_{j}", 1.0)
                self.blockchain.add_transaction(transaction)
            block = self.blockchain.mine_block(self.wallet.address)
            self.assertIsNotNone(block)
        
        # Force garbage collection
        gc.collect()
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Verify memory usage is reasonable (less than 100MB increase)
        self.assertLess(memory_increase, 100 * 1024 * 1024)  # 100MB


if __name__ == '__main__':
    unittest.main()
