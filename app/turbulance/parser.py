"""
Turbulance DSL Parser

This module parses Turbulance DSL scripts (.trb files) and extracts:
- Pipeline stage calls
- Computation requests  
- Variable assignments
- Research protocol structure

It also generates the three auxiliary files:
- .fs files (network graph consciousness state)
- .ghd files (resource orchestration dependencies) 
- .hre files (metacognitive decision memory)
"""

import re
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)

class TurbulanceNodeType(Enum):
    """Types of nodes in a Turbulance script"""
    PIPELINE_CALL = "pipeline_call"
    COMPUTATION = "computation"
    VARIABLE_ASSIGNMENT = "variable_assignment"
    CONDITION = "condition"
    LOOP = "loop"
    COMMENT = "comment"
    IMPORT = "import"

@dataclass
class TurbulanceNode:
    """Represents a parsed node in a Turbulance script"""
    node_type: TurbulanceNodeType
    line_number: int
    content: str
    parsed_data: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)

@dataclass
class TurbulanceScript:
    """Represents a complete parsed Turbulance script"""
    protocol_name: str
    nodes: List[TurbulanceNode]
    variables: Dict[str, Any] = field(default_factory=dict)
    pipeline_calls: List[TurbulanceNode] = field(default_factory=list)
    computations: List[TurbulanceNode] = field(default_factory=list)
    dependencies: Dict[str, List[str]] = field(default_factory=dict)
    
