"""
Domain Knowledge Extraction Stage

This stage retrieves specialized domain knowledge from expert language models,
prioritizes it by relevance, and establishes confidence levels for knowledge elements.
"""

from app.core.stages.stage2_domain_knowledge.domain_knowledge_service import DomainKnowledgeService

__all__ = ["DomainKnowledgeService"]