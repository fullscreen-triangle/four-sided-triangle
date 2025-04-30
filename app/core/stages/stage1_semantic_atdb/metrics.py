import logging
from typing import Dict, Any
import time

logger = logging.getLogger(__name__)

class MetricsAnalyzer:
    """
    Records and analyzes metrics for the Semantic ATDB service.
    
    This class tracks metrics about the performance of the semantic analysis
    and throttle detection to enable system optimization.
    """
    
    def __init__(self):
        """Initialize the metrics analyzer."""
        # In a production system, this would connect to a metrics storage system
        self.metrics_history = {
            "analysis": [],
            "throttle": []
        }
    
    def record_analysis_metrics(self, analysis: Dict[str, Any]) -> None:
        """
        Record metrics about semantic analysis.
        
        Args:
            analysis: The semantic analysis result
        """
        # Extract key metrics
        parameter_count = len(analysis.get("parametersOfInterest", []))
        confidence = analysis.get("confidence", 0)
        reasoning_length = len(analysis.get("reasoning", ""))
        
        # Record metrics
        metrics = {
            "timestamp": time.time(),
            "parameter_count": parameter_count,
            "confidence": confidence,
            "reasoning_length": reasoning_length,
            "intent": analysis.get("intentClassification", "unknown")
        }
        
        self.metrics_history["analysis"].append(metrics)
        
        # In a real system, we would send these to a metrics service
        logger.debug(f"Recorded analysis metrics: {metrics}")
    
    def record_throttle_metrics(self, throttle_detection: Dict[str, Any]) -> None:
        """
        Record metrics about throttle detection.
        
        Args:
            throttle_detection: The throttle detection result
        """
        # Extract key metrics
        is_throttled = throttle_detection.get("is_throttled", False)
        pattern = throttle_detection.get("pattern", None)
        confidence = throttle_detection.get("confidence", 0)
        metrics = throttle_detection.get("metrics", {})
        
        # Record metrics
        record = {
            "timestamp": time.time(),
            "is_throttled": is_throttled,
            "pattern": pattern,
            "confidence": confidence,
            "detail_metrics": metrics
        }
        
        self.metrics_history["throttle"].append(record)
        
        # In a real system, we would send these to a metrics service
        logger.debug(f"Recorded throttle metrics: {record}")
        
    def get_throttling_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about throttling detection.
        
        Returns:
            Statistics about throttling detection
        """
        throttle_records = self.metrics_history["throttle"]
        
        # Calculate throttling rate
        if not throttle_records:
            return {"throttle_rate": 0, "pattern_distribution": {}}
            
        throttle_count = sum(1 for record in throttle_records if record["is_throttled"])
        throttle_rate = throttle_count / len(throttle_records)
        
        # Calculate pattern distribution
        pattern_counts = {}
        for record in throttle_records:
            if record["is_throttled"] and record["pattern"]:
                pattern = record["pattern"]
                pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
        
        # Calculate pattern distribution percentages
        pattern_distribution = {}
        if throttle_count > 0:
            for pattern, count in pattern_counts.items():
                pattern_distribution[pattern] = count / throttle_count
        
        return {
            "throttle_rate": throttle_rate,
            "pattern_distribution": pattern_distribution,
            "total_records": len(throttle_records),
            "throttled_count": throttle_count
        }
