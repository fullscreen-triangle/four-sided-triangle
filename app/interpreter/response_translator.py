from typing import Dict, Any, List, Optional
import openai
import anthropic
import os
import json
import logging

from app.interpreter.models import InterpretedSolution

logger = logging.getLogger(__name__)

class ResponseTranslator:
    def __init__(self, openai_client=None, claude_client=None):
        self.openai_client = openai_client
        self.claude_client = claude_client

    async def translate_technical_content(
        self, 
        technical_content: Dict[str, Any], 
        user_context: Dict[str, Any]
    ) -> str:
        """
        Converts domain-specific technical content to an appropriate level for the user.
        
        Args:
            technical_content: The technical solution with domain-specific terms
            user_context: Information about the user's expertise level and preferences
            
        Returns:
            User-friendly explanation at the appropriate technical level
        """
        expertise_level = user_context.get("expertise_level", "general")
        
        # Prepare prompt for translation
        prompt = self._build_translation_prompt(technical_content, expertise_level)
        
        # Use LLM to translate content
        try:
            response = await self._get_llm_translation(prompt, user_context)
            return response
        except Exception as e:
            logger.error(f"Error translating technical content: {str(e)}")
            # Fallback to simplified content
            return self._generate_fallback_explanation(technical_content)
    
    async def build_narrative(
        self, 
        reasoning_steps: List[Dict[str, Any]],
        conclusions: List[Dict[str, Any]],
        user_context: Dict[str, Any]
    ) -> str:
        """
        Builds a cohesive explanatory narrative from reasoning steps.
        
        Args:
            reasoning_steps: List of reasoning steps from the solver
            conclusions: List of conclusions drawn from the solution
            user_context: Information about the user's expertise level and preferences
            
        Returns:
            Cohesive narrative explanation
        """
        # Prepare the prompt for the narrative builder
        prompt = self._build_narrative_prompt(reasoning_steps, conclusions, user_context)
        
        try:
            response = await self._get_llm_narrative(prompt, user_context)
            return response
        except Exception as e:
            logger.error(f"Error building narrative: {str(e)}")
            return self._generate_fallback_narrative(reasoning_steps, conclusions)
    
    async def enhance_clarity(
        self, 
        content: str,
        key_concepts: List[str],
        user_context: Dict[str, Any]
    ) -> str:
        """
        Improves explanation clarity and readability.
        
        Args:
            content: The content to enhance
            key_concepts: Key concepts that should be clearly explained
            user_context: Information about the user
            
        Returns:
            Enhanced content with improved clarity
        """
        # Prepare the prompt for clarity enhancement
        prompt = self._build_clarity_prompt(content, key_concepts, user_context)
        
        try:
            response = await self._get_llm_clarity_enhancement(prompt)
            return response
        except Exception as e:
            logger.error(f"Error enhancing clarity: {str(e)}")
            return content  # Return original content as fallback
    
    def _build_translation_prompt(
        self, 
        technical_content: Dict[str, Any], 
        expertise_level: str
    ) -> str:
        """Build prompt for translating technical content to appropriate level."""
        
        # Convert technical content to formatted text
        formatted_content = json.dumps(technical_content, indent=2)
        
        prompt = f"""
        Task: Translate the following technical content to a {expertise_level} audience level.
        
        Technical Content:
        {formatted_content}
        
        Guidelines:
        - For 'beginner' level: Explain concepts in simple terms, avoid jargon, use analogies
        - For 'intermediate' level: Use some field-specific terms but explain them
        - For 'expert' level: Use precise technical language appropriate for specialists
        - For 'general' level: Balance accessibility with some technical depth
        
        Your translation should be accurate, clear, and appropriate for the specified audience level.
        Focus on making the key points and conclusions understandable while maintaining accuracy.
        """
        
        return prompt
    
    def _build_narrative_prompt(
        self, 
        reasoning_steps: List[Dict[str, Any]],
        conclusions: List[Dict[str, Any]],
        user_context: Dict[str, Any]
    ) -> str:
        """Build prompt for creating a cohesive narrative."""
        
        # Convert reasoning steps to formatted text
        formatted_steps = json.dumps(reasoning_steps, indent=2)
        formatted_conclusions = json.dumps(conclusions, indent=2)
        
        prompt = f"""
        Task: Build a cohesive explanatory narrative from these reasoning steps and conclusions.
        
        Reasoning Steps:
        {formatted_steps}
        
        Conclusions:
        {formatted_conclusions}
        
        User Context:
        Expertise level: {user_context.get('expertise_level', 'general')}
        Preferred detail level: {user_context.get('detail_preference', 'balanced')}
        
        Guidelines:
        - Create a logical flow that explains how the reasoning led to the conclusions
        - Highlight key insights and important relationships
        - Use appropriate language for the user's expertise level
        - Balance technical accuracy with understandability
        - Focus on the most confident and important conclusions
        
        Your narrative should tell a cohesive story about how the solution was reached.
        """
        
        return prompt
    
    def _build_clarity_prompt(
        self, 
        content: str,
        key_concepts: List[str],
        user_context: Dict[str, Any]
    ) -> str:
        """Build prompt for enhancing clarity."""
        
        # Format key concepts
        formatted_concepts = "\n".join([f"- {concept}" for concept in key_concepts])
        
        prompt = f"""
        Task: Enhance the clarity and readability of the following explanation.
        
        Original Content:
        {content}
        
        Key Concepts That Must Be Clear:
        {formatted_concepts}
        
        User Context:
        Expertise level: {user_context.get('expertise_level', 'general')}
        
        Guidelines:
        - Improve sentence structure for readability
        - Define technical terms appropriately for the user's level
        - Use clear transitions between ideas
        - Ensure logical flow from one point to the next
        - Maintain accuracy while improving clarity
        - Highlight important relationships and connections
        
        Your enhanced explanation should be clearer and more readable while preserving
        all important information and technical accuracy.
        """
        
        return prompt
    
    async def _get_llm_translation(
        self, 
        prompt: str, 
        user_context: Dict[str, Any]
    ) -> str:
        """Get translation response from LLM based on user preferences."""
        
        preferred_model = user_context.get("preferred_model", "gpt-4")
        
        if "gpt" in preferred_model and self.openai_client:
            return await self._get_gpt_response(prompt, preferred_model)
        elif "claude" in preferred_model and self.claude_client:
            return await self._get_claude_response(prompt)
        else:
            # Default to GPT if available
            if self.openai_client:
                return await self._get_gpt_response(prompt, "gpt-4")
            elif self.claude_client:
                return await self._get_claude_response(prompt)
            else:
                raise ValueError("No LLM client available")
    
    async def _get_llm_narrative(
        self, 
        prompt: str, 
        user_context: Dict[str, Any]
    ) -> str:
        """Get narrative building response from LLM."""
        # Use same logic as translation
        return await self._get_llm_translation(prompt, user_context)
    
    async def _get_llm_clarity_enhancement(
        self, 
        prompt: str
    ) -> str:
        """Get clarity enhancement from LLM."""
        # Default to GPT-4 for clarity enhancement if available
        if self.openai_client:
            return await self._get_gpt_response(prompt, "gpt-4")
        elif self.claude_client:
            return await self._get_claude_response(prompt)
        else:
            raise ValueError("No LLM client available")
    
    async def _get_gpt_response(
        self, 
        prompt: str, 
        model: str = "gpt-4"
    ) -> str:
        """Get response from OpenAI GPT model."""
        try:
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are an expert at translating technical content to appropriate audience levels while maintaining accuracy."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1500
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error getting GPT response: {str(e)}")
            raise
    
    async def _get_claude_response(
        self, 
        prompt: str, 
        model: str = "claude-3-opus-20240229"
    ) -> str:
        """Get response from Anthropic Claude model."""
        try:
            response = self.claude_client.messages.create(
                model=model,
                max_tokens=1500,
                temperature=0.3,
                system="You are an expert at translating technical content to appropriate audience levels while maintaining accuracy.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Error getting Claude response: {str(e)}")
            raise
    
    def _generate_fallback_explanation(
        self, 
        technical_content: Dict[str, Any]
    ) -> str:
        """Generate a simple fallback explanation if LLM fails."""
        # Extract key information from technical content
        results = technical_content.get("results", {})
        conclusions = technical_content.get("conclusions", [])
        
        # Build a simple explanation
        explanation = "Based on the analysis, "
        
        if conclusions:
            explanation += "the main findings are: "
            for i, conclusion in enumerate(conclusions[:3]):  # Show top 3 conclusions
                if i > 0:
                    explanation += "; "
                explanation += conclusion.get("description", "")
        
        if results:
            explanation += "\n\nKey results include: "
            for i, (key, value) in enumerate(list(results.items())[:5]):  # Show top 5 results
                if i > 0:
                    explanation += ", "
                explanation += f"{key}: {value}"
        
        return explanation
    
    def _generate_fallback_narrative(
        self, 
        reasoning_steps: List[Dict[str, Any]],
        conclusions: List[Dict[str, Any]]
    ) -> str:
        """Generate a simple fallback narrative if LLM fails."""
        narrative = "Analysis process: "
        
        # Add simplified steps description
        for i, step in enumerate(reasoning_steps):
            if i > 0:
                narrative += "\n"
            narrative += f"{i+1}. {step.get('description', 'Analysis step')}"
        
        # Add conclusions
        if conclusions:
            narrative += "\n\nConclusions: "
            for i, conclusion in enumerate(conclusions):
                if i > 0:
                    narrative += "\n"
                narrative += f"- {conclusion.get('description', 'Finding')}"
        
        return narrative 