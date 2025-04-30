"""
Glycolytic Query Investment Cycle (GQIC) - Resource allocation for query processing.

This module implements a biochemically-inspired approach to computational resource
allocation, following a three-phase cycle analogous to glycolysis:
1. Initiation - Identify potential information sources and establish initial resource requirements
2. Investment - Allocate computational resources based on expected return-on-investment 
3. Payoff - Harvest results and measure actual information gain

The system allocates computational resources based on expected information yield,
optimizing for information density while managing computational constraints.
"""
import logging
import math
import numpy as np
from typing import Dict, Any, List, Tuple, Optional, Union

class GlycolicQueryInvestmentCycle:
    """
    Implements a metabolic-inspired approach to computational resource allocation.
    
    This class manages the allocation of computational resources to different query
    components based on expected information yield, following principles inspired
    by cellular metabolism.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Glycolytic Query Investment Cycle.
        
        Args:
            config: Optional configuration parameters
        """
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Default investment parameters
        self.max_total_investment = self.config.get("max_total_investment", 100.0)
        self.min_component_investment = self.config.get("min_component_investment", 5.0)
        self.investment_threshold = self.config.get("investment_threshold", 0.3)
        
        # Historical ROI tracking for adaptive learning
        self.historical_roi = {}
        
        self.logger.info("Initialized Glycolytic Query Investment Cycle")
    
    def allocate_investments(self, decomposed_query: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """
        Allocate computational resources to query components.
        
        Args:
            decomposed_query: Dictionary containing decomposed query components
            
        Returns:
            Dictionary mapping components to their investment allocations
        """
        self.logger.debug(f"Allocating investments for {len(decomposed_query.get('sub_queries', []))} components")
        
        # Extract atomic components from the decomposed query
        components = decomposed_query.get("sub_queries", [])
        if not components:
            self.logger.warning("No components found in decomposed query")
            return {}
        
        # Calculate expected information gain for each component
        component_info_gains = self._calculate_expected_info_gains(components)
        
        # Calculate resource requirements for each component
        component_resources = self._estimate_resource_requirements(components)
        
        # Calculate ROI and determine allocations
        allocations = self._optimize_allocations(components, component_info_gains, component_resources)
        
        return allocations
    
    def harvest_results(self, investments: Dict[str, Dict[str, Any]], 
                         results: Dict[str, Any]) -> Tuple[Dict[str, Any], float]:
        """
        Harvest results and measure actual information gain.
        
        Args:
            investments: Dictionary of investment allocations
            results: Dictionary of results from component execution
            
        Returns:
            Tuple of processed results and total information payoff
        """
        self.logger.debug(f"Harvesting results from {len(results)} components")
        
        processed_results = {}
        total_payoff = 0.0
        
        for component_id, result in results.items():
            if component_id not in investments:
                continue
                
            # Calculate actual information gain
            actual_gain = self._measure_information_content(result)
            
            # Calculate ROI
            investment = investments[component_id]["allocation"]
            roi = actual_gain / max(investment, 0.001)  # Avoid division by zero
            
            # Update historical ROI for this component type
            component_type = investments[component_id].get("type", "generic")
            if component_type not in self.historical_roi:
                self.historical_roi[component_type] = []
            
            self.historical_roi[component_type].append(roi)
            
            # Truncate history if too long
            if len(self.historical_roi[component_type]) > 100:
                self.historical_roi[component_type] = self.historical_roi[component_type][-100:]
            
            # Track total payoff
            total_payoff += actual_gain
            
            # Add ROI information to processed results
            processed_results[component_id] = {
                "result": result,
                "info_gain": actual_gain,
                "roi": roi
            }
        
        self.logger.info(f"Total information payoff: {total_payoff:.2f}")
        return processed_results, total_payoff
    
    def _calculate_expected_info_gains(self, components: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Calculate expected information gain for each component.
        
        Args:
            components: List of query components
            
        Returns:
            Dictionary mapping component IDs to expected information gains
        """
        info_gains = {}
        
        for component in components:
            component_id = component.get("id", str(hash(str(component))))
            component_type = component.get("task_type", "generic")
            
            # Base information gain calculation based on component characteristics
            base_gain = self._calculate_base_info_gain(component)
            
            # Adjust based on historical ROI for this component type
            historical_adjustment = self._get_historical_adjustment(component_type)
            
            # Final expected information gain
            info_gains[component_id] = base_gain * historical_adjustment
            
        return info_gains
    
    def _calculate_base_info_gain(self, component: Dict[str, Any]) -> float:
        """
        Calculate base information gain for a component.
        
        Args:
            component: Query component
            
        Returns:
            Base information gain value
        """
        # Simple heuristic based on component attributes
        # In a real implementation, this would be more sophisticated
        gain = 10.0  # Default base gain
        
        # Adjust based on component complexity
        query = component.get("query", "")
        if isinstance(query, str):
            # Length-based heuristic
            gain += min(len(query) / 50, 10.0)
            
            # Keyword-based heuristics
            if "explain" in query.lower() or "elaborate" in query.lower():
                gain += 5.0
            if "compare" in query.lower() or "contrast" in query.lower():
                gain += 7.0
            if "calculate" in query.lower() or "compute" in query.lower():
                gain += 8.0
        
        # Adjust based on domain
        domain = component.get("domain", "")
        if domain == "biomechanics":
            gain *= 1.2
        elif domain == "physiology":
            gain *= 1.1
            
        return gain
    
    def _get_historical_adjustment(self, component_type: str) -> float:
        """
        Get historical ROI adjustment factor for a component type.
        
        Args:
            component_type: Type of component
            
        Returns:
            Adjustment factor based on historical ROI
        """
        if component_type not in self.historical_roi or not self.historical_roi[component_type]:
            return 1.0
            
        # Calculate adjustment based on recent historical ROI
        recent_roi = self.historical_roi[component_type][-10:]
        avg_roi = sum(recent_roi) / len(recent_roi)
        
        # Convert to adjustment factor
        # Higher historical ROI leads to higher adjustment (up to 1.5x)
        adjustment = min(1.5, max(0.5, 0.75 + avg_roi / 4.0))
        
        return adjustment
    
    def _estimate_resource_requirements(self, components: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Estimate resource requirements for each component.
        
        Args:
            components: List of query components
            
        Returns:
            Dictionary mapping component IDs to resource requirements
        """
        resources = {}
        
        for component in components:
            component_id = component.get("id", str(hash(str(component))))
            
            # Base resource estimation
            base_resources = self._calculate_base_resources(component)
            
            # Store estimated resources
            resources[component_id] = base_resources
            
        return resources
    
    def _calculate_base_resources(self, component: Dict[str, Any]) -> float:
        """
        Calculate base resource requirements for a component.
        
        Args:
            component: Query component
            
        Returns:
            Base resource requirement value
        """
        # Simple heuristic based on component attributes
        resources = 5.0  # Default base resources
        
        # Adjust based on component complexity
        query = component.get("query", "")
        if isinstance(query, str):
            # Length-based heuristic
            resources += min(len(query) / 30, 15.0)
            
            # Keyword-based heuristics
            if "detailed" in query.lower() or "comprehensive" in query.lower():
                resources += 10.0
            if "calculate" in query.lower() or "compute" in query.lower():
                resources += 15.0
            if "optimize" in query.lower() or "simulate" in query.lower():
                resources += 20.0
        
        # Adjust based on domain
        domain = component.get("domain", "")
        if domain == "biomechanics":
            resources *= 1.3
        elif domain == "physiology":
            resources *= 1.2
            
        # Adjust based on completion criteria complexity
        criteria = component.get("completion_criteria", {})
        if criteria:
            resources += len(criteria) * 2.0
            
        return resources
    
    def _optimize_allocations(self, components: List[Dict[str, Any]], 
                              info_gains: Dict[str, float],
                              resources: Dict[str, float]) -> Dict[str, Dict[str, Any]]:
        """
        Optimize resource allocations based on ROI.
        
        Args:
            components: List of query components
            info_gains: Dictionary of expected information gains
            resources: Dictionary of resource requirements
            
        Returns:
            Dictionary of optimized allocations
        """
        # Calculate ROI for each component
        roi_values = {}
        for component in components:
            component_id = component.get("id", str(hash(str(component))))
            if component_id in info_gains and component_id in resources:
                # ROI = information gain / resources
                roi = info_gains[component_id] / max(resources[component_id], 0.001)
                roi_values[component_id] = roi
        
        # Sort components by ROI
        sorted_components = sorted(
            [(component_id, roi) for component_id, roi in roi_values.items()],
            key=lambda x: x[1],
            reverse=True
        )
        
        # Allocate resources based on ROI and sigmoid scaling
        total_adjusted_roi = sum(roi for _, roi in sorted_components)
        
        allocations = {}
        remaining_investment = self.max_total_investment
        
        # First pass: allocate minimum investment to all components
        for component in components:
            component_id = component.get("id", str(hash(str(component))))
            if component_id in roi_values:
                allocations[component_id] = {
                    "allocation": self.min_component_investment,
                    "expected_return": info_gains.get(component_id, 0.0),
                    "roi": roi_values.get(component_id, 0.0),
                    "type": component.get("task_type", "generic")
                }
                remaining_investment -= self.min_component_investment
        
        # Second pass: allocate remaining investment proportionally to ROI
        if sorted_components and remaining_investment > 0:
            for component_id, roi in sorted_components:
                if roi < self.investment_threshold:
                    continue  # Skip low-ROI components
                    
                # Calculate proportional allocation
                allocation_share = (roi / total_adjusted_roi) * remaining_investment
                
                # Add to existing allocation
                if component_id in allocations:
                    allocations[component_id]["allocation"] += allocation_share
        
        self.logger.debug(f"Optimized allocations for {len(allocations)} components")
        return allocations
    
    def _measure_information_content(self, result: Any) -> float:
        """
        Measure actual information content of a result.
        
        Args:
            result: Result from component execution
            
        Returns:
            Information content measure
        """
        # In a real implementation, this would be more sophisticated
        # and might involve entropy calculations, semantic density, etc.
        
        if result is None:
            return 0.0
            
        if isinstance(result, dict):
            # Approximate information content based on dictionary size and depth
            return self._measure_dict_info_content(result)
        elif isinstance(result, list):
            # Approximate information content based on list size and complexity
            return self._measure_list_info_content(result)
        elif isinstance(result, str):
            # Approximate information content based on string length and complexity
            return self._measure_string_info_content(result)
        else:
            # Default measure for other types
            return 5.0
    
    def _measure_dict_info_content(self, data: Dict) -> float:
        """
        Measure information content of a dictionary.
        
        Args:
            data: Dictionary to measure
            
        Returns:
            Information content measure
        """
        if not data:
            return 0.0
            
        # Base content from keys and values
        base_content = len(data) * 2.0
        
        # Add content from nested structures
        for key, value in data.items():
            if isinstance(value, dict):
                base_content += self._measure_dict_info_content(value) * 0.8  # Discount for nesting
            elif isinstance(value, list):
                base_content += self._measure_list_info_content(value) * 0.8  # Discount for nesting
            elif isinstance(value, str):
                base_content += min(len(value) / 100, 5.0)  # Cap string contribution
                
        return base_content
    
    def _measure_list_info_content(self, data: List) -> float:
        """
        Measure information content of a list.
        
        Args:
            data: List to measure
            
        Returns:
            Information content measure
        """
        if not data:
            return 0.0
            
        # Base content from list size
        base_content = len(data) * 1.0
        
        # Sample list items if the list is large
        sample_size = min(len(data), 10)
        sample = data[:sample_size]
        
        # Add content from sampled items
        for item in sample:
            if isinstance(item, dict):
                base_content += self._measure_dict_info_content(item) * 0.8 / sample_size
            elif isinstance(item, list):
                base_content += self._measure_list_info_content(item) * 0.7 / sample_size
            elif isinstance(item, str):
                base_content += min(len(item) / 200, 2.0) / sample_size
                
        # Scale up based on full list size
        if sample_size < len(data):
            base_content *= (1.0 + math.log(len(data) / sample_size))
                
        return base_content
    
    def _measure_string_info_content(self, data: str) -> float:
        """
        Measure information content of a string.
        
        Args:
            data: String to measure
            
        Returns:
            Information content measure
        """
        if not data:
            return 0.0
            
        # Base content from string length
        base_content = min(len(data) / 50, 20.0)
        
        # Adjust for information density indicators
        if ":" in data:  # Key-value pairs indicator
            base_content *= 1.2
        if any(char.isdigit() for char in data):  # Numerical content
            base_content *= 1.3
        if len(data.split()) > 3:  # More than a trivial phrase
            base_content *= (1.0 + min(len(data.split()) / 100, 0.5))
            
        return base_content 