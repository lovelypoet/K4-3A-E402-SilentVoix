from typing import List, Dict, Optional

def compute_mastery(attempts: List[Dict]) -> Optional[float]:
    """
    attempts: list of {"is_correct": bool, "difficulty": float}
    Returns weighted mastery in [0.0, 1.0], or None if no attempts exist.
    """
    if not attempts:
        return None
    total_weight = sum(a.get("difficulty", 1.0) for a in attempts)
    if total_weight == 0:
        return None
    correct_weight = sum(a.get("difficulty", 1.0) for a in attempts if a.get("is_correct", False))
    return correct_weight / total_weight

def compute_mastery_state(
    mastery: Optional[float],
    is_current: bool,
    weak_threshold: float = 0.5,
    mastered_threshold: float = 0.85,
) -> str:
    """
    Returns one of: "current", "not_learned", "weak", "learning", "mastered".
    `is_current` (the concept matching the active slide/timestamp) always wins,
    regardless of the underlying mastery score.
    """
    if is_current:
        return "current"
    if mastery is None:
        return "not_learned"
    if mastery < weak_threshold:
        return "weak"
    if mastery < mastered_threshold:
        return "learning"
    return "mastered"
