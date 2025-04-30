"""
Prompt generator implementation for the Four-Sided Triangle system.

This module provides a default implementation of the prompt generator
that creates prompts for various stages in the orchestration pipeline.
"""

import logging
from typing import Dict, Any, Optional, List

from app.orchestrator.interfaces import PromptGeneratorInterface, WorkingMemoryInterface

logger = logging.getLogger(__name__)

class DefaultPromptGenerator(PromptGeneratorInterface):
    """
    Default implementation of the prompt generator.
    
    This class creates prompts for various stages in the orchestration pipeline
    based on stage requirements, working memory, and system templates.
    """
    
    def __init__(self, templates_path: str = "app/orchestrator/templates"):
        """
        Initialize the prompt generator.
        
        Args:
            templates_path: Path to the prompt templates directory
        """
        self.templates_path = templates_path
        self._templates = self._load_templates()
        logger.info("DefaultPromptGenerator initialized with templates from %s", templates_path)
    
    def generate_stage_prompt(
        self, 
        stage_id: str, 
        working_memory: Dict[str, Any], 
        stage_config: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate a prompt for a specific pipeline stage.
        
        Args:
            stage_id: Identifier for the pipeline stage
            working_memory: Current working memory content
            stage_config: Optional stage-specific configuration
            
        Returns:
            Formatted prompt string for the stage
        """
        template = self._get_template_for_stage(stage_id)
        
        # Extract relevant context from working memory
        context = self._extract_context_for_stage(stage_id, working_memory)
        
        # Apply stage-specific configuration
        if stage_config:
            context.update(stage_config)
            
        # Format the template with the context
        try:
            prompt = template.format(**context)
            logger.debug("Generated prompt for stage %s", stage_id)
            return prompt
        except KeyError as e:
            logger.error("Missing template variable for stage %s: %s", stage_id, e)
            # Provide a basic fallback prompt
            return f"Process the following query: {working_memory.get('original_query', '')}"
    
    def generate_refinement_prompt(
        self, 
        stage_id: str, 
        working_memory: Dict[str, Any], 
        feedback: Dict[str, Any]
    ) -> str:
        """
        Generate a refinement prompt based on feedback.
        
        Args:
            stage_id: Identifier for the pipeline stage
            working_memory: Current working memory content
            feedback: Feedback on previous output
            
        Returns:
            Formatted refinement prompt string
        """
        template = self._get_refinement_template_for_stage(stage_id)
        
        # Extract relevant context from working memory
        context = self._extract_context_for_stage(stage_id, working_memory)
        
        # Add feedback to context
        context['feedback'] = feedback
        
        # Format the template with the context
        try:
            prompt = template.format(**context)
            logger.debug("Generated refinement prompt for stage %s", stage_id)
            return prompt
        except KeyError as e:
            logger.error("Missing template variable for refinement prompt %s: %s", stage_id, e)
            # Provide a basic fallback refinement prompt
            return (f"Refine your previous output based on the following feedback: "
                   f"{feedback.get('summary', 'Please improve your response.')}")
    
    def generate_system_prompt(self, stage_id: str) -> str:
        """
        Generate a system prompt for a specific stage.
        
        Args:
            stage_id: Identifier for the pipeline stage
            
        Returns:
            System prompt string for the stage
        """
        template = self._get_system_template_for_stage(stage_id)
        return template
    
    def _load_templates(self) -> Dict[str, Dict[str, str]]:
        """
        Load prompt templates from the templates directory.
        
        Returns:
            Dictionary of templates organized by stage
        """
        # This is a simplified implementation that uses hardcoded templates
        # In a real implementation, this would load templates from files
        
        templates = {
            "query_processor": {
                "main": "Process the following query:\n\n{original_query}\n\nContext: {context}",
                "refinement": "Refine your processing of the query based on this feedback:\n\n{feedback['summary']}\n\nOriginal query: {original_query}",
                "system": "You are a query processor. Your job is to understand the user's query and extract key information."
            },
            "retriever": {
                "main": "Retrieve relevant information for the following query:\n\n{processed_query}\n\nFocus on: {focus_areas}",
                "refinement": "Refine your retrieval based on this feedback:\n\n{feedback['summary']}\n\nQuery: {processed_query}",
                "system": "You are a retrieval system. Your job is to find the most relevant information for the query."
            },
            "solver": {
                "main": "Solve the following query using the retrieved information:\n\n{processed_query}\n\nRetrieved information: {retrieved_information}",
                "refinement": "Refine your solution based on this feedback:\n\n{feedback['summary']}\n\nQuery: {processed_query}",
                "system": "You are a problem solver. Your job is to provide an accurate solution to the query using the retrieved information."
            },
            "interpreter": {
                "main": "Interpret and explain the solution in a user-friendly way:\n\n{solution}\n\nOriginal query: {original_query}\n\nUser expertise level: {user_expertise_level}",
                "refinement": "Refine your interpretation based on this feedback:\n\n{feedback['summary']}\n\nSolution: {solution}",
                "system": "You are an interpreter. Your job is to explain solutions in a way that is clear and appropriate for the user's expertise level."
            },
            "default": {
                "main": "Process the following input:\n\n{input}\n\nContext: {context}",
                "refinement": "Refine your output based on this feedback:\n\n{feedback['summary']}\n\nOriginal input: {input}",
                "system": "You are an AI assistant processing a stage in the Four-Sided Triangle system."
            }
        }
        
        return templates
    
    def _get_template_for_stage(self, stage_id: str) -> str:
        """
        Get the appropriate prompt template for a stage.
        
        Args:
            stage_id: Identifier for the pipeline stage
            
        Returns:
            Template string for the stage
        """
        if stage_id in self._templates:
            return self._templates[stage_id]["main"]
        
        logger.warning("No template found for stage %s, using default", stage_id)
        return self._templates["default"]["main"]
    
    def _get_refinement_template_for_stage(self, stage_id: str) -> str:
        """
        Get the appropriate refinement template for a stage.
        
        Args:
            stage_id: Identifier for the pipeline stage
            
        Returns:
            Refinement template string for the stage
        """
        if stage_id in self._templates:
            return self._templates[stage_id]["refinement"]
        
        logger.warning("No refinement template found for stage %s, using default", stage_id)
        return self._templates["default"]["refinement"]
    
    def _get_system_template_for_stage(self, stage_id: str) -> str:
        """
        Get the appropriate system template for a stage.
        
        Args:
            stage_id: Identifier for the pipeline stage
            
        Returns:
            System template string for the stage
        """
        if stage_id in self._templates:
            return self._templates[stage_id]["system"]
        
        logger.warning("No system template found for stage %s, using default", stage_id)
        return self._templates["default"]["system"]
    
    def _extract_context_for_stage(self, stage_id: str, working_memory: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract relevant context from working memory for a stage.
        
        Args:
            stage_id: Identifier for the pipeline stage
            working_memory: Current working memory content
            
        Returns:
            Dictionary with relevant context for the stage
        """
        # Start with the full working memory
        context = working_memory.copy()
        
        # Add some defaults in case keys are missing
        context.setdefault('original_query', '')
        context.setdefault('processed_query', context.get('original_query', ''))
        context.setdefault('context', {})
        context.setdefault('focus_areas', [])
        context.setdefault('retrieved_information', [])
        context.setdefault('solution', {})
        context.setdefault('user_expertise_level', 'intermediate')
        
        return context

# Global singleton instance
prompt_generator = DefaultPromptGenerator()
