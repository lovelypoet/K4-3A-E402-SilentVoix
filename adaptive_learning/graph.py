from typing import Dict, List, Optional

def find_weak_prerequisite(
    edges: Dict[str, List[str]], 
    mastery_scores: Dict[str, Optional[float]], 
    start_concept_id: str,
    weak_threshold: float = 0.5,
    mastered_threshold: float = 0.85
) -> Optional[str]:
    """
    Walks backward along `prerequisite` edges from `start_concept_id` to find the first
    concept whose mastery is below `weak_threshold`.
    
    edges: Mapping of concept_id -> list of prerequisite concept_ids (backward edges)
    mastery_scores: Mapping of concept_id -> mastery score (or None if not learned)
    Returns: The concept_id of the recommended weak prerequisite, or None if the start concept is not weak.
    """
    start_mastery = mastery_scores.get(start_concept_id)
    if start_mastery is not None and start_mastery >= weak_threshold:
        return None
        
    visited = set()
    queue = []
    
    # We want to find an ancestor, so we enqueue immediate prerequisites first
    if start_concept_id in edges:
        # Tie-break deterministic order: sort the prerequisites alphabetically
        queue.extend(sorted(edges[start_concept_id]))
        
    while queue:
        current_node = queue.pop(0)
        
        if current_node in visited:
            continue
        visited.add(current_node)
        
        node_mastery = mastery_scores.get(current_node)
        
        # Filter out already-mastered candidate
        if node_mastery is not None and node_mastery >= mastered_threshold:
            # Continue traversal in case its prerequisites are somehow weak? 
            # Usually if it's mastered, we wouldn't need to review its prerequisites. 
            # But we'll just skip recommending this node and continue.
            pass
        elif node_mastery is None or node_mastery < weak_threshold:
            # Found a weak or unlearned prerequisite!
            return current_node
            
        # Add its prerequisites to the queue (deterministic order)
        if current_node in edges:
            # Append to the end of the queue for BFS
            for prereq in sorted(edges[current_node]):
                if prereq not in visited:
                    queue.append(prereq)
            
    # If no weak prerequisite found (either leaf node or all mastered)
    # The plan says: "No prerequisite (leaf node): return 'no prerequisite — review this concept directly'"
    return start_concept_id
