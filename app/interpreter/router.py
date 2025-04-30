from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
import logging

from app.interpreter import InterpreterService, InterpretationResponse, InterpretationRequest
from app.utils.helpers import timer_decorator
from app.utils.utils import error_handler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create router without prefix (it will be added in main.py)
router = APIRouter(tags=["Interpreter"])

# Create interpreter service instance
interpreter_service = InterpreterService()

def get_interpreter():
    """
    Dependency to get the interpreter service instance.
    """
    return interpreter_service

@router.post(
    "/interpret",
    response_model=InterpretationResponse
)
@timer_decorator
@error_handler
async def interpret_solution(
    request: InterpretationRequest,
    interpreter: InterpreterService = Depends(get_interpreter)
):
    """
    Interpret a solution package from the solver.
    """
    return await interpreter.interpret_solution(request)

@router.post(
    "/assess-quality"
)
@timer_decorator
@error_handler
async def assess_quality(
    interpreted_solution: Dict[str, Any],
    original_solution: Dict[str, Any],
    interpreter: InterpreterService = Depends(get_interpreter)
):
    """
    Assess the quality of an interpreted solution.
    """
    quality_assessor = interpreter.quality_assessor
    return await quality_assessor.assess_quality(
        interpreted_solution,
        original_solution,
        {}  # Empty domain knowledge as fallback
    )

@router.post(
    "/enhance-clarity"
)
@timer_decorator
@error_handler
async def enhance_clarity(
    content: str,
    key_concepts: List[str],
    expertise_level: str,
    interpreter: InterpreterService = Depends(get_interpreter)
):
    """
    Enhance the clarity of an explanation.
    """
    translator = interpreter.response_translator
    user_context = {"expertise_level": expertise_level}
    
    enhanced_content = await translator.enhance_clarity(
        content,
        key_concepts,
        user_context
    )
    
    return {"enhancedContent": enhanced_content}

@router.post(
    "/follow-ups"
)
@timer_decorator
@error_handler
async def generate_follow_ups(
    interpreted_solution: Dict[str, Any],
    user_context: Dict[str, Any],
    interpreter: InterpreterService = Depends(get_interpreter)
):
    """
    Generate follow-up suggestions based on the interpretation.
    """
    # Extract key insights for follow-up generation
    key_insights = interpreted_solution.get("key_insights", [])
    
    # Format insights as proper conclusion objects
    conclusions = []
    for i, insight in enumerate(key_insights):
        conclusions.append({
            "id": f"insight_{i}",
            "description": insight,
            "statement": insight,
            "confidence": 0.8,
            "parameters": {},
            "supportingEvidence": []
        })
    
    suggestions = await interpreter._generate_follow_up_suggestions(
        conclusions,
        user_context
    )
    
    return {"suggestions": suggestions}

@router.post(
    "/translate-content"
)
@timer_decorator
@error_handler
async def translate_content(
    technical_content: Dict[str, Any],
    user_context: Dict[str, Any],
    interpreter: InterpreterService = Depends(get_interpreter)
):
    """
    Translate technical content to user-friendly language.
    """
    translator = interpreter.response_translator
    translated_content = await translator.translate_technical_content(
        technical_content,
        user_context
    )
    
    return {"translatedContent": translated_content} 