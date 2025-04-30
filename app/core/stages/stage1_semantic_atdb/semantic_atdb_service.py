import logging
import time
from typing import Dict, Any, List, Optional
import json

from app.core.stages.stage1_semantic_atdb.throttle_detector import ThrottleDetector
from app.core.stages.stage1_semantic_atdb.bypass_strategies import BypassStrategySelector
from app.core.stages.stage1_semantic_atdb.prompt_generator import PromptGenerator
from app.core.stages.stage1_semantic_atdb.metrics import MetricsAnalyzer

logger = logging.getLogger(__name__)

class SemanticATDBService:
    """
    Enhanced Stage 1: Integrated Semantic Analysis with Adversarial Throttle Detection and Bypass
    
    This service combines advanced semantic understanding with throttle detection to ensure
    the pipeline receives comprehensive query transformations even when LLMs attempt to limit responses.
    """
    
    def __init__(self, llm_service=None):
        """Initialize the Semantic ATDB service with required components."""
        self.llm_service = llm_service
        self.throttle_detector = ThrottleDetector()
        self.bypass_strategy_selector = BypassStrategySelector()
        self.prompt_generator = PromptGenerator()
        self.metrics_analyzer = MetricsAnalyzer()
        
        logger.info("Semantic ATDB service initialized")
    
    async def process_query(self, query_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a user query through semantic analysis with throttle detection and bypass.
        
        Args:
            query_data: Dictionary containing the query text and context information
            
        Returns:
            Processed semantic model with comprehensive parameters
        """
        start_time = time.time()
        query_text = query_data.get("query", "")
        context = query_data.get("context", {})
        
        logger.info(f"Processing query with Semantic ATDB: {query_text[:50]}...")
        
        # Phase 1: Initial semantic analysis
        initial_analysis = await self._perform_semantic_analysis(query_text, context)
        
        # Phase 2: Throttle detection
        throttle_detection = self.throttle_detector.detect_throttling(
            response=initial_analysis,
            query=query_text,
            context=context
        )
        
        # Record metrics for monitoring
        self._record_metrics(initial_analysis, throttle_detection)
        
        if throttle_detection["is_throttled"]:
            logger.info(f"Throttling detected: {throttle_detection['pattern']} with confidence {throttle_detection['confidence']:.2f}")
            
            # Phase 3: Apply bypass strategy
            bypass_strategy = self.bypass_strategy_selector.select_strategy(
                throttle_pattern=throttle_detection["pattern"],
                query=query_text,
                initial_response=initial_analysis
            )
            
            # Phase 4: Execute bypass strategy
            enhanced_analyses = await self._execute_bypass_strategy(
                bypass_strategy=bypass_strategy,
                query_text=query_text,
                context=context
            )
            
            # Phase 5: Merge and reconcile results
            final_analysis = self._reconcile_analyses(initial_analysis, enhanced_analyses)
            
            # Include throttling metadata
            final_analysis["metadata"]["throttling_detected"] = True
            final_analysis["metadata"]["throttle_pattern"] = throttle_detection["pattern"]
            final_analysis["metadata"]["bypass_strategy"] = bypass_strategy["name"]
        else:
            logger.info("No throttling detected in initial analysis")
            final_analysis = initial_analysis
            final_analysis["metadata"]["throttling_detected"] = False
        
        # Calculate processing time
        processing_time = time.time() - start_time
        final_analysis["metadata"]["processing_time"] = processing_time
        
        logger.info(f"Semantic ATDB processing completed in {processing_time:.2f} seconds")
        return final_analysis
    
    async def _perform_semantic_analysis(
        self, 
        query_text: str, 
        context: Dict[str, Any] = None,
        prompt_enhancement: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Perform semantic analysis on the query using the enhanced prompt.
        
        Args:
            query_text: The raw query text
            context: Additional context for the query
            prompt_enhancement: Optional customizations to the prompt
            
        Returns:
            Semantic analysis result
        """
        # Generate the enhanced semantic prompt
        system_prompt = self.prompt_generator.create_semantic_prompt(prompt_enhancement)
        
        # Prepare message for LLM
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Query: {query_text}"}
        ]
        
        # Add context if available
        if context and context.get("history"):
            for entry in context["history"][-3:]:  # Include last 3 exchanges for context
                messages.append({"role": entry["role"], "content": entry["content"]})
        
        # Call LLM
        response = await self.llm_service.generate_response(messages)
        
        # Parse LLM response
        try:
            parsed_response = self._parse_llm_response(response)
            
            # Add metadata
            parsed_response["metadata"] = {
                "model_used": self.llm_service.get_model_name(),
                "timestamp": time.time(),
                "original_query": query_text
            }
            
            return parsed_response
        except Exception as e:
            logger.error(f"Error parsing LLM response: {str(e)}")
            return self._create_fallback_response(query_text)
    
    async def _execute_bypass_strategy(
        self, 
        bypass_strategy: Dict[str, Any],
        query_text: str,
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Execute the selected bypass strategy.
        
        Args:
            bypass_strategy: The selected bypass strategy
            query_text: The original query text
            context: Query context
            
        Returns:
            List of analysis results from the bypass strategy
        """
        strategy_name = bypass_strategy["name"]
        
        if strategy_name == "query_partitioning":
            return await self._execute_partition_strategy(bypass_strategy, query_text, context)
        elif strategy_name == "depth_reframing":
            return await self._execute_reframing_strategy(bypass_strategy, query_text, context)
        elif strategy_name == "progressive_disclosure":
            return await self._execute_progressive_strategy(bypass_strategy, query_text, context)
        else:
            logger.warning(f"Unknown bypass strategy: {strategy_name}")
            return []
    
    async def _execute_partition_strategy(
        self, 
        strategy: Dict[str, Any],
        query_text: str,
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Execute the query partitioning strategy."""
        subqueries = strategy["subqueries"]
        results = []
        
        for subquery in subqueries:
            # Create a customized prompt emphasizing the specific aspect
            prompt_enhancement = {
                "focus_instruction": f"Focus specifically on the {subquery['aspect']} aspect of the query.",
                "emphasize_completeness": True
            }
            
            # Process the subquery
            result = await self._perform_semantic_analysis(
                subquery["text"], 
                context, 
                prompt_enhancement
            )
            
            # Add metadata
            result["metadata"]["subquery_aspect"] = subquery["aspect"]
            results.append(result)
        
        return results
    
    async def _execute_reframing_strategy(
        self, 
        strategy: Dict[str, Any],
        query_text: str,
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Execute the depth reframing strategy."""
        # Create a customized prompt emphasizing depth
        prompt_enhancement = {
            "depth_instruction": strategy["reframed_instruction"],
            "force_exhaustive_analysis": True,
            "increase_parameter_exploration": True
        }
        
        # Process with the reframed instruction
        result = await self._perform_semantic_analysis(
            strategy["reframed_query"], 
            context, 
            prompt_enhancement
        )
        
        return [result]
    
    async def _execute_progressive_strategy(
        self, 
        strategy: Dict[str, Any],
        query_text: str,
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Execute the progressive disclosure strategy."""
        results = []
        accumulated_knowledge = {}
        
        # Process initial query
        initial_result = await self._perform_semantic_analysis(
            strategy["initial_query"], 
            context
        )
        results.append(initial_result)
        
        # Extract knowledge from initial query
        accumulated_knowledge["parameters"] = initial_result.get("parametersOfInterest", [])
        accumulated_knowledge["intent"] = initial_result.get("intentClassification", "")
        accumulated_knowledge["subject"] = initial_result.get("keySubject", "")
        
        # Process follow-up queries
        for i, followup_query in enumerate(strategy["followup_queries"]):
            # Add accumulated knowledge to context
            enhanced_context = {**context, "accumulated_knowledge": accumulated_knowledge}
            
            # Create progressive prompt enhancement
            prompt_enhancement = {
                "prior_knowledge": accumulated_knowledge,
                "iteration": i + 1,
                "instruction": f"Build upon previous findings: {json.dumps(accumulated_knowledge)}"
            }
            
            # Process followup query
            followup_result = await self._perform_semantic_analysis(
                followup_query, 
                enhanced_context, 
                prompt_enhancement
            )
            
            # Update accumulated knowledge
            accumulated_knowledge["parameters"].extend([
                p for p in followup_result.get("parametersOfInterest", [])
                if p not in accumulated_knowledge["parameters"]
            ])
            
            results.append(followup_result)
        
        return results
    
    def _reconcile_analyses(
        self, 
        initial_analysis: Dict[str, Any],
        enhanced_analyses: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Reconcile initial and enhanced analyses into a comprehensive result.
        
        Args:
            initial_analysis: The initial semantic analysis
            enhanced_analyses: Results from bypass strategies
            
        Returns:
            Consolidated analysis
        """
        # Start with a copy of the initial analysis
        reconciled = dict(initial_analysis)
        
        # If no enhanced analyses, return initial
        if not enhanced_analyses:
            return reconciled
        
        # Combine parameters of interest (eliminate duplicates)
        all_parameters = set(reconciled.get("parametersOfInterest", []))
        for analysis in enhanced_analyses:
            all_parameters.update(analysis.get("parametersOfInterest", []))
        reconciled["parametersOfInterest"] = list(all_parameters)
        
        # Use the most confident intent classification
        intent_confidences = [
            (initial_analysis.get("intentClassification", ""), initial_analysis.get("confidence", 0))
        ]
        for analysis in enhanced_analyses:
            intent_confidences.append(
                (analysis.get("intentClassification", ""), analysis.get("confidence", 0))
            )
        best_intent = max(intent_confidences, key=lambda x: x[1])
        reconciled["intentClassification"] = best_intent[0]
        
        # Combine reasoning (take the most detailed one)
        reasoning_lengths = [
            (initial_analysis.get("reasoning", ""), len(initial_analysis.get("reasoning", "")))
        ]
        for analysis in enhanced_analyses:
            reasoning_lengths.append(
                (analysis.get("reasoning", ""), len(analysis.get("reasoning", "")))
            )
        best_reasoning = max(reasoning_lengths, key=lambda x: x[1])
        reconciled["reasoning"] = best_reasoning[0]
        
        # Create the most comprehensive reformulated query
        reformulated_queries = [
            initial_analysis.get("reformulatedQuery", "")
        ]
        for analysis in enhanced_analyses:
            reformulated_queries.append(analysis.get("reformulatedQuery", ""))
        
        # Select the most detailed reformulation
        reconciled["reformulatedQuery"] = max(reformulated_queries, key=len)
        
        # Update confidence to reflect comprehensive analysis
        reconciled["confidence"] = min(0.95, max([
            initial_analysis.get("confidence", 0)] + 
            [a.get("confidence", 0) for a in enhanced_analyses]
        ))
        
        return reconciled
    
    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """Parse the LLM response into a structured semantic analysis."""
        try:
            # Extract JSON from the response
            json_match = response.find('{')
            if json_match == -1:
                raise ValueError("No JSON object found in response")
            
            json_str = response[json_match:]
            parsed = json.loads(json_str)
            
            # Validate required fields
            required_fields = ["intentClassification", "keySubject", "parametersOfInterest", "confidence", "reasoning"]
            for field in required_fields:
                if field not in parsed:
                    logger.warning(f"Missing required field in LLM response: {field}")
                    parsed[field] = "" if field != "parametersOfInterest" else []
                    
            # Ensure confidence is a float between 0 and 1
            if not isinstance(parsed["confidence"], (int, float)):
                parsed["confidence"] = 0.5
            parsed["confidence"] = max(0.0, min(1.0, float(parsed["confidence"])))
            
            return parsed
        except Exception as e:
            logger.error(f"Error parsing LLM response: {str(e)}")
            raise
    
    def _create_fallback_response(self, query_text: str) -> Dict[str, Any]:
        """Create a fallback response when parsing fails."""
        return {
            "intentClassification": "informational",
            "keySubject": "general",
            "parametersOfInterest": [],
            "confidence": 0.3,
            "reasoning": "Failed to parse LLM response. Using fallback response.",
            "reformulatedQuery": query_text,
            "metadata": {
                "is_fallback": True,
                "timestamp": time.time(),
                "original_query": query_text
            }
        }
    
    def _record_metrics(self, analysis: Dict[str, Any], throttle_detection: Dict[str, Any]) -> None:
        """Record metrics for monitoring and improvement."""
        # In a production system, these metrics would be sent to a monitoring service
        self.metrics_analyzer.record_analysis_metrics(analysis)
        self.metrics_analyzer.record_throttle_metrics(throttle_detection)
