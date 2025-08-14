"""
ScenarioGenerator for BlockyHomework blockchain system.
Creates and manages attack simulation scenarios.
"""

import json
import random
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

from .attack_simulator import AttackSimulator


class AttackType(Enum):
    """Types of blockchain attacks."""
    FIFTY_ONE_PERCENT = "51_percent"
    DOUBLE_SPEND = "double_spend"
    SELFISH_MINING = "selfish_mining"
    ECLIPSE = "eclipse"
    SYBIL = "sybil"
    ROUTING = "routing"


@dataclass
class AttackScenario:
    """Represents an attack simulation scenario."""
    name: str
    attack_type: AttackType
    description: str
    attack_power: int
    duration: int
    network_size: int
    parameters: Dict[str, Any]
    difficulty: str  # "easy", "medium", "hard"
    success_criteria: Dict[str, Any]
    created_at: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()


@dataclass
class SimulationResult:
    """Represents the result of a simulation."""
    scenario_name: str
    attack_type: str
    success: bool
    metrics: Dict[str, Any]
    duration: float
    timestamp: str
    chain_comparison: Dict[str, Any]
    analysis: Dict[str, Any]


class ScenarioGenerator:
    """
    Generates and manages attack simulation scenarios.
    Provides predefined scenarios and custom scenario creation.
    """
    
    def __init__(self):
        self.predefined_scenarios = self._create_predefined_scenarios()
        self.custom_scenarios = {}
        self.simulation_history = []
        self.attack_simulator = AttackSimulator()
    
    def get_predefined_scenarios(self) -> List[AttackScenario]:
        """Get list of predefined attack scenarios."""
        return list(self.predefined_scenarios.values())
    
    def get_custom_scenarios(self) -> List[AttackScenario]:
        """Get list of custom attack scenarios."""
        return list(self.custom_scenarios.values())
    
    def create_custom_scenario(self, name: str, attack_type: AttackType,
                             description: str, attack_power: int,
                             duration: int, network_size: int,
                             parameters: Dict[str, Any] = None,
                             difficulty: str = "medium") -> AttackScenario:
        """
        Create a custom attack scenario.
        
        Args:
            name: Scenario name
            attack_type: Type of attack
            description: Scenario description
            attack_power: Attack power percentage
            duration: Attack duration in minutes
            network_size: Network size
            parameters: Additional parameters
            difficulty: Scenario difficulty
            
        Returns:
            AttackScenario: Created scenario
        """
        if parameters is None:
            parameters = {}
        
        scenario = AttackScenario(
            name=name,
            attack_type=attack_type,
            description=description,
            attack_power=attack_power,
            duration=duration,
            network_size=network_size,
            parameters=parameters,
            difficulty=difficulty,
            success_criteria=self._get_default_success_criteria(attack_type)
        )
        
        self.custom_scenarios[name] = scenario
        return scenario
    
    def run_scenario(self, scenario: AttackScenario) -> SimulationResult:
        """
        Run a specific attack scenario.
        
        Args:
            scenario: Attack scenario to run
            
        Returns:
            SimulationResult: Simulation results
        """
        start_time = datetime.now()
        
        # Configure simulator
        self.attack_simulator.attack_type = scenario.attack_type.value
        self.attack_simulator.attack_power = scenario.attack_power
        self.attack_simulator.attack_duration = scenario.duration
        self.attack_simulator.network_size = scenario.network_size
        
        # Start simulation
        success = self.attack_simulator.start_simulation(
            scenario=scenario.attack_type.value,
            attack_power=scenario.attack_power,
            duration=scenario.duration,
            network_size=scenario.network_size
        )
        
        if not success:
            raise RuntimeError("Failed to start simulation")
        
        # Wait for simulation to complete
        while self.attack_simulator.is_running:
            import time
            time.sleep(0.1)
        
        # Get results
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        metrics = self.attack_simulator.get_attack_metrics()
        chain_comparison = self.attack_simulator.get_chain_comparison()
        
        # Create result
        result = SimulationResult(
            scenario_name=scenario.name,
            attack_type=scenario.attack_type.value,
            success=metrics['attack_success'],
            metrics=metrics,
            duration=duration,
            timestamp=end_time.isoformat(),
            chain_comparison=chain_comparison,
            analysis=self._analyze_results(scenario, metrics, chain_comparison)
        )
        
        # Store in history
        self.simulation_history.append(result)
        
        return result
    
    def run_scenario_batch(self, scenarios: List[AttackScenario]) -> List[SimulationResult]:
        """
        Run multiple scenarios in batch.
        
        Args:
            scenarios: List of scenarios to run
            
        Returns:
            List[SimulationResult]: Results for all scenarios
        """
        results = []
        
        for scenario in scenarios:
            try:
                result = self.run_scenario(scenario)
                results.append(result)
            except Exception as e:
                print(f"Error running scenario {scenario.name}: {e}")
                # Create error result
                error_result = SimulationResult(
                    scenario_name=scenario.name,
                    attack_type=scenario.attack_type.value,
                    success=False,
                    metrics={'error': str(e)},
                    duration=0,
                    timestamp=datetime.now().isoformat(),
                    chain_comparison={},
                    analysis={'error': str(e)}
                )
                results.append(error_result)
        
        return results
    
    def generate_comparison_report(self, results: List[SimulationResult]) -> Dict[str, Any]:
        """
        Generate a comparison report for multiple simulation results.
        
        Args:
            results: List of simulation results
            
        Returns:
            Dict: Comparison report
        """
        if not results:
            return {}
        
        # Calculate statistics
        total_scenarios = len(results)
        successful_attacks = sum(1 for r in results if r.success)
        success_rate = (successful_attacks / total_scenarios) * 100
        
        # Average metrics
        avg_duration = sum(r.duration for r in results) / total_scenarios
        avg_network_impact = sum(r.metrics.get('network_impact', 0) for r in results) / total_scenarios
        
        # Group by attack type
        attack_type_stats = {}
        for result in results:
            attack_type = result.attack_type
            if attack_type not in attack_type_stats:
                attack_type_stats[attack_type] = {
                    'count': 0,
                    'successful': 0,
                    'avg_duration': 0,
                    'avg_network_impact': 0
                }
            
            stats = attack_type_stats[attack_type]
            stats['count'] += 1
            if result.success:
                stats['successful'] += 1
            stats['avg_duration'] += result.duration
            stats['avg_network_impact'] += result.metrics.get('network_impact', 0)
        
        # Calculate averages for each attack type
        for attack_type, stats in attack_type_stats.items():
            count = stats['count']
            stats['avg_duration'] /= count
            stats['avg_network_impact'] /= count
            stats['success_rate'] = (stats['successful'] / count) * 100
        
        return {
            'summary': {
                'total_scenarios': total_scenarios,
                'successful_attacks': successful_attacks,
                'success_rate': success_rate,
                'avg_duration': avg_duration,
                'avg_network_impact': avg_network_impact
            },
            'attack_type_analysis': attack_type_stats,
            'detailed_results': [asdict(result) for result in results],
            'recommendations': self._generate_recommendations(results)
        }
    
    def export_report(self, results: List[SimulationResult], 
                     filename: str = None) -> str:
        """
        Export simulation results to a JSON report file.
        
        Args:
            results: List of simulation results
            filename: Output filename (optional)
            
        Returns:
            str: Path to exported file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"blockchain_attack_report_{timestamp}.json"
        
        report = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'total_scenarios': len(results),
                'generator_version': '1.0.0'
            },
            'comparison_report': self.generate_comparison_report(results),
            'individual_results': [asdict(result) for result in results]
        }
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        return filename
    
    def _create_predefined_scenarios(self) -> Dict[str, AttackScenario]:
        """Create predefined attack scenarios."""
        scenarios = {}
        
        # 51% Attack Scenarios
        scenarios['51_percent_basic'] = AttackScenario(
            name="Basic 51% Attack",
            attack_type=AttackType.FIFTY_ONE_PERCENT,
            description="Standard 51% attack with moderate network control",
            attack_power=51,
            duration=10,
            network_size=100,
            parameters={'strategy': 'continuous_mining'},
            difficulty="medium",
            success_criteria={'min_blocks_ahead': 2}
        )
        
        scenarios['51_percent_aggressive'] = AttackScenario(
            name="Aggressive 51% Attack",
            attack_type=AttackType.FIFTY_ONE_PERCENT,
            description="High-power 51% attack with maximum network control",
            attack_power=75,
            duration=15,
            network_size=200,
            parameters={'strategy': 'aggressive_mining'},
            difficulty="hard",
            success_criteria={'min_blocks_ahead': 5}
        )
        
        # Double Spend Scenarios
        scenarios['double_spend_basic'] = AttackScenario(
            name="Basic Double Spend",
            attack_type=AttackType.DOUBLE_SPEND,
            description="Simple double-spend attack on a single transaction",
            attack_power=60,
            duration=8,
            network_size=50,
            parameters={'target_transaction': 'random'},
            difficulty="easy",
            success_criteria={'double_spend_success': True}
        )
        
        scenarios['double_spend_advanced'] = AttackScenario(
            name="Advanced Double Spend",
            attack_type=AttackType.DOUBLE_SPEND,
            description="Complex double-spend with multiple transactions",
            attack_power=70,
            duration=12,
            network_size=100,
            parameters={'target_transaction': 'multiple', 'confirmation_depth': 3},
            difficulty="hard",
            success_criteria={'double_spend_success': True, 'min_transactions': 3}
        )
        
        # Selfish Mining Scenarios
        scenarios['selfish_mining_basic'] = AttackScenario(
            name="Basic Selfish Mining",
            attack_type=AttackType.SELFISH_MINING,
            description="Simple selfish mining strategy",
            attack_power=40,
            duration=10,
            network_size=80,
            parameters={'withhold_blocks': True},
            difficulty="medium",
            success_criteria={'revenue_increase': 0.1}
        )
        
        scenarios['selfish_mining_advanced'] = AttackScenario(
            name="Advanced Selfish Mining",
            attack_type=AttackType.SELFISH_MINING,
            description="Advanced selfish mining with dynamic strategy",
            attack_power=45,
            duration=15,
            network_size=150,
            parameters={'withhold_blocks': True, 'dynamic_strategy': True},
            difficulty="hard",
            success_criteria={'revenue_increase': 0.2}
        )
        
        # Eclipse Attack Scenarios
        scenarios['eclipse_basic'] = AttackScenario(
            name="Basic Eclipse Attack",
            attack_type=AttackType.ECLIPSE,
            description="Simple eclipse attack isolating target nodes",
            attack_power=30,
            duration=6,
            network_size=60,
            parameters={'target_nodes': 'random'},
            difficulty="medium",
            success_criteria={'isolated_nodes': 0.3}
        )
        
        scenarios['eclipse_advanced'] = AttackScenario(
            name="Advanced Eclipse Attack",
            attack_type=AttackType.ECLIPSE,
            description="Advanced eclipse attack with network manipulation",
            attack_power=50,
            duration=10,
            network_size=120,
            parameters={'target_nodes': 'strategic', 'network_manipulation': True},
            difficulty="hard",
            success_criteria={'isolated_nodes': 0.5}
        )
        
        return scenarios
    
    def _get_default_success_criteria(self, attack_type: AttackType) -> Dict[str, Any]:
        """Get default success criteria for an attack type."""
        criteria = {
            AttackType.FIFTY_ONE_PERCENT: {
                'min_blocks_ahead': 2,
                'network_impact': 0.6
            },
            AttackType.DOUBLE_SPEND: {
                'double_spend_success': True,
                'confirmation_depth': 1
            },
            AttackType.SELFISH_MINING: {
                'revenue_increase': 0.1,
                'block_advantage': 1
            },
            AttackType.ECLIPSE: {
                'isolated_nodes': 0.3,
                'network_fragmentation': 0.5
            }
        }
        
        return criteria.get(attack_type, {})
    
    def _analyze_results(self, scenario: AttackScenario, 
                        metrics: Dict[str, Any], 
                        chain_comparison: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze simulation results."""
        analysis = {
            'scenario_evaluation': self._evaluate_scenario_success(scenario, metrics),
            'attack_effectiveness': self._calculate_attack_effectiveness(metrics),
            'network_resilience': self._assess_network_resilience(metrics, chain_comparison),
            'risk_assessment': self._assess_attack_risk(scenario, metrics),
            'mitigation_suggestions': self._suggest_mitigations(scenario, metrics)
        }
        
        return analysis
    
    def _evaluate_scenario_success(self, scenario: AttackScenario, 
                                 metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate if the scenario met its success criteria."""
        success_met = True
        failed_criteria = []
        
        for criterion, target_value in scenario.success_criteria.items():
            actual_value = metrics.get(criterion, 0)
            
            if isinstance(target_value, bool):
                if actual_value != target_value:
                    success_met = False
                    failed_criteria.append(criterion)
            elif isinstance(target_value, (int, float)):
                if actual_value < target_value:
                    success_met = False
                    failed_criteria.append(criterion)
        
        return {
            'overall_success': success_met,
            'failed_criteria': failed_criteria,
            'success_rate': self._calculate_success_rate(metrics)
        }
    
    def _calculate_attack_effectiveness(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate attack effectiveness metrics."""
        total_blocks = metrics.get('blocks_mined_attack', 0) + metrics.get('blocks_mined_legitimate', 0)
        attack_ratio = metrics.get('blocks_mined_attack', 0) / max(1, total_blocks)
        
        return {
            'attack_ratio': attack_ratio,
            'network_impact': metrics.get('network_impact', 0),
            'efficiency_score': attack_ratio * (metrics.get('attack_power', 0) / 100)
        }
    
    def _assess_network_resilience(self, metrics: Dict[str, Any], 
                                 chain_comparison: Dict[str, Any]) -> Dict[str, Any]:
        """Assess network resilience against the attack."""
        legitimate_blocks = len(chain_comparison.get('legitimate_chain', {}).get('blocks', []))
        attack_blocks = len(chain_comparison.get('attack_chain', {}).get('blocks', []))
        
        resilience_score = 0
        if legitimate_blocks > 0:
            resilience_score = legitimate_blocks / max(1, legitimate_blocks + attack_blocks)
        
        return {
            'resilience_score': resilience_score,
            'legitimate_chain_strength': legitimate_blocks,
            'attack_chain_strength': attack_blocks,
            'consensus_stability': 1 - metrics.get('network_impact', 0) / 100
        }
    
    def _assess_attack_risk(self, scenario: AttackScenario, 
                          metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Assess the risk level of the attack."""
        risk_factors = {
            'attack_power': scenario.attack_power / 100,
            'duration': scenario.duration / 60,  # Convert to hours
            'network_size': scenario.network_size / 1000,  # Normalize
            'success_rate': metrics.get('attack_success', False)
        }
        
        overall_risk = sum(risk_factors.values()) / len(risk_factors)
        
        risk_level = "low"
        if overall_risk > 0.7:
            risk_level = "high"
        elif overall_risk > 0.4:
            risk_level = "medium"
        
        return {
            'overall_risk': overall_risk,
            'risk_level': risk_level,
            'risk_factors': risk_factors
        }
    
    def _suggest_mitigations(self, scenario: AttackScenario, 
                           metrics: Dict[str, Any]) -> List[str]:
        """Suggest mitigation strategies based on attack results."""
        mitigations = []
        
        if scenario.attack_type == AttackType.FIFTY_ONE_PERCENT:
            if metrics.get('attack_success', False):
                mitigations.extend([
                    "Implement stronger consensus mechanisms",
                    "Increase network decentralization",
                    "Add checkpoint mechanisms",
                    "Implement chain reorganization limits"
                ])
        
        elif scenario.attack_type == AttackType.DOUBLE_SPEND:
            if metrics.get('double_spend_success', False):
                mitigations.extend([
                    "Increase confirmation requirements",
                    "Implement transaction finality",
                    "Add double-spend detection",
                    "Use multi-signature transactions"
                ])
        
        elif scenario.attack_type == AttackType.SELFISH_MINING:
            if metrics.get('revenue_increase', 0) > 0.1:
                mitigations.extend([
                    "Implement uncle block rewards",
                    "Add selfish mining detection",
                    "Use alternative consensus mechanisms",
                    "Implement block withholding penalties"
                ])
        
        elif scenario.attack_type == AttackType.ECLIPSE:
            if metrics.get('isolated_nodes', 0) > 0.3:
                mitigations.extend([
                    "Implement peer diversity requirements",
                    "Add network topology monitoring",
                    "Use secure peer discovery",
                    "Implement connection limits"
                ])
        
        return mitigations
    
    def _calculate_success_rate(self, metrics: Dict[str, Any]) -> float:
        """Calculate overall success rate based on metrics."""
        factors = [
            metrics.get('attack_success', False),
            metrics.get('network_impact', 0) / 100,
            metrics.get('blocks_mined_attack', 0) / max(1, metrics.get('blocks_mined_attack', 0) + metrics.get('blocks_mined_legitimate', 0))
        ]
        
        return sum(factors) / len(factors) * 100 