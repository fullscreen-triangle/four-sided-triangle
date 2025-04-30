"""
Metacognitive Task Partitioning (MTP) - Self-interrogative query decomposition.

This module implements the metacognitive query decomposition process, which 
breaks complex queries into optimally sized sub-tasks using self-interrogative
principles. The system treats itself as an object of inquiry, applying
metacognitive principles from cognitive science to optimize task partitioning.
"""
import logging
import re
import json
import uuid
from typing import Dict, Any, List, Optional, Set, Tuple

class MetacognitiveTaskManager:
    """
    Implements self-interrogative decomposition of complex queries into optimally sized sub-tasks.
    
    This class applies metacognitive principles to decompose queries, treating the system
    itself as an object of inquiry rather than using fixed decomposition heuristics.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Metacognitive Task Manager.
        
        Args:
            config: Optional configuration parameters
        """
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Load domain-specific task templates
        self.task_templates = self._load_task_templates()
        
        # Knowledge domain definitions
        self.knowledge_domains = self._load_knowledge_domains()
        
        self.logger.info("Initialized Metacognitive Task Manager")
    
    def decompose_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Decompose a complex query into optimally sized sub-tasks.
        
        Args:
            query: The original user query
            context: Optional additional context
            
        Returns:
            Dictionary containing decomposed query components
        """
        context = context or {}
        self.logger.debug(f"Decomposing query: {query[:50]}...")
        
        # Phase 1: Identify knowledge domains required
        domains = self._extract_knowledge_domains(query)
        self.logger.debug(f"Identified domains: {domains}")
        
        # Phase 2: For each domain, identify specific tasks
        domain_tasks = {}
        for domain in domains:
            domain_tasks[domain] = self._identify_domain_tasks(query, domain)
        
        # Phase 3: Formulate specific sub-queries
        sub_queries = []
        for domain, tasks in domain_tasks.items():
            for task in tasks:
                sub_query = self._formulate_sub_query(query, domain, task)
                completion_criteria = self._define_completion_criteria(domain, task)
                
                query_id = str(uuid.uuid4())
                sub_queries.append({
                    "id": query_id,
                    "query": sub_query,
                    "domain": domain,
                    "task_type": task,
                    "completion_criteria": completion_criteria
                })
        
        # Phase 4: Establish dependency graph
        dependency_graph = self._establish_dependencies(sub_queries)
        
        # Assemble the decomposed query result
        decomposed_result = {
            "original_query": query,
            "domains": domains,
            "sub_queries": sub_queries,
            "dependency_graph": dependency_graph,
            "context": context
        }
        
        self.logger.info(f"Decomposed query into {len(sub_queries)} sub-queries across {len(domains)} domains")
        return decomposed_result
    
    def _load_task_templates(self) -> Dict[str, Dict[str, Any]]:
        """
        Load task templates for different domains.
        
        Returns:
            Dictionary of task templates by domain
        """
        # In a real implementation, this would load from a configuration file
        # Here we define a minimal set of templates inline
        
        return {
            "biomechanics": {
                "measurement": {
                    "template": "Extract {metric_type} measurements for {subject}",
                    "requires": ["subject", "metric_type"]
                },
                "calculation": {
                    "template": "Calculate {calculation_type} for {subject} using {parameters}",
                    "requires": ["subject", "calculation_type", "parameters"]
                },
                "comparison": {
                    "template": "Compare {metric_a} and {metric_b} for {subject}",
                    "requires": ["subject", "metric_a", "metric_b"]
                }
            },
            "physiology": {
                "energy_systems": {
                    "template": "Analyze {energy_system} contribution during {activity}",
                    "requires": ["energy_system", "activity"]
                },
                "cardiac_output": {
                    "template": "Calculate cardiac output for {subject} during {activity_level}",
                    "requires": ["subject", "activity_level"]
                }
            },
            "generic": {
                "extraction": {
                    "template": "Extract key information about {topic}",
                    "requires": ["topic"]
                },
                "summary": {
                    "template": "Provide a summary of {topic}",
                    "requires": ["topic"]
                },
                "explanation": {
                    "template": "Explain {topic} in detail",
                    "requires": ["topic"]
                }
            }
        }
    
    def _load_knowledge_domains(self) -> Dict[str, Dict[str, Any]]:
        """
        Load knowledge domain definitions.
        
        Returns:
            Dictionary of knowledge domain definitions
        """
        # In a real implementation, this would load from a configuration file
        # Here we define a minimal set of domains inline
        
        return {
            "biomechanics": {
                "keywords": [
                    "biomechanics", "force", "torque", "joint angle", "kinematics", 
                    "kinetics", "power output", "velocity", "acceleration", "stride", 
                    "gait", "motion", "segment", "lever arm", "anthropometric"
                ],
                "entities": ["joint", "muscle", "limb", "segment", "force", "power"],
                "relations": ["produces", "applies", "rotates", "extends", "flexes"]
            },
            "physiology": {
                "keywords": [
                    "physiology", "metabolism", "energy", "oxygen", "lactate", "anaerobic", 
                    "aerobic", "cardiac", "heart rate", "vo2", "respiration", "fatigue",
                    "blood flow", "muscle fiber", "atp", "phosphagen"
                ],
                "entities": ["energy system", "muscle fiber", "heart", "lungs", "blood"],
                "relations": ["produces", "consumes", "transports", "metabolizes"]
            },
            "statistics": {
                "keywords": [
                    "statistics", "average", "mean", "correlation", "regression", "significance",
                    "probability", "distribution", "variance", "standard deviation", "confidence",
                    "interval", "hypothesis", "test", "p-value", "coefficient"
                ],
                "entities": ["sample", "population", "distribution", "model", "test"],
                "relations": ["correlates", "predicts", "depends", "varies"]
            }
        }
    
    def _extract_knowledge_domains(self, query: str) -> List[str]:
        """
        Identify knowledge domains required to answer the query.
        
        Args:
            query: User query
            
        Returns:
            List of relevant knowledge domains
        """
        query_lower = query.lower()
        domains = []
        domain_scores = {}
        
        # Calculate score for each domain based on keyword matches
        for domain, domain_info in self.knowledge_domains.items():
            score = 0
            
            # Keywords match
            for keyword in domain_info["keywords"]:
                if keyword.lower() in query_lower:
                    score += 2  # Keywords are strong indicators
            
            # Entity match
            for entity in domain_info["entities"]:
                if entity.lower() in query_lower:
                    score += 1
            
            # Relation match
            for relation in domain_info["relations"]:
                if relation.lower() in query_lower:
                    score += 1
            
            domain_scores[domain] = score
        
        # Select domains with significant scores
        threshold = max(1, max(domain_scores.values()) * 0.3)  # At least 30% of max score
        
        for domain, score in domain_scores.items():
            if score >= threshold:
                domains.append(domain)
        
        # If no domains found, add generic domain
        if not domains:
            domains.append("generic")
        
        return domains
    
    def _identify_domain_tasks(self, query: str, domain: str) -> List[str]:
        """
        Identify specific tasks within a knowledge domain.
        
        Args:
            query: User query
            domain: Knowledge domain
            
        Returns:
            List of task types
        """
        query_lower = query.lower()
        
        # Get domain-specific task templates
        templates = self.task_templates.get(domain, self.task_templates.get("generic", {}))
        
        # Identify which tasks are relevant based on query content
        relevant_tasks = []
        
        # Domain-specific task identification logic
        if domain == "biomechanics":
            if any(kw in query_lower for kw in ["measure", "dimensions", "size", "length", "mass"]):
                relevant_tasks.append("measurement")
            if any(kw in query_lower for kw in ["calculate", "compute", "determine", "find"]):
                relevant_tasks.append("calculation")
            if any(kw in query_lower for kw in ["compare", "contrast", "versus", "difference"]):
                relevant_tasks.append("comparison")
        
        elif domain == "physiology":
            if any(kw in query_lower for kw in ["energy", "metabolism", "atp", "glycolysis"]):
                relevant_tasks.append("energy_systems")
            if any(kw in query_lower for kw in ["heart", "cardiac", "blood", "circulation"]):
                relevant_tasks.append("cardiac_output")
        
        # Generic task identification as fallback
        if not relevant_tasks:
            if any(kw in query_lower for kw in ["extract", "identify", "list"]):
                relevant_tasks.append("extraction")
            elif any(kw in query_lower for kw in ["summarize", "overview", "brief"]):
                relevant_tasks.append("summary")
            elif any(kw in query_lower for kw in ["explain", "detail", "elaborate"]):
                relevant_tasks.append("explanation")
        
        # Ensure we always have at least one task
        if not relevant_tasks and "generic" in self.task_templates:
            relevant_tasks.append(next(iter(self.task_templates["generic"].keys())))
        
        return relevant_tasks
    
    def _formulate_sub_query(self, query: str, domain: str, task: str) -> str:
        """
        Formulate a specific sub-query for a domain and task.
        
        Args:
            query: Original query
            domain: Knowledge domain
            task: Task type
            
        Returns:
            Formulated sub-query
        """
        # Extract parameters from query for template filling
        params = self._extract_parameters(query, domain, task)
        
        # Get the template for this domain and task
        template_info = self.task_templates.get(domain, {}).get(task)
        
        if not template_info:
            # Fallback to generic template
            template_info = self.task_templates.get("generic", {}).get("extraction")
        
        if not template_info:
            # Last resort fallback
            return f"Extract information about {domain} focusing on {task} from: {query}"
        
        # Fill template with extracted parameters
        template = template_info["template"]
        for param, value in params.items():
            placeholder = f"{{{param}}}"
            if placeholder in template:
                template = template.replace(placeholder, value)
        
        # If some placeholders remain unfilled, try to infer from query
        remaining_placeholders = re.findall(r"\{([^}]+)\}", template)
        for placeholder in remaining_placeholders:
            if placeholder in params:
                continue  # Already handled
            
            # Try to extract a value from the query
            inferred_value = self._infer_parameter(query, placeholder)
            if inferred_value:
                template = template.replace(f"{{{placeholder}}}", inferred_value)
            else:
                # Replace unfilled placeholder with general term
                template = template.replace(f"{{{placeholder}}}", "relevant information")
        
        # Add original query as context
        sub_query = f"{template} based on this query: '{query}'"
        
        return sub_query
    
    def _extract_parameters(self, query: str, domain: str, task: str) -> Dict[str, str]:
        """
        Extract parameters from the query for template filling.
        
        Args:
            query: Original query
            domain: Knowledge domain
            task: Task type
            
        Returns:
            Dictionary of parameter values
        """
        params = {}
        query_lower = query.lower()
        
        # Generic extraction of common parameters
        
        # Subject extraction (looking for demographic info)
        subject_match = re.search(r"(?:for|about)\s+(?:a|an)\s+(\d+[- ]year[- ]old\s+\w+(?:\s+\w+)?)", query)
        if subject_match:
            params["subject"] = subject_match.group(1)
        
        # Activity extraction
        activity_match = re.search(r"during\s+(\w+(?:\s+\w+){0,3})", query)
        if activity_match:
            params["activity"] = activity_match.group(1)
        
        # Topic extraction (general fallback)
        # Use the most specific noun phrase as the topic
        topic_candidates = [
            r"about\s+(\w+(?:\s+\w+){0,3})",
            r"regarding\s+(\w+(?:\s+\w+){0,3})",
            r"on\s+(\w+(?:\s+\w+){0,3})"
        ]
        
        for pattern in topic_candidates:
            topic_match = re.search(pattern, query)
            if topic_match:
                params["topic"] = topic_match.group(1)
                break
        
        # Domain-specific parameter extraction
        if domain == "biomechanics":
            # Metric type extraction
            metric_types = ["anthropometric", "kinematic", "kinetic", "temporal-spatial"]
            for metric in metric_types:
                if metric in query_lower:
                    params["metric_type"] = metric
                    break
            
            # Calculation type extraction
            calc_types = {
                "force": ["force", "strength"],
                "power": ["power", "output"],
                "velocity": ["velocity", "speed"],
                "acceleration": ["acceleration"],
                "torque": ["torque", "moment"]
            }
            
            for calc_type, keywords in calc_types.items():
                if any(kw in query_lower for kw in keywords):
                    params["calculation_type"] = calc_type
                    break
        
        elif domain == "physiology":
            # Energy system extraction
            energy_systems = ["aerobic", "anaerobic", "phosphagen", "glycolytic", "oxidative"]
            for system in energy_systems:
                if system in query_lower:
                    params["energy_system"] = system
                    break
            
            # Activity level extraction
            if "rest" in query_lower:
                params["activity_level"] = "rest"
            elif "maximum" in query_lower or "max" in query_lower:
                params["activity_level"] = "maximum exertion"
            elif "moderate" in query_lower:
                params["activity_level"] = "moderate activity"
            elif "exercise" in query_lower or "activity" in query_lower:
                params["activity_level"] = "exercise"
        
        return params
    
    def _infer_parameter(self, query: str, param_name: str) -> Optional[str]:
        """
        Infer a parameter value from the query.
        
        Args:
            query: Original query
            param_name: Parameter name to infer
            
        Returns:
            Inferred parameter value or None
        """
        query_lower = query.lower()
        
        # Common parameter inference patterns
        if param_name == "subject":
            # Look for demographic descriptions
            subject_patterns = [
                r"(?:for|about)\s+(?:a|an)\s+(\d+[- ]year[- ]old\s+\w+(?:\s+\w+)?)",
                r"(?:for|about)\s+(?:a|an)\s+(\w+\s+athlete)",
                r"(?:for|about)\s+(?:a|an)\s+(\w+\s+individual)"
            ]
            
            for pattern in subject_patterns:
                match = re.search(pattern, query)
                if match:
                    return match.group(1)
            
            # Default subject if none found
            return "the subject"
        
        elif param_name == "topic":
            # Look for main topic phrases
            topic_patterns = [
                r"about\s+(\w+(?:\s+\w+){0,3})",
                r"regarding\s+(\w+(?:\s+\w+){0,3})",
                r"of\s+(\w+(?:\s+\w+){0,3})"
            ]
            
            for pattern in topic_patterns:
                match = re.search(pattern, query)
                if match:
                    return match.group(1)
            
            # Check for domain-specific keywords
            for domain, info in self.knowledge_domains.items():
                for keyword in info["keywords"]:
                    if keyword in query_lower:
                        return keyword
            
            # Default generic topic
            return "the relevant topic"
        
        # Domain-specific parameter inference
        elif param_name == "metric_type" and "biomechanics" in query_lower:
            for metric in ["anthropometric", "kinematic", "kinetic", "temporal-spatial"]:
                if metric in query_lower:
                    return metric
            return "biomechanical"
        
        # More parameter inferences could be added here
        
        return None
    
    def _define_completion_criteria(self, domain: str, task: str) -> Dict[str, Any]:
        """
        Define completion criteria for a sub-query.
        
        Args:
            domain: Knowledge domain
            task: Task type
            
        Returns:
            Dictionary of completion criteria
        """
        # Define completion criteria based on domain and task type
        criteria = {
            "required_elements": [],
            "format_requirements": {},
            "quality_thresholds": {}
        }
        
        # Domain-specific criteria
        if domain == "biomechanics":
            if task == "measurement":
                criteria["required_elements"] = ["measurements", "units", "reference_ranges"]
                criteria["format_requirements"] = {"include_tables": True}
                criteria["quality_thresholds"] = {"precision": 0.85, "completeness": 0.9}
            elif task == "calculation":
                criteria["required_elements"] = ["calculated_values", "formulas_used", "units"]
                criteria["format_requirements"] = {"include_equations": True}
                criteria["quality_thresholds"] = {"numerical_accuracy": 0.95}
            elif task == "comparison":
                criteria["required_elements"] = ["comparison_points", "differences", "similarities"]
                criteria["format_requirements"] = {"include_visualization": True}
                criteria["quality_thresholds"] = {"comparative_depth": 0.8}
        
        elif domain == "physiology":
            if task == "energy_systems":
                criteria["required_elements"] = ["energy_systems", "contribution_percentages", "time_course"]
                criteria["quality_thresholds"] = {"physiological_accuracy": 0.9}
            elif task == "cardiac_output":
                criteria["required_elements"] = ["heart_rate", "stroke_volume", "cardiac_output"]
                criteria["quality_thresholds"] = {"physiological_accuracy": 0.9}
        
        # Generic criteria as fallback
        if not criteria["required_elements"]:
            criteria["required_elements"] = ["key_points", "explanations"]
            criteria["quality_thresholds"] = {"relevance": 0.8, "accuracy": 0.8}
        
        return criteria
    
    def _establish_dependencies(self, sub_queries: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """
        Establish dependencies between sub-queries.
        
        Args:
            sub_queries: List of sub-query specifications
            
        Returns:
            Dependency graph as a dictionary mapping query IDs to dependency lists
        """
        dependency_graph = {}
        
        # Map for quick access to queries by ID
        query_map = {q["id"]: q for q in sub_queries}
        
        # Initialize empty dependency lists for all queries
        for query in sub_queries:
            dependency_graph[query["id"]] = []
        
        # Analyze task types to establish natural dependencies
        for query in sub_queries:
            query_id = query["id"]
            domain = query["domain"]
            task = query["task_type"]
            
            # Find potential dependencies based on task type
            for other_query in sub_queries:
                if other_query["id"] == query_id:
                    continue  # Skip self
                
                other_domain = other_query["domain"]
                other_task = other_query["task_type"]
                
                # Domain-specific dependency rules
                if domain == "biomechanics":
                    # Calculations depend on measurements
                    if task == "calculation" and other_task == "measurement":
                        dependency_graph[query_id].append(other_query["id"])
                    
                    # Comparisons depend on either measurements or calculations
                    if task == "comparison" and (other_task == "measurement" or other_task == "calculation"):
                        dependency_graph[query_id].append(other_query["id"])
                
                elif domain == "physiology":
                    # Energy system analysis might depend on cardiac output
                    if task == "energy_systems" and other_task == "cardiac_output":
                        dependency_graph[query_id].append(other_query["id"])
                
                # Cross-domain dependencies
                if domain == "statistics" and other_domain in ["biomechanics", "physiology"]:
                    # Statistical analysis depends on data from other domains
                    dependency_graph[query_id].append(other_query["id"])
        
        return dependency_graph 