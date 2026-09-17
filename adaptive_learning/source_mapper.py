from typing import Dict, List, Optional, Any
from .mock_data import MOCK_CONCEPTS, MOCK_SOURCE_MAPPING

class SourceMapper:
    """
    Module Source Mapper: Ánh xạ 2 chiều giữa Bài giảng (Slide / Video Timestamp) và Knowledge Graph (Concepts).
    """
    def __init__(self, source_mapping: Optional[Dict[str, Dict[str, Any]]] = None, concepts: Optional[Dict[str, Any]] = None):
        self.source_mapping = source_mapping if source_mapping is not None else MOCK_SOURCE_MAPPING
        self.concepts = concepts if concepts is not None else MOCK_CONCEPTS

    def get_concepts_by_slide(self, slide_num: int) -> List[Dict[str, Any]]:
        """
        Trả về danh sách các Concept tương ứng với trang Slide hiện tại.
        """
        matched = []
        for concept_id, mapping in self.source_mapping.items():
            if mapping.get("slide") == slide_num:
                concept_info = self.concepts.get(concept_id, {})
                matched.append({
                    "concept_id": concept_id,
                    "name": concept_info.get("name", "Unknown"),
                    "slide": slide_num,
                    "start_time": mapping.get("start_time"),
                    "end_time": mapping.get("end_time")
                })
        return matched

    def get_concept_by_time(self, timestamp_seconds: float) -> Optional[Dict[str, Any]]:
        """
        Trả về Concept tương ứng với giây thứ N trong Video.
        """
        for concept_id, mapping in self.source_mapping.items():
            start = mapping.get("start_time")
            end = mapping.get("end_time")
            if start is not None and end is not None and start <= timestamp_seconds <= end:
                concept_info = self.concepts.get(concept_id, {})
                return {
                    "concept_id": concept_id,
                    "name": concept_info.get("name", "Unknown"),
                    "slide": mapping.get("slide"),
                    "start_time": start,
                    "end_time": end
                }
        return None

    def get_source_by_concept(self, concept_id: str) -> Dict[str, Any]:
        """
        Trả về mốc Slide & Timestamp của một Concept.
        """
        return self.source_mapping.get(concept_id, {})