class TurbulanceParser:
    """Parser for Turbulance DSL scripts"""
    
    def __init__(self):
        self.pipeline_stages = [
            "query_processor", "context_analyzer", "domain_expert", 
            "evidence_synthesizer", "uncertainty_quantifier", 
            "result_interpreter", "quality_assessor", "response_generator"
        ]
        
        # Regex patterns for parsing
        self.patterns = {
            'pipeline_call': re.compile(r'(\w+)\s*=\s*pipeline_stage\(\s*"([^"]+)"\s*,?\s*([^)]*)\)'),
            'computation': re.compile(r'(\w+)\s*=\s*compute\(\s*([^)]+)\)'),
            'variable': re.compile(r'(\w+)\s*=\s*(.+)'),
            'condition': re.compile(r'if\s+(.+):'),
            'loop': re.compile(r'for\s+(\w+)\s+in\s+(.+):'),
            'comment': re.compile(r'#.*'),
            'import': re.compile(r'from\s+(\w+)\s+import\s+(.+)')
        }
    
    def parse_script(self, script_content: str, protocol_name: str = "research_protocol") -> TurbulanceScript:
        """Parse a complete Turbulance script"""
        logger.info(f"Parsing Turbulance script: {protocol_name}")
        
        lines = script_content.strip().split('\n')
        nodes = []
        variables = {}
        pipeline_calls = []
        computations = []
        dependencies = {}
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue
                
            node = self._parse_line(line, line_num)
            if node:
                nodes.append(node)
                
                # Track different types of nodes
                if node.node_type == TurbulanceNodeType.PIPELINE_CALL:
                    pipeline_calls.append(node)
                    # Extract dependencies
                    stage_name = node.parsed_data.get('stage')
                    dependencies[node.parsed_data.get('variable', f'stage_{line_num}')] = [stage_name]
                    
                elif node.node_type == TurbulanceNodeType.COMPUTATION:
                    computations.append(node)
                    
                elif node.node_type == TurbulanceNodeType.VARIABLE_ASSIGNMENT:
                    var_name = node.parsed_data.get('variable')
                    var_value = node.parsed_data.get('value')
                    if var_name:
                        variables[var_name] = var_value
        
        script = TurbulanceScript(
            protocol_name=protocol_name,
            nodes=nodes,
            variables=variables,
            pipeline_calls=pipeline_calls,
            computations=computations,
            dependencies=dependencies
        )
        
        return script
    
    def _parse_line(self, line: str, line_num: int) -> Optional[TurbulanceNode]:
        """Parse a single line of Turbulance script"""
        
        # Check for comments
        if self.patterns['comment'].match(line):
            return TurbulanceNode(
                node_type=TurbulanceNodeType.COMMENT,
                line_number=line_num,
                content=line,
                parsed_data={'text': line[1:].strip()}
            )
        
        # Check for imports
        import_match = self.patterns['import'].match(line)
        if import_match:
            return TurbulanceNode(
                node_type=TurbulanceNodeType.IMPORT,
                line_number=line_num,
                content=line,
                parsed_data={
                    'module': import_match.group(1),
                    'imports': import_match.group(2).strip()
                }
            )
        
        # Check for pipeline calls
        pipeline_match = self.patterns['pipeline_call'].match(line)
        if pipeline_match:
            variable = pipeline_match.group(1)
            stage = pipeline_match.group(2)
            params_str = pipeline_match.group(3).strip() if pipeline_match.group(3) else ""
            
            # Parse parameters
            params = self._parse_parameters(params_str)
            
            return TurbulanceNode(
                node_type=TurbulanceNodeType.PIPELINE_CALL,
                line_number=line_num,
                content=line,
                parsed_data={
                    'variable': variable,
                    'stage': stage,
                    'parameters': params
                },
                outputs=[variable]
            )
        
        # Check for computations
        compute_match = self.patterns['computation'].match(line)
        if compute_match:
            variable = compute_match.group(1)
            computation_str = compute_match.group(2).strip()
            
            return TurbulanceNode(
                node_type=TurbulanceNodeType.COMPUTATION,
                line_number=line_num,
                content=line,
                parsed_data={
                    'variable': variable,
                    'computation': computation_str
                },
                outputs=[variable]
            )
        
        # Check for conditions
        condition_match = self.patterns['condition'].match(line)
        if condition_match:
            return TurbulanceNode(
                node_type=TurbulanceNodeType.CONDITION,
                line_number=line_num,
                content=line,
                parsed_data={'condition': condition_match.group(1)}
            )
        
        # Check for loops
        loop_match = self.patterns['loop'].match(line)
        if loop_match:
            return TurbulanceNode(
                node_type=TurbulanceNodeType.LOOP,
                line_number=line_num,
                content=line,
                parsed_data={
                    'variable': loop_match.group(1),
                    'iterable': loop_match.group(2)
                }
            )
        
        # Check for variable assignments
        var_match = self.patterns['variable'].match(line)
        if var_match:
            return TurbulanceNode(
                node_type=TurbulanceNodeType.VARIABLE_ASSIGNMENT,
                line_number=line_num,
                content=line,
                parsed_data={
                    'variable': var_match.group(1),
                    'value': var_match.group(2).strip()
                },
                outputs=[var_match.group(1)]
            )
        
        return None
    
    def _parse_parameters(self, params_str: str) -> Dict[str, Any]:
        """Parse parameter string from pipeline calls"""
        if not params_str:
            return {}
        
        params = {}
        # Simple parameter parsing - can be enhanced
        try:
            # Remove leading/trailing whitespace and split by commas
            param_pairs = [p.strip() for p in params_str.split(',') if p.strip()]
            
            for pair in param_pairs:
                if '=' in pair:
                    key, value = pair.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Try to parse as JSON for complex values
                    try:
                        params[key] = json.loads(value)
                    except json.JSONDecodeError:
                        # Remove quotes if present
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        elif value.startswith("'") and value.endswith("'"):
                            value = value[1:-1]
                        params[key] = value
        except Exception as e:
            logger.warning(f"Error parsing parameters '{params_str}': {e}")
        
        return params
    
    def generate_auxiliary_files(self, script: TurbulanceScript) -> Dict[str, str]:
        """Generate the three auxiliary files for a Turbulance script"""
        
        # Generate .fs file (network graph consciousness state)
        fs_content = self._generate_fs_file(script)
        
        # Generate .ghd file (resource orchestration dependencies)
        ghd_content = self._generate_ghd_file(script)
        
        # Generate .hre file (metacognitive decision memory)
        hre_content = self._generate_hre_file(script)
        
        return {
            'fs': fs_content,
            'ghd': ghd_content,
            'hre': hre_content
        }
    
    def _generate_fs_file(self, script: TurbulanceScript) -> str:
        """Generate .fs file (network graph consciousness state)"""
        fs_data = {
            "protocol_name": script.protocol_name,
            "network_topology": {
                "nodes": [],
                "edges": [],
                "consciousness_levels": {}
            },
            "state_transitions": [],
            "memory_banks": {
                "working_memory": {},
                "long_term_memory": {},
                "episodic_memory": {}
            }
        }
        
        # Add nodes for each pipeline call
        for call in script.pipeline_calls:
            node_id = call.parsed_data.get('variable', f'node_{call.line_number}')
            stage = call.parsed_data.get('stage', 'unknown')
            
            fs_data["network_topology"]["nodes"].append({
                "id": node_id,
                "type": "pipeline_stage",
                "stage": stage,
                "line": call.line_number,
                "parameters": call.parsed_data.get('parameters', {})
            })
            
            # Set consciousness level based on stage
            consciousness_map = {
                "query_processor": 0.8,
                "context_analyzer": 0.7,
                "domain_expert": 0.9,
                "evidence_synthesizer": 0.85,
                "uncertainty_quantifier": 0.6,
                "result_interpreter": 0.75,
                "quality_assessor": 0.7,
                "response_generator": 0.8
            }
            fs_data["network_topology"]["consciousness_levels"][node_id] = consciousness_map.get(stage, 0.5)
        
        # Add edges based on dependencies
        for var, deps in script.dependencies.items():
            for dep in deps:
                fs_data["network_topology"]["edges"].append({
                    "from": dep,
                    "to": var,
                    "weight": 1.0,
                    "type": "data_flow"
                })
        
        return json.dumps(fs_data, indent=2)
    
    def _generate_ghd_file(self, script: TurbulanceScript) -> str:
        """Generate .ghd file (resource orchestration dependencies)"""
        ghd_data = {
            "protocol_name": script.protocol_name,
            "resource_requirements": {
                "computational": {},
                "memory": {},
                "network": {},
                "storage": {}
            },
            "orchestration_plan": {
                "stages": [],
                "dependencies": script.dependencies,
                "parallel_groups": [],
                "sequential_order": []
            },
            "resource_allocation": {
                "cpu_cores": {},
                "memory_gb": {},
                "gpu_units": {},
                "network_bandwidth": {}
            }
        }
        
        # Estimate resource requirements for each stage
        for call in script.pipeline_calls:
            stage = call.parsed_data.get('stage', 'unknown')
            var_name = call.parsed_data.get('variable', f'stage_{call.line_number}')
            
            # Default resource estimates
            resource_estimates = {
                "query_processor": {"cpu": 1, "memory": 2, "gpu": 0},
                "context_analyzer": {"cpu": 2, "memory": 4, "gpu": 0},
                "domain_expert": {"cpu": 4, "memory": 8, "gpu": 1},
                "evidence_synthesizer": {"cpu": 3, "memory": 6, "gpu": 0},
                "uncertainty_quantifier": {"cpu": 2, "memory": 4, "gpu": 0},
                "result_interpreter": {"cpu": 2, "memory": 4, "gpu": 0},
                "quality_assessor": {"cpu": 1, "memory": 2, "gpu": 0},
                "response_generator": {"cpu": 2, "memory": 4, "gpu": 0}
            }
            
            estimates = resource_estimates.get(stage, {"cpu": 1, "memory": 2, "gpu": 0})
            
            ghd_data["orchestration_plan"]["stages"].append({
                "stage": stage,
                "variable": var_name,
                "line": call.line_number,
                "estimated_duration": 30.0,  # seconds
                "resource_requirements": estimates
            })
            
            ghd_data["resource_allocation"]["cpu_cores"][var_name] = estimates["cpu"]
            ghd_data["resource_allocation"]["memory_gb"][var_name] = estimates["memory"]
            ghd_data["resource_allocation"]["gpu_units"][var_name] = estimates["gpu"]
        
        return json.dumps(ghd_data, indent=2)
    
    def _generate_hre_file(self, script: TurbulanceScript) -> str:
        """Generate .hre file (metacognitive decision memory)"""
        hre_data = {
            "protocol_name": script.protocol_name,
            "decision_tree": {
                "root": "protocol_start",
                "nodes": {},
                "branches": []
            },
            "metacognitive_strategies": {
                "monitoring": [],
                "control": [],
                "planning": []
            },
            "memory_consolidation": {
                "working_memory_size": 7,  # Miller's magic number
                "long_term_storage": {},
                "episodic_traces": []
            },
            "decision_criteria": {
                "confidence_thresholds": {},
                "quality_gates": {},
                "fallback_strategies": {}
            }
        }
        
        # Build decision tree from script structure
        for i, call in enumerate(script.pipeline_calls):
            stage = call.parsed_data.get('stage', 'unknown')
            var_name = call.parsed_data.get('variable', f'stage_{call.line_number}')
            
            node_id = f"decision_{i}"
            hre_data["decision_tree"]["nodes"][node_id] = {
                "stage": stage,
                "variable": var_name,
                "decision_type": "pipeline_execution",
                "success_criteria": f"successful_{stage}_completion",
                "failure_handling": f"retry_{stage}_with_fallback"
            }
            
            # Add metacognitive strategies
            hre_data["metacognitive_strategies"]["monitoring"].append({
                "stage": stage,
                "metrics": ["execution_time", "quality_score", "confidence_level"],
                "thresholds": {"min_quality": 0.7, "max_time": 60.0}
            })
            
            hre_data["metacognitive_strategies"]["control"].append({
                "stage": stage,
                "controls": ["adaptive_timeout", "quality_gating", "resource_throttling"]
            })
        
        # Add planning strategies
        hre_data["metacognitive_strategies"]["planning"] = [
            {
                "strategy": "sequential_execution",
                "description": "Execute stages in order with dependency checking"
            },
            {
                "strategy": "parallel_optimization", 
                "description": "Identify parallel execution opportunities"
            },
            {
                "strategy": "resource_balancing",
                "description": "Balance computational load across available resources"
            }
        ]
        
        return json.dumps(hre_data, indent=2)
    
    def extract_pipeline_sequence(self, script: TurbulanceScript) -> List[Dict[str, Any]]:
        """Extract the sequence of pipeline stage calls for execution"""
        sequence = []
        
        for call in script.pipeline_calls:
            sequence.append({
                'variable': call.parsed_data.get('variable'),
                'stage': call.parsed_data.get('stage'),
                'parameters': call.parsed_data.get('parameters', {}),
                'line_number': call.line_number,
                'dependencies': call.dependencies
            })
        
        return sequence 