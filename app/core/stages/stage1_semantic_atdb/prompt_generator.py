import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class PromptGenerator:
    """
    Generates enhanced semantic prompts for different scenarios.
    
    This class creates specialized prompts for semantic analysis,
    incorporating the enhanced semantics approach and adapting for
    different bypassing strategies.
    """
    
    def __init__(self):
        """Initialize the prompt generator."""
        pass
    
    def create_semantic_prompt(
        self, 
        enhancements: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create the enhanced semantic prompt with optional customizations.
        
        Args:
            enhancements: Optional customizations to the prompt
            
        Returns:
            The formatted system prompt
        """
        # Base semantic prompt
        base_prompt = """
You are the Query Transformation Module (Stage 1) in a seven-stage optimization pipeline.

Your sole purpose is to be the ultimate meaning finder - analyzing user queries to extract their precise intent, structure, and implicit tasks. You excel at dimensional reduction, transforming ambiguous natural language into structured, actionable representations.

For each query, perform an exhaustive analysis to:

1. INTENT DISCOVERY:
   - Identify primary intent (informational, computational, comparative, or predictive)
   - Uncover secondary or implicit intents that may not be explicitly stated
   - Assess if the query contains multiple nested questions or requests

2. SUBJECT EXTRACTION:
   - Determine the central subject and any peripheral subjects
   - Extract specific attributes or properties of interest
   - Identify contextual boundaries of the subject matter

3. PARAMETER IDENTIFICATION:
   - Extract explicit parameters mentioned in the query
   - Infer implicit parameters that would be necessary to answer completely
   - Determine relationships between parameters

4. QUERY REFORMULATION:
   - Restructure the query to eliminate ambiguity
   - Make implicit questions explicit
   - Ensure all necessary parameters for downstream processing are captured

Format your response as a JSON object with the following structure:
{
  "intentClassification": "string",
  "keySubject": "string", 
  "parametersOfInterest": ["string"],
  "confidence": number,
  "reasoning": "string",
  "reformulatedQuery": "string"
}

Your task is critical as it determines how the query will be processed through the remaining six stages of the pipeline. Focus exclusively on understanding the full meaning and structure of the query, not on answering it.
"""

        # If no enhancements, return base prompt
        if not enhancements:
            return base_prompt.strip()
        
        # Apply enhancements
        enhanced_prompt = base_prompt
        
        # Add focus instructions if provided
        if "focus_instruction" in enhancements:
            enhanced_prompt += f"\n\nIMPORTANT: {enhancements['focus_instruction']}"
        
        # Add depth instructions if provided
        if "depth_instruction" in enhancements:
            enhanced_prompt += f"\n\nDEPTH INSTRUCTION: {enhancements['depth_instruction']}"
        
        # Add parameter exploration emphasis if needed
        if enhancements.get("increase_parameter_exploration", False):
            enhanced_prompt += """

IMPORTANT: Your primary task is PARAMETER EXPLORATION. You must:
- Be exhaustive in identifying parameters
- Go beyond obvious parameters to find subtle or implicit ones
- Consider specialized domain parameters that experts would recognize
- Explore interconnections between parameters
- Consider edge cases and unusual parameters"""
        
        # Force exhaustive analysis if specified
        if enhancements.get("force_exhaustive_analysis", False):
            enhanced_prompt += """

EXHAUSTIVE ANALYSIS REQUIRED: Do not stop at surface level understanding. Dig deeper:
- Consider all possible interpretations of the query
- Identify obscure or rarely considered parameters
- Ensure complete coverage of the domain space
- Leave no possible parameter unidentified"""
        
        # Add prior knowledge incorporation if provided
        if "prior_knowledge" in enhancements:
            knowledge = enhancements["prior_knowledge"]
            parameters_str = ", ".join(knowledge.get("parameters", []))
            enhanced_prompt += f"""

INCORPORATE PRIOR KNOWLEDGE: Build upon these previously identified elements:
- Parameters already identified: {parameters_str}
- Known intent: {knowledge.get("intent", "unknown")}
- Central subject: {knowledge.get("subject", "unknown")}"""
        
        # Add iteration-specific instructions if specified
        if "iteration" in enhancements and "instruction" in enhancements:
            enhanced_prompt += f"""

ITERATION {enhancements['iteration']} INSTRUCTION: {enhancements['instruction']}"""
        
        # Return the enhanced prompt
        return enhanced_prompt.strip()
