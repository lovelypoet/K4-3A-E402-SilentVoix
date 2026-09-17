import os
import json
from typing import List, Dict, Any, Optional
from .models import Document, Chunk

class DocumentIngestor:
    """
    Handles ingestion of PDF, PPTX, and Transcript files,
    extracting text chunks while strictly preserving Slide numbers and Timestamps.
    """
    
    @staticmethod
    def ingest_transcript_json(transcript_data: List[Dict[str, Any]], lesson_id: str = "lesson_01") -> List[Chunk]:
        """
        Ingests a transcript list with start_time, end_time, and text.
        """
        chunks = []
        for i, item in enumerate(transcript_data):
            text = item.get("text", "").strip()
            if not text:
                continue
            chunk = Chunk(
                chunk_id=f"chunk_tr_{i+1:03d}",
                lesson_id=lesson_id,
                text=text,
                start_time=float(item.get("start_time", 0)),
                end_time=float(item.get("end_time", 0))
            )
            chunks.append(chunk)
        return chunks

    @staticmethod
    def ingest_slides_data(slides_data: List[Dict[str, Any]], lesson_id: str = "lesson_01") -> List[Chunk]:
        """
        Ingests slide objects containing slide number and slide text content.
        """
        chunks = []
        for item in slides_data:
            slide_num = item.get("slide")
            text = item.get("text", "").strip()
            if not text or slide_num is None:
                continue
            chunk = Chunk(
                chunk_id=f"chunk_slide_{slide_num:03d}",
                lesson_id=lesson_id,
                text=text,
                slide=int(slide_num)
            )
            chunks.append(chunk)
        return chunks

    @staticmethod
    def process_raw_text(text: str, lesson_id: str = "lesson_01", default_slide: int = 1) -> List[Chunk]:
        """
        Fallback chunker for plain text.
        """
        if not text or not text.strip():
            return []
        
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        chunks = []
        for idx, p in enumerate(paragraphs):
            chunks.append(Chunk(
                chunk_id=f"chunk_txt_{idx+1:03d}",
                lesson_id=lesson_id,
                text=p,
                slide=default_slide
            ))
        return chunks
