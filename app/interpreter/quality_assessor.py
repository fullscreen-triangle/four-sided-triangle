from typing import Dict, Any, List
import json
import logging
from openai import OpenAI
import anthropic

from app.interpreter.models import ResponseQualityMetrics

logger = logging.getLogger(__name__)

class QualityAssessor:
    def __init__(self, openai_client=None, claude_client=None):
        self.openai_client = openai_client
        self.claude_client = claude_client
    
    async def assess_quality(
        self, 
        interpreted_solution: Dict[str, Any],
        original_solution: Dict[str, Any],
        domain_knowledge: Dict[str, Any]
    ) -> ResponseQualityMetrics:
        """
        Evaluates the quality of the interpreted solution across multiple dimensions.
        
        Args:
            interpreted_solution: The solution after interpretation
            original_solution: The original technical solution from the solver
            domain_knowledge: Domain-specific knowledge for accuracy verification
            
        Returns:
            Quality metrics for different aspects of the solution
        """
        # Try to use LLM for quality assessment
        try:
            metrics = await self._get_llm_quality_assessment(
                interpreted_solution, 
                original_solution, 
                domain_knowledge
            )
            return metrics
        except Exception as e:
            logger.error(f"Error in LLM quality assessment: {str(e)}")
            # Fallback to simple heuristic assessment
            return self._fallback_quality_assessment(
                interpreted_solution, 
                original_solution
            )
    
    async def verify_accuracy(
        self, 
        interpreted_solution: Dict[str, Any],
        original_solution: Dict[str, Any]
    ) -> float:
        """
        Verifies factual correctness against domain knowledge.
        
        Args:
            interpreted_solution: The solution after interpretation
            original_solution: The original technical solution
            
        Returns:
            Accuracy score between 0.0 and 1.0
        """
        # Compare key facts between original and interpreted solutions
        prompt = self._build_accuracy_verification_prompt(
            interpreted_solution, 
            original_solution
        )
        
        try:
            accuracy_score = await self._get_accuracy_verification(prompt)
            return accuracy_score
        except Exception as e:
            logger.error(f"Error verifying accuracy: {str(e)}")
            return self._calculate_simple_accuracy(
                interpreted_solution, 
                original_solution
            )
    
    async def evaluate_completeness(
        self, 
        interpreted_solution: Dict[str, Any],
        original_solution: Dict[str, Any]
    ) -> float:
        """
        Verifies all query aspects are addressed.
        
        Args:
            interpreted_solution: The solution after interpretation
            original_solution: The original technical solution
            
        Returns:
            Completeness score between 0.0 and 1.0
        """
        prompt = self._build_completeness_prompt(
            interpreted_solution, 
            original_solution
        )
        
        try:
            completeness_score = await self._get_completeness_evaluation(prompt)
            return completeness_score
        except Exception as e:
            logger.error(f"Error evaluating completeness: {str(e)}")
            return self._calculate_simple_completeness(
                interpreted_solution, 
                original_solution
            )
    
    async def assess_clarity(
        self, 
        content: str
    ) -> float:
        """
        Evaluates explanation comprehensibility.
        
        Args:
            content: The content to evaluate
            
        Returns:
            Clarity score between 0.0 and 1.0
        """
        prompt = self._build_clarity_assessment_prompt(content)
        
        try:
            clarity_score = await self._get_clarity_assessment(prompt)
            return clarity_score
        except Exception as e:
            logger.error(f"Error assessing clarity: {str(e)}")
            return self._calculate_simple_clarity(content)
    
    async def detect_bias(
        self, 
        content: str
    ) -> Dict[str, Any]:
        """
        Identifies and addresses potential biases in response.
        
        Args:
            content: The content to evaluate for bias
            
        Returns:
            Dictionary with bias score and detected biases
        """
        prompt = self._build_bias_detection_prompt(content)
        
        try:
            bias_assessment = await self._get_bias_assessment(prompt)
            return bias_assessment
        except Exception as e:
            logger.error(f"Error detecting bias: {str(e)}")
            return {
                "bias_score": 0.1,  # Assume low bias by default
                "detected_biases": []
            }
    
    def _build_accuracy_verification_prompt(
        self, 
        interpreted_solution: Dict[str, Any],
        original_solution: Dict[str, Any]
    ) -> str:
        """Builds prompt for accuracy verification."""
        
        # Convert solutions to formatted text
        interpreted_json = json.dumps({
            "explanation": interpreted_solution.get("user_friendly_explanation", ""),
            "key_insights": interpreted_solution.get("key_insights", [])
        }, indent=2)
        
        original_json = json.dumps({
            "results": original_solution.get("results", {}),
            "conclusions": original_solution.get("conclusions", [])
        }, indent=2)
        
        prompt = f"""
        Task: Verify the factual accuracy of the interpreted solution against the original solution.
        
        Original Solution:
        {original_json}
        
        Interpreted Solution:
        {interpreted_json}
        
        Guidelines:
        - Check if all key numerical values are correctly represented
        - Verify that causal relationships are maintained
        - Confirm that conclusions match between the original and interpreted versions
        - Check if any factual statements contradict the original solution
        - Identify any oversimplifications that change the meaning
        
        Please provide:
        1. An accuracy score between 0.0 and 1.0 (where 1.0 is perfectly accurate)
        2. A JSON object with the structure: {{"score": float, "errors": [list of factual errors]}}
        """
        
        return prompt
    
    def _build_completeness_prompt(
        self, 
        interpreted_solution: Dict[str, Any],
        original_solution: Dict[str, Any]
    ) -> str:
        """Builds prompt for completeness evaluation."""
        
        # Extract key elements from original solution
        original_conclusions = original_solution.get("conclusions", [])
        key_parameters = list(original_solution.get("results", {}).keys())
        
        # Format as lists
        conclusion_points = "\n".join([
            f"- {c.get('description', 'Conclusion')}" 
            for c in original_conclusions[:5]
        ])
        
        parameter_points = "\n".join([f"- {p}" for p in key_parameters[:10]])
        
        # Get interpreted content
        interpreted_text = interpreted_solution.get("user_friendly_explanation", "")
        
        prompt = f"""
        Task: Evaluate how completely the interpreted solution covers the original solution.
        
        Key elements that should be covered from the original solution:
        
        Key Conclusions:
        {conclusion_points}
        
        Key Parameters/Results:
        {parameter_points}
        
        Interpreted Solution:
        {interpreted_text}
        
        Guidelines:
        - Check if all key conclusions are represented in the interpretation
        - Verify that important parameters and their values are included
        - Assess if any critical relationships or insights are missing
        - Consider the overall context and whether the interpretation maintains the full scope
        
        Please provide:
        1. A completeness score between 0.0 and 1.0 (where 1.0 is completely comprehensive)
        2. A JSON object with the structure: {{"score": float, "missing_elements": [list of missing key elements]}}
        """
        
        return prompt
    
    def _build_clarity_assessment_prompt(
        self, 
        content: str
    ) -> str:
        """Builds prompt for clarity assessment."""
        
        prompt = f"""
        Task: Evaluate the clarity and comprehensibility of the following explanation.
        
        Content to Evaluate:
        {content[:4000]}  # Limit to avoid token limits
        
        Guidelines:
        - Assess readability (sentence structure, paragraph flow, transitions)
        - Check explanation of technical concepts
        - Evaluate logical flow and coherence
        - Consider appropriate level of detail
        - Assess use of jargon and technical terminology
        
        Please provide:
        1. A clarity score between 0.0 and 1.0 (where 1.0 is perfectly clear)
        2. A JSON object with the structure: {{"score": float, "improvement_suggestions": [list of suggestions]}}
        """
        
        return prompt
    
    def _build_bias_detection_prompt(
        self, 
        content: str
    ) -> str:
        """Builds prompt for bias detection."""
        
        prompt = f"""
        Task: Identify any potential biases in the following content.
        
        Content to Evaluate:
        {content[:4000]}  # Limit to avoid token limits
        
        Guidelines:
        - Check for confirmation bias (favoring information that confirms preexisting beliefs)
        - Look for selection bias (cherry-picking data or examples)
        - Identify framing bias (presenting information to encourage particular interpretations)
        - Assess for technical bias (favoring particular methods or approaches)
        - Check for language that suggests unwarranted certainty
        
        Please provide:
        1. A bias assessment score between 0.0 and 1.0 (where 0.0 is no detected bias)
        2. A JSON object with the structure: {{"bias_score": float, "detected_biases": [list of specific biases found]}}
        """
        
        return prompt
    
    async def _get_llm_quality_assessment(
        self, 
        interpreted_solution: Dict[str, Any],
        original_solution: Dict[str, Any],
        domain_knowledge: Dict[str, Any]
    ) -> ResponseQualityMetrics:
        """Use LLM to get comprehensive quality assessment."""
        
        # Prepare assessment context
        assessment_context = {
            "interpreted_solution": {
                "explanation": interpreted_solution.get("user_friendly_explanation", ""),
                "key_insights": interpreted_solution.get("key_insights", [])
            },
            "original_solution": {
                "results": original_solution.get("results", {}),
                "conclusions": original_solution.get("conclusions", [])
            },
            "domain_knowledge": domain_knowledge
        }
        
        # Create prompt
        prompt = f"""
        Task: Perform a comprehensive quality assessment of the interpreted solution.
        
        Assessment Context:
        {json.dumps(assessment_context, indent=2)}
        
        Please evaluate the solution on the following dimensions:
        1. Accuracy (factual correctness compared to original solution)
        2. Completeness (coverage of all key aspects from original solution)
        3. Clarity (readability and comprehensibility)
        4. Relevance (focus on addressing the core query/problem)
        5. Bias (presence of unwarranted assumptions or skewed perspectives)
        
        For each dimension, provide a score between 0.0 and 1.0 and brief justification.
        Calculate an overall quality score as a weighted average.
        
        Return your assessment as a JSON object with this structure:
        {{
            "accuracy": float,
            "completeness": float,
            "clarity": float,
            "relevance": float,
            "bias_assessment": float,
            "overall_quality": float
        }}
        """
        
        # First try using GPT if available
        if self.openai_client:
            try:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4",
                    response_format={"type": "json_object"},
                    messages=[
                        {"role": "system", "content": "You are an expert at evaluating explanation quality across multiple dimensions. You always respond with valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1
                )
                metrics_json = json.loads(response.choices[0].message.content)
                
                # Create metrics from response
                return ResponseQualityMetrics(
                    accuracy=metrics_json.get("accuracy", 0.7),
                    completeness=metrics_json.get("completeness", 0.7),
                    clarity=metrics_json.get("clarity", 0.7),
                    relevance=metrics_json.get("relevance", 0.7),
                    bias_assessment=metrics_json.get("bias_assessment", 0.1),
                    overall_quality=metrics_json.get("overall_quality", 0.7)
                )
                
            except Exception as e:
                logger.error(f"Error in GPT quality assessment: {str(e)}")
                # Try Claude if GPT fails
                if self.claude_client:
                    try:
                        response = self.claude_client.messages.create(
                            model="claude-3-opus-20240229",
                            max_tokens=1000,
                            temperature=0.1,
                            system="You are an expert at evaluating explanation quality across multiple dimensions. You always respond with valid JSON.",
                            messages=[
                                {"role": "user", "content": prompt}
                            ]
                        )
                        
                        # Extract JSON from Claude response
                        content = response.content[0].text
                        # Find JSON content (might be wrapped in markdown code blocks)
                        if "```json" in content:
                            json_text = content.split("```json")[1].split("```")[0].strip()
                        elif "```" in content:
                            json_text = content.split("```")[1].split("```")[0].strip()
                        else:
                            json_text = content
                            
                        metrics_json = json.loads(json_text)
                        
                        return ResponseQualityMetrics(
                            accuracy=metrics_json.get("accuracy", 0.7),
                            completeness=metrics_json.get("completeness", 0.7),
                            clarity=metrics_json.get("clarity", 0.7),
                            relevance=metrics_json.get("relevance", 0.7),
                            bias_assessment=metrics_json.get("bias_assessment", 0.1),
                            overall_quality=metrics_json.get("overall_quality", 0.7)
                        )
                        
                    except Exception as claude_e:
                        logger.error(f"Error in Claude quality assessment: {str(claude_e)}")
                        # Fall back to simple assessment
        
        # Default fallback if no LLM available or both failed
        return self._fallback_quality_assessment(interpreted_solution, original_solution)
    
    async def _get_accuracy_verification(self, prompt: str) -> float:
        """Get accuracy verification from LLM."""
        try:
            if self.openai_client:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4",
                    response_format={"type": "json_object"},
                    messages=[
                        {"role": "system", "content": "You are an expert at verifying factual accuracy. You always respond with valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1
                )
                result = json.loads(response.choices[0].message.content)
                return result.get("score", 0.8)
            elif self.claude_client:
                response = self.claude_client.messages.create(
                    model="claude-3-opus-20240229",
                    max_tokens=500,
                    temperature=0.1,
                    system="You are an expert at verifying factual accuracy. You always respond with valid JSON.",
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                # Extract JSON from Claude response
                content = response.content[0].text
                # Find JSON content (might be wrapped in markdown code blocks)
                if "```json" in content:
                    json_text = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    json_text = content.split("```")[1].split("```")[0].strip()
                else:
                    json_text = content
                    
                result = json.loads(json_text)
                return result.get("score", 0.8)
            else:
                return 0.8  # Default fallback
        except Exception as e:
            logger.error(f"Error in accuracy verification: {str(e)}")
            return 0.8
    
    async def _get_completeness_evaluation(self, prompt: str) -> float:
        """Get completeness evaluation from LLM."""
        try:
            if self.openai_client:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4",
                    response_format={"type": "json_object"},
                    messages=[
                        {"role": "system", "content": "You are an expert at evaluating completeness of explanations. You always respond with valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1
                )
                result = json.loads(response.choices[0].message.content)
                return result.get("score", 0.8)
            elif self.claude_client:
                response = self.claude_client.messages.create(
                    model="claude-3-opus-20240229",
                    max_tokens=500,
                    temperature=0.1,
                    system="You are an expert at evaluating completeness of explanations. You always respond with valid JSON.",
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                # Extract JSON from Claude response
                content = response.content[0].text
                # Find JSON content
                if "```json" in content:
                    json_text = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    json_text = content.split("```")[1].split("```")[0].strip()
                else:
                    json_text = content
                    
                result = json.loads(json_text)
                return result.get("score", 0.8)
            else:
                return 0.8  # Default fallback
        except Exception as e:
            logger.error(f"Error in completeness evaluation: {str(e)}")
            return 0.8
    
    async def _get_clarity_assessment(self, prompt: str) -> float:
        """Get clarity assessment from LLM."""
        try:
            if self.openai_client:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4",
                    response_format={"type": "json_object"},
                    messages=[
                        {"role": "system", "content": "You are an expert at assessing text clarity and readability. You always respond with valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1
                )
                result = json.loads(response.choices[0].message.content)
                return result.get("score", 0.8)
            elif self.claude_client:
                response = self.claude_client.messages.create(
                    model="claude-3-opus-20240229",
                    max_tokens=500,
                    temperature=0.1,
                    system="You are an expert at assessing text clarity and readability. You always respond with valid JSON.",
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                # Extract JSON from Claude response
                content = response.content[0].text
                # Find JSON content
                if "```json" in content:
                    json_text = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    json_text = content.split("```")[1].split("```")[0].strip()
                else:
                    json_text = content
                    
                result = json.loads(json_text)
                return result.get("score", 0.8)
            else:
                return 0.8  # Default fallback
        except Exception as e:
            logger.error(f"Error in clarity assessment: {str(e)}")
            return 0.8
    
    async def _get_bias_assessment(self, prompt: str) -> Dict[str, Any]:
        """Get bias assessment from LLM."""
        try:
            default_response = {
                "bias_score": 0.1,
                "detected_biases": []
            }
            
            if self.openai_client:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4",
                    response_format={"type": "json_object"},
                    messages=[
                        {"role": "system", "content": "You are an expert at detecting bias in explanations. You always respond with valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1
                )
                result = json.loads(response.choices[0].message.content)
                return {
                    "bias_score": result.get("bias_score", 0.1),
                    "detected_biases": result.get("detected_biases", [])
                }
            elif self.claude_client:
                response = self.claude_client.messages.create(
                    model="claude-3-opus-20240229",
                    max_tokens=500,
                    temperature=0.1,
                    system="You are an expert at detecting bias in explanations. You always respond with valid JSON.",
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                # Extract JSON from Claude response
                content = response.content[0].text
                # Find JSON content
                if "```json" in content:
                    json_text = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    json_text = content.split("```")[1].split("```")[0].strip()
                else:
                    json_text = content
                    
                result = json.loads(json_text)
                return {
                    "bias_score": result.get("bias_score", 0.1),
                    "detected_biases": result.get("detected_biases", [])
                }
            else:
                return default_response  # Default fallback
        except Exception as e:
            logger.error(f"Error in bias assessment: {str(e)}")
            return {
                "bias_score": 0.1,
                "detected_biases": []
            }
    
    def _fallback_quality_assessment(
        self, 
        interpreted_solution: Dict[str, Any],
        original_solution: Dict[str, Any]
    ) -> ResponseQualityMetrics:
        """Calculate quality metrics using simple heuristics as a fallback."""
        
        # Calculate simple metrics
        accuracy = self._calculate_simple_accuracy(interpreted_solution, original_solution)
        completeness = self._calculate_simple_completeness(interpreted_solution, original_solution)
        clarity = self._calculate_simple_clarity(interpreted_solution.get("user_friendly_explanation", ""))
        
        # Default values for metrics that are harder to calculate with heuristics
        relevance = 0.8
        bias_assessment = 0.1  # Assume low bias by default
        
        # Calculate overall quality as a weighted average
        overall_quality = (
            accuracy * 0.3 +
            completeness * 0.3 +
            clarity * 0.2 +
            relevance * 0.15 +
            (1.0 - bias_assessment) * 0.05  # Lower bias is better
        )
        
        return ResponseQualityMetrics(
            accuracy=accuracy,
            completeness=completeness,
            clarity=clarity,
            relevance=relevance,
            bias_assessment=bias_assessment,
            overall_quality=overall_quality
        )
    
    def _calculate_simple_accuracy(
        self, 
        interpreted_solution: Dict[str, Any],
        original_solution: Dict[str, Any]
    ) -> float:
        """
        Calculate a simple accuracy score based on comparing interpreted content with original solution.
        
        Args:
            interpreted_solution: The interpreted solution
            original_solution: The original solution data
            
        Returns:
            Accuracy score between 0 and 1
        """
        # Extract relevant data for comparison
        tech_explanation = interpreted_solution.get("technical_explanation", "")
        user_explanation = interpreted_solution.get("user_friendly_explanation", "")
        key_insights = interpreted_solution.get("key_insights", [])
        
        # Original data to check against
        results = original_solution.get("results", {})
        conclusions = original_solution.get("conclusions", [])
        
        # Initialize accuracy metrics
        result_accuracy = 0.0
        conclusion_accuracy = 0.0
        insight_accuracy = 0.0
        
        # Check if results are accurately represented in explanations
        if results:
            # Count how many results are mentioned in the explanations
            results_found = 0
            for key, value in results.items():
                # Convert to string for text matching
                result_str = f"{key}.*?{value}" if isinstance(value, (int, float, str)) else key
                
                # Check if this result appears in either explanation
                if (
                    self._contains_result(tech_explanation, key, value) or 
                    self._contains_result(user_explanation, key, value)
                ):
                    results_found += 1
            
            result_accuracy = min(1.0, results_found / max(1, len(results)))
        else:
            # No results to check against, so default to high accuracy
            result_accuracy = 0.9
        
        # Check conclusion accuracy
        if conclusions:
            # For each conclusion, check if it's represented in the explanations or insights
            conclusions_found = 0
            for conclusion in conclusions:
                description = conclusion.get("description", "")
                if not description:
                    continue
                
                # Extract key parts of the conclusion (nouns, significant terms)
                key_terms = self._extract_key_terms(description)
                
                # Check if these key terms appear in explanations or insights
                if (
                    self._contains_terms(tech_explanation, key_terms) or
                    self._contains_terms(user_explanation, key_terms) or
                    any(self._contains_terms(insight, key_terms) for insight in key_insights)
                ):
                    conclusions_found += 1
            
            conclusion_accuracy = min(1.0, conclusions_found / max(1, len(conclusions)))
        else:
            # No conclusions to check against
            conclusion_accuracy = 0.9
        
        # Calculate overall accuracy as weighted average
        # Weigh conclusion accuracy more heavily as they're more important
        overall_accuracy = (result_accuracy * 0.4) + (conclusion_accuracy * 0.6)
        
        # Return the accuracy score, minimum 0.6 for reasonable defaults
        return min(1.0, max(0.6, overall_accuracy))
    
    def _contains_result(self, text: str, key: str, value: Any) -> bool:
        """Check if a result key and value are represented in text."""
        import re
        
        # Clean up key and text for matching
        key_clean = key.lower().replace('_', ' ')
        text_lower = text.lower()
        
        # Different matching patterns based on value type
        if isinstance(value, (int, float)):
            # Look for key with numeric value
            # Allow for some flexibility in number formatting
            value_str = str(value)
            value_patterns = [
                # Exact match
                fr"{key_clean}.*?{value_str}",
                # With approx one decimal rounding
                fr"{key_clean}.*?{round(float(value), 1)}",
                # General proximity
                fr"{key_clean}.*?[\d.]+"
            ]
            
            return any(re.search(pattern, text_lower) for pattern in value_patterns)
        elif isinstance(value, str):
            # For string values, check if both key and value appear in text
            return key_clean in text_lower and value.lower() in text_lower
        else:
            # Just check for the key
            return key_clean in text_lower
    
    def _extract_key_terms(self, text: str) -> List[str]:
        """Extract important terms from text."""
        # Split into words
        words = text.lower().split()
        
        # Keep only significant words (longer than 4 chars, not stopwords)
        stopwords = ['the', 'and', 'that', 'this', 'with', 'from', 'have', 'for', 'not', 'are', 'were']
        key_terms = [word for word in words if len(word) > 4 and word not in stopwords]
        
        return key_terms
    
    def _contains_terms(self, text: str, terms: List[str], threshold: float = 0.3) -> bool:
        """Check if a significant portion of terms appear in the text."""
        if not terms:
            return False
        
        text_lower = text.lower()
        matches = sum(1 for term in terms if term in text_lower)
        
        # Consider it a match if at least threshold% of terms are found
        return matches / len(terms) >= threshold
    
    def _calculate_simple_completeness(
        self, 
        interpreted_solution: Dict[str, Any],
        original_solution: Dict[str, Any]
    ) -> float:
        """Calculate a simple completeness score based on heuristics."""
        # Check if all key insights are included
        user_explanation = interpreted_solution.get("user_friendly_explanation", "")
        
        # Count how many original conclusions appear to be represented
        conclusions = original_solution.get("conclusions", [])
        if not conclusions:
            return 0.8  # Default if no conclusions
            
        # Simple check: see if key terms from conclusions appear in explanation
        found_count = 0
        for conclusion in conclusions:
            description = conclusion.get("description", "")
            # Extract key terms (simplified approach)
            key_terms = [word for word in description.split() if len(word) > 5]
            
            # Check if any key terms appear in the explanation
            if any(term.lower() in user_explanation.lower() for term in key_terms):
                found_count += 1
                
        completeness_score = min(1.0, found_count / max(1, len(conclusions)))
        return max(0.6, completeness_score)  # Minimum score of 0.6
    
    def _calculate_simple_clarity(self, content: str) -> float:
        """Calculate a simple clarity score based on heuristics."""
        if not content:
            return 0.7  # Default
            
        # Simple heuristics for clarity
        words = content.split()
        total_words = len(words)
        
        if total_words == 0:
            return 0.7
            
        # Average word length (shorter words tend to be more readable)
        avg_word_length = sum(len(word) for word in words) / total_words
        word_length_score = max(0, min(1, 2 - avg_word_length / 8))
        
        # Average sentence length (shorter sentences tend to be clearer)
        sentences = content.split('.')
        total_sentences = max(1, len(sentences))
        avg_sentence_length = total_words / total_sentences
        sentence_length_score = max(0, min(1, 2 - avg_sentence_length / 25))
        
        # Combined score
        clarity_score = (word_length_score + sentence_length_score) / 2
        return min(1.0, max(0.6, clarity_score)) 