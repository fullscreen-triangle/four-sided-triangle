from typing import Dict, Any, List
import logging
from openai import OpenAI
import anthropic
import os
from concurrent.futures import ThreadPoolExecutor
import time

from app.interpreter.models import (
    InterpretationRequest,
    InterpretationResponse,
    InterpretedSolution,
    ResponseQualityMetrics
)
from app.interpreter.response_translator import ResponseTranslator
from app.interpreter.quality_assessor import QualityAssessor

logger = logging.getLogger(__name__)

class InterpreterService:
    def __init__(self):
        # Initialize LLM clients
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.claude_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.executor = ThreadPoolExecutor(max_workers=3)  # For parallel operations
        
        # Initialize component classes
        self.response_translator = ResponseTranslator(
            openai_client=self.openai_client,
            claude_client=self.claude_client
        )
        self.quality_assessor = QualityAssessor(
            openai_client=self.openai_client,
            claude_client=self.claude_client
        )
    
    async def interpret_solution(self, request: InterpretationRequest) -> InterpretationResponse:
        """
        Interpret a solution package into a user-friendly format.
        """
        try:
            solution_package = request.solution_package
            user_context = request.user_context or {}
            
            # Track processing time
            start_time = time.time()
            
            # 1. Generate technical explanation
            technical_explanation = await self._generate_technical_explanation(solution_package)
            
            # 2. Extract key insights
            conclusions = solution_package.get("conclusions", [])
            results = solution_package.get("results", {})
            key_insights = await self._extract_key_insights(conclusions, results)
            
            # 3. Generate user-friendly explanation
            user_friendly_explanation = await self.response_translator.translate_to_user_friendly(
                technical_explanation,
                user_context.get("expertise_level", "general")
            )
            
            # 4. Generate follow-up suggestions
            follow_up_suggestions = await self._generate_follow_up_suggestions(
                conclusions,
                user_context
            )
            
            # 5. Extract sources
            sources = solution_package.get("sources", [])
            
            # 6. Create the interpreted solution
            interpreted_solution = InterpretedSolution(
                technical_explanation=technical_explanation,
                user_friendly_explanation=user_friendly_explanation,
                key_insights=key_insights,
                follow_up_suggestions=follow_up_suggestions,
                sources=sources
            )
            
            # 7. Assess quality
            quality_metrics = await self.quality_assessor.assess_quality(
                interpreted_solution,
                solution_package,
                solution_package.get("domain_knowledge", {})
            )
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # 8. Return full response
            return InterpretationResponse(
                interpreted_solution=interpreted_solution,
                quality_metrics=quality_metrics,
                metadata={
                    "model_used": user_context.get("preferred_model", "gpt-4"),
                    "expertise_level": user_context.get("expertise_level", "general"),
                    "processing_time": round(processing_time, 3)
                }
            )
            
        except Exception as e:
            logger.error(f"Error in interpreter service: {str(e)}")
            # Generate fallback response
            return self._generate_fallback_response(request)
    
    async def _generate_technical_explanation(self, solution_package: Dict[str, Any]) -> str:
        """Generate a technical explanation from the solution package."""
        # Extract relevant components from solution package
        results = solution_package.get("results", {})
        conclusions = solution_package.get("conclusions", [])
        reasoning_paths = solution_package.get("reasoning_paths", [])
        
        # Build a technical explanation focused on accuracy and completeness
        explanation = "Technical Analysis Results:\n\n"
        
        # Add conclusions
        if conclusions:
            explanation += "Conclusions:\n"
            for i, conclusion in enumerate(conclusions):
                explanation += f"{i+1}. {conclusion.get('description', '')}"
                if conclusion.get('confidence'):
                    explanation += f" (Confidence: {conclusion.get('confidence')})"
                explanation += "\n"
            explanation += "\n"
        
        # Add key results
        if results:
            explanation += "Key Parameters and Results:\n"
            for key, value in results.items():
                explanation += f"- {key}: {value}\n"
            explanation += "\n"
        
        # Add reasoning summary
        if reasoning_paths:
            explanation += "Reasoning Approaches:\n"
            for i, path in enumerate(reasoning_paths):
                if isinstance(path, dict):
                    explanation += f"{i+1}. {path.get('strategy', 'Analysis approach')}"
                    if path.get('confidence'):
                        explanation += f" (Confidence: {path.get('confidence')})"
                    explanation += "\n"
            
        return explanation
    
    async def _extract_key_insights(
        self, 
        conclusions: List[Dict[str, Any]], 
        results: Dict[str, Any]
    ) -> List[str]:
        """
        Extract key insights from conclusions and results.
        
        Args:
            conclusions: List of conclusion objects
            results: Dictionary of computation results
            
        Returns:
            List of key insights as strings
        """
        insights = []
        
        # Extract from conclusions (high confidence ones first)
        sorted_conclusions = sorted(
            conclusions, 
            key=lambda c: c.get('confidence', 0),
            reverse=True
        )
        
        # Add high-confidence conclusions as insights
        for conclusion in sorted_conclusions[:3]:  # Top 3 conclusions
            if conclusion.get('confidence', 0) > 0.6:  # Only use reasonably confident conclusions
                insight = conclusion.get('description', '')
                if insight and insight not in insights:
                    insights.append(insight)
        
        # Analyze numerical results for significant patterns
        if results:
            numerical_results = {}
            # Extract numerical values
            for key, value in results.items():
                try:
                    if isinstance(value, (int, float)):
                        numerical_results[key] = value
                    elif isinstance(value, str) and value.replace('.', '', 1).isdigit():
                        numerical_results[key] = float(value)
                except (ValueError, TypeError):
                    continue
            
            # Find significant values (outliers, extremes)
            if len(numerical_results) >= 3:
                # Find max and min values
                max_key = max(numerical_results, key=numerical_results.get)
                min_key = min(numerical_results, key=numerical_results.get)
                
                # Add insights about extremes
                insights.append(f"The highest value is {max_key} at {numerical_results[max_key]}.")
                insights.append(f"The lowest value is {min_key} at {numerical_results[min_key]}.")
            
            # Add insights about key parameters
            elif numerical_results:
                # Just take the most important parameters based on name
                important_params = []
                for key in numerical_results:
                    # Look for keywords indicating importance
                    if any(term in key.lower() for term in ['total', 'score', 'overall', 'key', 'primary', 'main']):
                        important_params.append(key)
                
                # If no important-sounding params found, just use the first few
                if not important_params and numerical_results:
                    important_params = list(numerical_results.keys())[:2]
                
                # Add insights about these parameters
                for key in important_params[:2]:
                    insights.append(f"The {key} value is {numerical_results[key]}.")
        
        # Ensure we have at least a few insights
        if len(insights) < 2 and conclusions:
            # Add any remaining conclusions
            for conclusion in sorted_conclusions[3:5]:
                insight = conclusion.get('description', '')
                if insight and insight not in insights:
                    insights.append(insight)
        
        return insights[:5]  # Limit to top 5 insights
    
    async def _generate_follow_up_suggestions(
        self, 
        conclusions: List[Dict[str, Any]],
        user_context: Dict[str, Any]
    ) -> List[str]:
        """Generate suggestions for follow-up queries."""
        # In a full implementation, this would use an LLM to generate contextually relevant suggestions
        # Here we'll just provide some generic ones based on conclusions
        
        suggestions = [
            "Explore how different parameters might affect the outcome",
            "Analyze the sensitivity of results to key assumptions"
        ]
        
        # Add suggestions based on conclusions
        if conclusions:
            for conclusion in conclusions[:2]:  # Top 2 conclusions
                description = conclusion.get('description', '')
                if description:
                    # Extract key terms by simple word length heuristic
                    key_terms = [word for word in description.split() if len(word) > 6]
                    if key_terms:
                        term = key_terms[0]
                        suggestions.append(f"Investigate how {term} relates to other factors")
        
        return suggestions[:3]  # Return top 3 suggestions
    
    def _generate_fallback_response(self, request: InterpretationRequest) -> InterpretationResponse:
        """Generate a simple fallback response if processing fails."""
        solution_package = request.solution_package
        
        # Extract any available information
        conclusions = solution_package.get("conclusions", [])
        results = solution_package.get("results", {})
        
        # Create a simple explanation
        explanation = "Based on the analysis, "
        
        if conclusions:
            explanation += "the following conclusions were reached: "
            for i, conclusion in enumerate(conclusions[:3]):
                if i > 0:
                    explanation += "; "
                explanation += conclusion.get("description", "")
        else:
            explanation += "no clear conclusions could be determined."
        
        if results:
            explanation += "\n\nKey results: "
            for i, (key, value) in enumerate(list(results.items())[:5]):
                if i > 0:
                    explanation += ", "
                explanation += f"{key}: {value}"
        
        # Create interpreted solution with minimal information
        interpreted_solution = InterpretedSolution(
            technical_explanation=explanation,
            user_friendly_explanation=explanation,
            key_insights=[c.get("description", "") for c in conclusions[:3]],
            follow_up_suggestions=["Consider refining the analysis parameters"]
        )
        
        # Create minimal quality metrics
        quality_metrics = ResponseQualityMetrics(
            accuracy=0.7,
            completeness=0.7,
            clarity=0.7,
            relevance=0.7,
            bias_assessment=0.1,
            overall_quality=0.7
        )
        
        return InterpretationResponse(
            interpreted_solution=interpreted_solution,
            quality_metrics=quality_metrics,
            metadata={"error": "Fallback response due to processing error"}
        ) 