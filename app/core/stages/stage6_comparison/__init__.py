"""
Response Comparison Stage

This stage compares and combines multiple response candidates by implementing
ensemble diversification, computing pairwise diversity scores, and optimizing
the balance between quality and diversity.
"""

from app.core.stages.stage6_comparison.response_comparison_service import ResponseComparisonService

__all__ = ["ResponseComparisonService"] 