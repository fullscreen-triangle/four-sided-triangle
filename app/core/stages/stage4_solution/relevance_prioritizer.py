"""
Relevance Prioritizer

This module contains the RelevancePrioritizer class, which is responsible for
prioritizing information by relevance, novelty, and user intent alignment.
"""

import logging
from typing import Dict, Any, List, Optional, Set, Tuple

class RelevancePrioritizer:
    """
    Prioritizes information elements based on relevance, novelty, and user intent alignment.
    
    This class analyzes and ranks information elements to identify which ones are most
    important to include in the solution based on their relationship to the query and
    their information value.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Relevance Prioritizer.
        
        Args:
            config: Configuration dictionary for prioritization parameters
        """
        self.logger = logging.getLogger(__name__)
        self.config = config or {}
        
        # Prioritization parameters
        self.relevance_threshold = self.config.get("relevance_threshold", 0.5)
        self.novelty_weight = self.config.get("novelty_weight", 0.3)
        self.intent_alignment_weight = self.config.get("intent_alignment_weight", 0.4)
        self.explicit_request_bonus = self.config.get("explicit_request_bonus", 0.15)
        
        self.logger.info("Relevance Prioritizer initialized")
    
    async def prioritize(self, domain_knowledge: Dict[str, Any], 
                        original_query: Dict[str, Any],
                        context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prioritize information elements based on relevance to the query and novelty.
        
        Args:
            domain_knowledge: Domain knowledge from the knowledge extraction stage
            original_query: The original user query with metadata
            context: Context data from the orchestrator
            
        Returns:
            Prioritized information elements
        """
        self.logger.info("Starting information prioritization")
        
        # Extract query metadata
        query_intent = original_query.get("intent", {})
        query_entities = original_query.get("entities", [])
        query_constraints = original_query.get("constraints", {})
        query_text = original_query.get("text", "")
        
        # Extract knowledge elements
        knowledge_elements = domain_knowledge.get("elements", [])
        self.logger.info(f"Processing {len(knowledge_elements)} knowledge elements")
        
        # Step 1: Detect explicit information requests
        explicit_requests = self._detect_explicit_requests(query_text, query_entities)
        self.logger.info(f"Detected {len(explicit_requests)} explicit information requests")
        
        # Step 2: Calculate initial relevance scores
        scored_elements = self._calculate_relevance_scores(
            knowledge_elements, 
            query_intent,
            query_entities, 
            explicit_requests
        )
        
        # Step 3: Calculate novelty scores
        scored_elements = self._calculate_novelty_scores(scored_elements, context)
        
        # Step 4: Apply intent alignment adjustment
        scored_elements = self._align_with_user_intent(scored_elements, query_intent, query_constraints)
        
        # Step 5: Prioritize and label elements
        prioritized_elements = self._prioritize_elements(scored_elements)
        
        # Step 6: Group related elements
        element_groups = self._group_related_elements(prioritized_elements)
        
        # Create the final output structure
        result = {
            "elements": prioritized_elements,
            "element_groups": element_groups,
            "priority_metrics": {
                "high_priority_count": sum(1 for e in prioritized_elements if e.get("prominence") == "high"),
                "medium_priority_count": sum(1 for e in prioritized_elements if e.get("prominence") == "medium"),
                "low_priority_count": sum(1 for e in prioritized_elements if e.get("prominence") == "low"),
                "avg_relevance_score": sum(e.get("relevance_score", 0) for e in prioritized_elements) / len(prioritized_elements) if prioritized_elements else 0,
                "explicit_requests": list(explicit_requests)
            },
            "prioritization_parameters": {
                "relevance_threshold": self.relevance_threshold,
                "novelty_weight": self.novelty_weight,
                "intent_alignment_weight": self.intent_alignment_weight,
                "explicit_request_bonus": self.explicit_request_bonus
            }
        }
        
        self.logger.info("Information prioritization completed")
        return result
    
    def _detect_explicit_requests(self, query_text: str, query_entities: List[Dict[str, Any]]) -> Set[str]:
        """
        Detect explicit requests for information in the query.
        
        Args:
            query_text: The raw query text
            query_entities: Entities extracted from the query
            
        Returns:
            Set of explicitly requested information types
        """
        explicit_requests = set()
        
        # Look for request indicators in the query text
        request_indicators = [
            "explain", "describe", "tell me about", "information on",
            "details", "specifics", "how does", "what is", "when did",
            "why does", "show me", "provide", "give me"
        ]
        
        query_lower = query_text.lower()
        
        # Extract entity names for matching
        entity_names = [entity.get("name", "").lower() for entity in query_entities]
        entity_types = [entity.get("type", "").lower() for entity in query_entities]
        
        # Check for explicit requests
        for indicator in request_indicators:
            if indicator in query_lower:
                # Find the position of the indicator
                indicator_pos = query_lower.find(indicator)
                
                # Extract text after the indicator to identify what was requested
                text_after = query_lower[indicator_pos + len(indicator):].strip()
                
                # Match with entities
                for entity_name, entity_type in zip(entity_names, entity_types):
                    if entity_name in text_after:
                        explicit_requests.add(entity_type)
                        explicit_requests.add(entity_name)
        
        # Also add all entity types as potential explicit requests
        explicit_requests.update(entity_types)
        
        return explicit_requests
    
    def _calculate_relevance_scores(self, knowledge_elements: List[Dict[str, Any]],
                                  query_intent: Dict[str, Any],
                                  query_entities: List[Dict[str, Any]],
                                  explicit_requests: Set[str]) -> List[Dict[str, Any]]:
        """
        Calculate relevance scores for knowledge elements.
        
        Args:
            knowledge_elements: Domain knowledge elements
            query_intent: Intent information from the query
            query_entities: Entities extracted from the query
            explicit_requests: Set of explicitly requested information
            
        Returns:
            Knowledge elements with relevance scores
        """
        scored_elements = []
        
        # Extract entity names and types for matching
        entity_names = [entity.get("name", "").lower() for entity in query_entities]
        entity_types = [entity.get("type", "").lower() for entity in query_entities]
        entity_ids = [entity.get("id", "") for entity in query_entities]
        
        for element in knowledge_elements:
            element_copy = element.copy()
            
            # Initial relevance is based on the element's raw relevance from domain knowledge
            base_relevance = element.get("relevance", 0.5)
            
            # Entity match bonus
            entity_match_score = self._calculate_entity_match(
                element, entity_names, entity_types, entity_ids
            )
            
            # Intent alignment score
            intent_match_score = self._calculate_intent_match(element, query_intent)
            
            # Explicit request bonus
            explicit_bonus = 0.0
            element_type = element.get("type", "").lower()
            element_domain = element.get("domain", "").lower()
            
            for request in explicit_requests:
                if (request in element_type or 
                    request in element_domain or 
                    request in element.get("keywords", [])):
                    explicit_bonus = self.explicit_request_bonus
                    break
            
            # Combine scores
            relevance_score = (
                base_relevance * 0.4 +
                entity_match_score * 0.3 +
                intent_match_score * 0.3 +
                explicit_bonus
            )
            
            # Cap at 1.0
            element_copy["relevance_score"] = min(relevance_score, 1.0)
            
            # Track the score components for debugging
            element_copy["relevance_components"] = {
                "base_relevance": base_relevance,
                "entity_match_score": entity_match_score,
                "intent_match_score": intent_match_score,
                "explicit_bonus": explicit_bonus
            }
            
            scored_elements.append(element_copy)
        
        return scored_elements
    
    def _calculate_entity_match(self, element: Dict[str, Any], 
                              entity_names: List[str],
                              entity_types: List[str],
                              entity_ids: List[str]) -> float:
        """
        Calculate how well an element matches the entities in the query.
        
        Args:
            element: Knowledge element
            entity_names: List of entity names from the query
            entity_types: List of entity types from the query
            entity_ids: List of entity IDs from the query
            
        Returns:
            Entity match score (0.0-1.0)
        """
        element_entities = element.get("entities", [])
        element_keywords = [k.lower() for k in element.get("keywords", [])]
        element_domain = element.get("domain", "").lower()
        element_type = element.get("type", "").lower()
        
        # Direct entity ID matches
        direct_matches = sum(1 for entity_id in entity_ids 
                           if any(e.get("id") == entity_id for e in element_entities))
        
        # Name and type matches
        name_matches = sum(1 for name in entity_names 
                         if name in element_keywords or name in element_domain)
        
        type_matches = sum(1 for type_name in entity_types 
                         if type_name == element_type or type_name in element_keywords)
        
        # Calculate match score
        total_entities = len(entity_ids)
        if total_entities == 0:
            return 0.5  # Neutral score if no entities in query
        
        # Weight direct matches more heavily
        weighted_matches = (direct_matches * 2 + name_matches + type_matches)
        max_possible = total_entities * 4  # Maximum possible weighted matches
        
        match_score = weighted_matches / max_possible if max_possible > 0 else 0.0
        return match_score
    
    def _calculate_intent_match(self, element: Dict[str, Any], 
                              query_intent: Dict[str, Any]) -> float:
        """
        Calculate how well an element matches the query intent.
        
        Args:
            element: Knowledge element
            query_intent: Intent information from the query
            
        Returns:
            Intent match score (0.0-1.0)
        """
        # Get intent attributes
        intent_type = query_intent.get("type", "informational")
        intent_focus = query_intent.get("focus", [])
        intent_action = query_intent.get("action", "")
        
        element_type = element.get("type", "")
        element_focus = element.get("focus", [])
        element_actions = element.get("actions", [])
        
        match_scores = []
        
        # Match by intent type
        if intent_type == "informational" and element_type in ["fact", "concept", "definition"]:
            match_scores.append(0.9)
        elif intent_type == "procedural" and element_type in ["procedure", "step", "instruction"]:
            match_scores.append(0.9)
        elif intent_type == "comparative" and element_type in ["comparison", "contrast", "difference"]:
            match_scores.append(0.9)
        else:
            match_scores.append(0.3)  # Default match
        
        # Match by focus
        focus_matches = 0
        for focus in intent_focus:
            if focus in element_focus:
                focus_matches += 1
        
        focus_score = focus_matches / len(intent_focus) if intent_focus else 0.5
        match_scores.append(focus_score)
        
        # Match by action
        action_score = 0.0
        if intent_action:
            if intent_action in element_actions:
                action_score = 1.0
            elif any(action.startswith(intent_action) for action in element_actions):
                action_score = 0.7
        else:
            action_score = 0.5  # Neutral if no intent action
        
        match_scores.append(action_score)
        
        # Combine scores
        intent_match = sum(match_scores) / len(match_scores)
        return intent_match
    
    def _calculate_novelty_scores(self, scored_elements: List[Dict[str, Any]], 
                                context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Calculate novelty scores based on what information is already known.
        
        Args:
            scored_elements: Elements with relevance scores
            context: Context data from the orchestrator
            
        Returns:
            Elements with novelty scores
        """
        # Extract previously delivered information from context
        previous_info = set()
        if "working_memory" in context and "previous_responses" in context["working_memory"]:
            for response in context["working_memory"]["previous_responses"]:
                if "elements" in response:
                    for element in response["elements"]:
                        if "id" in element:
                            previous_info.add(element["id"])
                        if "keywords" in element:
                            previous_info.update(element["keywords"])
        
        # Update elements with novelty scores
        for element in scored_elements:
            novelty_score = 1.0  # Default to highest novelty
            
            # Check if element ID has been delivered before
            if "id" in element and element["id"] in previous_info:
                novelty_score = 0.2  # Very low novelty if directly delivered before
            
            # Check for keyword overlap with previous information
            if "keywords" in element:
                keyword_overlap = sum(1 for kw in element["keywords"] if kw in previous_info)
                total_keywords = len(element["keywords"])
                
                if total_keywords > 0:
                    overlap_ratio = keyword_overlap / total_keywords
                    # Reduce novelty score based on overlap
                    keyword_novelty = 1.0 - (overlap_ratio * 0.8)
                    
                    # Take the lowest novelty score
                    novelty_score = min(novelty_score, keyword_novelty)
            
            # Store the novelty score
            element["novelty_score"] = novelty_score
            
            # Adjust the relevance score based on novelty
            adjusted_relevance = (
                element["relevance_score"] * (1 - self.novelty_weight) +
                novelty_score * self.novelty_weight
            )
            element["adjusted_relevance"] = adjusted_relevance
        
        return scored_elements
    
    def _align_with_user_intent(self, scored_elements: List[Dict[str, Any]],
                              query_intent: Dict[str, Any],
                              query_constraints: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Adjust element scores based on alignment with user intent and constraints.
        
        Args:
            scored_elements: Elements with relevance and novelty scores
            query_intent: Intent information from the query
            query_constraints: Constraint information from the query
            
        Returns:
            Elements with final priority scores
        """
        # Extract intent characteristics
        detail_level = query_intent.get("detail_level", "medium")
        scope = query_intent.get("scope", "standard")
        
        # Extract constraints
        max_elements = query_constraints.get("max_elements", 0)
        required_types = query_constraints.get("required_types", [])
        excluded_types = query_constraints.get("excluded_types", [])
        
        for element in scored_elements:
            intent_alignment = 0.5  # Default neutral alignment
            
            # Align with detail level
            element_specificity = element.get("specificity", "medium")
            if detail_level == element_specificity:
                intent_alignment += 0.2
            elif (detail_level == "high" and element_specificity == "low") or \
                 (detail_level == "low" and element_specificity == "high"):
                intent_alignment -= 0.2
            
            # Align with scope
            element_type = element.get("type", "")
            is_foundational = element.get("is_foundational", False)
            
            if scope == "comprehensive" and is_foundational:
                intent_alignment += 0.15
            elif scope == "focused" and not is_foundational:
                intent_alignment += 0.15
            
            # Check required and excluded types
            if element_type in required_types:
                intent_alignment += 0.25
            if element_type in excluded_types:
                intent_alignment -= 0.5
            
            # Clamp alignment value
            intent_alignment = max(0.0, min(1.0, intent_alignment))
            
            # Combine scores for final priority
            element["intent_alignment"] = intent_alignment
            element["final_priority"] = (
                element["adjusted_relevance"] * (1 - self.intent_alignment_weight) +
                intent_alignment * self.intent_alignment_weight
            )
        
        return scored_elements
    
    def _prioritize_elements(self, scored_elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Prioritize elements based on final scores and assign prominence labels.
        
        Args:
            scored_elements: Elements with final priority scores
            
        Returns:
            Prioritized elements with prominence labels
        """
        # Sort elements by final priority score
        sorted_elements = sorted(
            scored_elements, 
            key=lambda x: x.get("final_priority", 0), 
            reverse=True
        )
        
        # Determine thresholds for high/medium/low prominence
        if sorted_elements:
            # Dynamic thresholds based on the score distribution
            scores = [element.get("final_priority", 0) for element in sorted_elements]
            max_score = max(scores)
            min_score = min(scores)
            score_range = max_score - min_score
            
            # Adjust thresholds based on score distribution
            if score_range < 0.2:  # Tight distribution
                # Use percentile-based approach
                high_threshold = sorted(scores, reverse=True)[int(len(scores) * 0.3)]
                low_threshold = sorted(scores, reverse=True)[int(len(scores) * 0.7)]
            else:
                # Use fixed gaps
                high_threshold = max_score - (score_range * 0.3)
                low_threshold = min_score + (score_range * 0.3)
        else:
            # Fallback to default thresholds
            high_threshold = 0.7
            low_threshold = 0.4
        
        # Assign prominence labels
        for element in sorted_elements:
            priority = element.get("final_priority", 0)
            
            if priority >= high_threshold:
                element["prominence"] = "high"
            elif priority >= low_threshold:
                element["prominence"] = "medium"
            else:
                element["prominence"] = "low"
        
        return sorted_elements
    
    def _group_related_elements(self, prioritized_elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Group related elements together to maintain coherence.
        
        Args:
            prioritized_elements: Prioritized elements
            
        Returns:
            List of element groups
        """
        # Create a map of element IDs to indices
        element_map = {
            element.get("id", f"element_{i}"): i 
            for i, element in enumerate(prioritized_elements)
        }
        
        # Initialize groups
        groups = []
        processed = set()
        
        # Process elements in priority order
        for i, element in enumerate(prioritized_elements):
            element_id = element.get("id", f"element_{i}")
            
            if element_id in processed:
                continue
            
            # Start a new group with this element
            group = {
                "primary_element": element_id,
                "related_elements": [],
                "prominence": element.get("prominence", "medium"),
                "relevance_score": element.get("final_priority", 0)
            }
            
            # Find related elements
            dependencies = element.get("dependencies", [])
            for dep_id in dependencies:
                if dep_id in element_map and dep_id != element_id:
                    group["related_elements"].append(dep_id)
                    processed.add(dep_id)
            
            # Check for mutual information relationships
            mutual_info = element.get("mutual_information", {})
            for related_id, info_value in mutual_info.items():
                if (related_id in element_map and 
                    related_id != element_id and 
                    info_value > 0.5):  # Only include strong relationships
                    
                    if related_id not in group["related_elements"]:
                        group["related_elements"].append(related_id)
                        processed.add(related_id)
            
            # Only add groups with related elements
            if group["related_elements"] or element.get("prominence") == "high":
                groups.append(group)
            
            processed.add(element_id)
        
        # Sort groups by the prominence and relevance of their primary elements
        groups.sort(key=lambda g: (
            {"high": 3, "medium": 2, "low": 1}.get(g["prominence"], 0),
            g["relevance_score"]
        ), reverse=True)
        
        return groups 