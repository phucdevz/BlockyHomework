"""
AttackSimulator for BlockyHomework blockchain system.
51% attack simulation implementation.
"""

import time
import random
import threading
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
import json

from models.blockchain import Blockchain
from models.block import Block
from models.transaction import Transaction
from models.wallet import Wallet


class AttackSimulator:
    """
    Simulates various blockchain attacks for educational purposes.
    Supports 51% attacks, double-spending, selfish mining, and eclipse attacks.
    """
    
    def __init__(self):
        self.is_running = False
        self.current_scenario = None
        self.attack_progress = 0
        self.simulation_thread = None
        
        # Attack configuration
        self.attack_type = "51_percent"
        self.attack_power = 51  # Percentage of network hashpower
        self.attack_duration = 10  # Minutes
        self.network_size = 100  # Number of nodes
        
        # Simulation state
        self.legitimate_chain = Blockchain()
        self.attack_chain = Blockchain()
        self.attack_wallet = Wallet()
        
        # Metrics
        self.metrics = {
            'attack_success': False,
            'blocks_mined_attack': 0,
            'blocks_mined_legitimate': 0,
            'attack_duration_actual': 0,
            'network_impact': 0,
            'double_spend_success': False,
            'fork_resolution_time': 0
        }
        
        # Callbacks
        self.on_progress_update = None
        self.on_attack_complete = None
        self.on_metrics_update = None
        
        # Attack scenarios
        self.scenarios = {
            '51_percent': self._simulate_51_percent_attack,
            'double_spend': self._simulate_double_spend,
            'selfish_mining': self._simulate_selfish_mining,
            'eclipse': self._simulate_eclipse_attack
        }
    
    def start_simulation(self, scenario: str = "51_percent", 
                        attack_power: int = 51, 
                        duration: int = 10,
                        network_size: int = 100) -> bool:
        """
        Start an attack simulation.
        
        Args:
            scenario: Type of attack to simulate
            attack_power: Percentage of network hashpower controlled by attacker
            duration: Duration of attack in minutes
            network_size: Number of nodes in the network
            
        Returns:
            bool: True if simulation started successfully
        """
        if self.is_running:
            return False
        
        self.attack_type = scenario
        self.attack_power = attack_power
        self.attack_duration = duration
        self.network_size = network_size
        
        # Reset simulation state
        self._reset_simulation()
        
        # Start simulation thread
        self.is_running = True
        self.simulation_thread = threading.Thread(
            target=self._run_simulation,
            daemon=True
        )
        self.simulation_thread.start()
        
        return True
    
    def stop_simulation(self) -> bool:
        """Stop the current simulation."""
        if not self.is_running:
            return False
        
        self.is_running = False
        if self.simulation_thread:
            self.simulation_thread.join(timeout=5)
        
        return True
    
    def get_simulation_status(self) -> Dict[str, Any]:
        """Get current simulation status."""
        return {
            'is_running': self.is_running,
            'current_scenario': self.current_scenario,
            'attack_progress': self.attack_progress,
            'attack_type': self.attack_type,
            'attack_power': self.attack_power,
            'attack_duration': self.attack_duration,
            'network_size': self.network_size
        }
    
    def get_attack_metrics(self) -> Dict[str, Any]:
        """Get attack simulation metrics."""
        return self.metrics.copy()
    
    def get_chain_comparison(self) -> Dict[str, Any]:
        """Get comparison between legitimate and attack chains."""
        return {
            'legitimate_chain': {
                'length': len(self.legitimate_chain.chain),
                'blocks': [block.to_dict() for block in self.legitimate_chain.chain[-5:]]
            },
            'attack_chain': {
                'length': len(self.attack_chain.chain),
                'blocks': [block.to_dict() for block in self.attack_chain.chain[-5:]]
            }
        }
    
    def _reset_simulation(self):
        """Reset simulation state."""
        self.attack_progress = 0
        self.current_scenario = None
        self.legitimate_chain = Blockchain()
        self.attack_chain = Blockchain()
        self.attack_wallet = Wallet()
        
        # Reset metrics
        self.metrics = {
            'attack_success': False,
            'blocks_mined_attack': 0,
            'blocks_mined_legitimate': 0,
            'attack_duration_actual': 0,
            'network_impact': 0,
            'double_spend_success': False,
            'fork_resolution_time': 0
        }
    
    def _run_simulation(self):
        """Main simulation loop."""
        start_time = time.time()
        self.current_scenario = self.attack_type
        
        try:
            # Run the selected attack scenario
            if self.attack_type in self.scenarios:
                self.scenarios[self.attack_type]()
            else:
                self._simulate_51_percent_attack()
                
        except Exception as e:
            print(f"Simulation error: {e}")
        finally:
            self.is_running = False
            self.metrics['attack_duration_actual'] = time.time() - start_time
            
            if self.on_attack_complete:
                self.on_attack_complete(self.metrics)
    
    def _simulate_51_percent_attack(self):
        """Simulate a 51% attack."""
        print("Starting 51% attack simulation...")
        
        # Create initial legitimate chain
        self._mine_legitimate_blocks(5)
        
        # Start attack
        attack_start_time = time.time()
        target_duration = self.attack_duration * 60  # Convert to seconds
        
        while self.is_running and (time.time() - attack_start_time) < target_duration:
            # Calculate attack progress
            elapsed = time.time() - attack_start_time
            self.attack_progress = min(100, (elapsed / target_duration) * 100)
            
            # Simulate mining based on attack power
            if random.random() < (self.attack_power / 100):
                # Attacker mines a block
                self._mine_attack_block()
                self.metrics['blocks_mined_attack'] += 1
            else:
                # Legitimate network mines a block
                self._mine_legitimate_block()
                self.metrics['blocks_mined_legitimate'] += 1
            
            # Update progress callback
            if self.on_progress_update:
                self.on_progress_update(self.attack_progress)
            
            # Update metrics
            self._update_attack_metrics()
            
            time.sleep(1)  # Simulate time passing
        
        # Determine attack success
        self._evaluate_attack_success()
    
    def _simulate_double_spend(self):
        """Simulate a double-spend attack."""
        print("Starting double-spend attack simulation...")
        
        # Create initial legitimate chain
        self._mine_legitimate_blocks(3)
        
        # Create a legitimate transaction
        victim_wallet = Wallet()
        legitimate_tx = self.attack_wallet.create_transaction(
            victim_wallet.address, 10.0
        )
        self.legitimate_chain.add_transaction(legitimate_tx)
        self._mine_legitimate_block()
        
        # Start attack - create conflicting transaction
        attack_tx = self.attack_wallet.create_transaction(
            self.attack_wallet.address, 10.0  # Send to self instead
        )
        self.attack_chain.add_transaction(attack_tx)
        
        # Mine attack chain faster
        attack_start_time = time.time()
        target_duration = self.attack_duration * 60
        
        while self.is_running and (time.time() - attack_start_time) < target_duration:
            elapsed = time.time() - attack_start_time
            self.attack_progress = min(100, (elapsed / target_duration) * 100)
            
            # Attack chain mines faster
            if random.random() < 0.7:  # 70% chance for attack chain
                self._mine_attack_block()
                self.metrics['blocks_mined_attack'] += 1
            else:
                self._mine_legitimate_block()
                self.metrics['blocks_mined_legitimate'] += 1
            
            if self.on_progress_update:
                self.on_progress_update(self.attack_progress)
            
            time.sleep(1)
        
        # Check if double-spend was successful
        self.metrics['double_spend_success'] = (
            len(self.attack_chain.chain) > len(self.legitimate_chain.chain)
        )
    
    def _simulate_selfish_mining(self):
        """Simulate selfish mining attack."""
        print("Starting selfish mining simulation...")
        
        # Create initial legitimate chain
        self._mine_legitimate_blocks(3)
        
        attack_start_time = time.time()
        target_duration = self.attack_duration * 60
        
        while self.is_running and (time.time() - attack_start_time) < target_duration:
            elapsed = time.time() - attack_start_time
            self.attack_progress = min(100, (elapsed / target_duration) * 100)
            
            # Selfish mining strategy
            if random.random() < (self.attack_power / 100):
                # Attacker finds block but doesn't broadcast immediately
                self._mine_attack_block()
                self.metrics['blocks_mined_attack'] += 1
                
                # Wait and see if legitimate network finds a block
                time.sleep(2)
                
                if random.random() < 0.3:  # 30% chance legitimate network finds block
                    self._mine_legitimate_block()
                    self.metrics['blocks_mined_legitimate'] += 1
            else:
                # Legitimate network mines
                self._mine_legitimate_block()
                self.metrics['blocks_mined_legitimate'] += 1
            
            if self.on_progress_update:
                self.on_progress_update(self.attack_progress)
            
            time.sleep(1)
    
    def _simulate_eclipse_attack(self):
        """Simulate eclipse attack."""
        print("Starting eclipse attack simulation...")
        
        # Create initial legitimate chain
        self._mine_legitimate_blocks(3)
        
        attack_start_time = time.time()
        target_duration = self.attack_duration * 60
        
        while self.is_running and (time.time() - attack_start_time) < target_duration:
            elapsed = time.time() - attack_start_time
            self.attack_progress = min(100, (elapsed / target_duration) * 100)
            
            # Eclipse attack reduces legitimate network connectivity
            if random.random() < (self.attack_power / 100):
                # Attack blocks are mined
                self._mine_attack_block()
                self.metrics['blocks_mined_attack'] += 1
            else:
                # Legitimate network has reduced mining power due to eclipse
                if random.random() < 0.3:  # Only 30% chance due to eclipse
                    self._mine_legitimate_block()
                    self.metrics['blocks_mined_legitimate'] += 1
            
            if self.on_progress_update:
                self.on_progress_update(self.attack_progress)
            
            time.sleep(1)
    
    def _mine_legitimate_blocks(self, count: int):
        """Mine multiple legitimate blocks."""
        for _ in range(count):
            self._mine_legitimate_block()
    
    def _mine_legitimate_block(self):
        """Mine a single legitimate block."""
        # Create some transactions
        for _ in range(random.randint(1, 5)):
            tx = Transaction(
                sender="legitimate_sender",
                recipient="legitimate_recipient",
                amount=random.uniform(0.1, 5.0)
            )
            self.legitimate_chain.add_transaction(tx)
        
        # Mine the block
        block = self.legitimate_chain.mine_block("legitimate_miner")
        if block:
            self.metrics['blocks_mined_legitimate'] += 1
    
    def _mine_attack_block(self):
        """Mine a single attack block."""
        # Create attack transactions
        for _ in range(random.randint(1, 3)):
            tx = Transaction(
                sender=self.attack_wallet.address,
                recipient=self.attack_wallet.address,
                amount=random.uniform(0.1, 2.0)
            )
            self.attack_chain.add_transaction(tx)
        
        # Mine the block
        block = self.attack_chain.mine_block(self.attack_wallet.address)
        if block:
            self.metrics['blocks_mined_attack'] += 1
    
    def _evaluate_attack_success(self):
        """Evaluate if the attack was successful."""
        attack_chain_length = len(self.attack_chain.chain)
        legitimate_chain_length = len(self.legitimate_chain.chain)
        
        # Attack is successful if attack chain is longer
        self.metrics['attack_success'] = attack_chain_length > legitimate_chain_length
        
        # Calculate network impact
        total_blocks = attack_chain_length + legitimate_chain_length
        if total_blocks > 0:
            self.metrics['network_impact'] = (attack_chain_length / total_blocks) * 100
        
        # Calculate fork resolution time
        if self.metrics['attack_success']:
            self.metrics['fork_resolution_time'] = self.metrics['attack_duration_actual']
    
    def _update_attack_metrics(self):
        """Update attack metrics during simulation."""
        if self.on_metrics_update:
            self.on_metrics_update(self.metrics)
    
    def set_progress_callback(self, callback: Callable[[int], None]):
        """Set callback for progress updates."""
        self.on_progress_update = callback
    
    def set_completion_callback(self, callback: Callable[[Dict], None]):
        """Set callback for attack completion."""
        self.on_attack_complete = callback
    
    def set_metrics_callback(self, callback: Callable[[Dict], None]):
        """Set callback for metrics updates."""
        self.on_metrics_update = callback
    
    def export_simulation_report(self) -> Dict[str, Any]:
        """Export a comprehensive simulation report."""
        return {
            'simulation_info': {
                'attack_type': self.attack_type,
                'attack_power': self.attack_power,
                'duration': self.attack_duration,
                'network_size': self.network_size,
                'timestamp': datetime.now().isoformat()
            },
            'results': self.metrics,
            'chain_comparison': self.get_chain_comparison(),
            'success_rate': self._calculate_success_rate()
        }
    
    def _calculate_success_rate(self) -> float:
        """Calculate attack success rate based on metrics."""
        if self.metrics['attack_duration_actual'] == 0:
            return 0.0
        
        # Complex success rate calculation based on multiple factors
        power_factor = self.attack_power / 100
        duration_factor = min(1.0, self.metrics['attack_duration_actual'] / (self.attack_duration * 60))
        block_ratio = self.metrics['blocks_mined_attack'] / max(1, self.metrics['blocks_mined_attack'] + self.metrics['blocks_mined_legitimate'])
        
        success_rate = (power_factor * 0.4 + duration_factor * 0.3 + block_ratio * 0.3) * 100
        return min(100.0, success_rate) 