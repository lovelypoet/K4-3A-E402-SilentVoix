from pathlib import Path

import pytest

from adaptive_learning import ingestion
from adaptive_learning.ingestion import DocumentIngestor


def test_stamp_chunks_preserves_document_and_source_identity():
    chunks = DocumentIngestor.process_raw_text("A meaningful lesson paragraph.", lesson_id="lesson_x")
    DocumentIngestor.stamp_chunks(
        chunks,
        document_id="doc_x",
        source_key="file:abc",
        source_group="file:abc",
        source_type="document",
    )
    assert chunks[0].document_id == "doc_x"
    assert chunks[0].lesson_id == "lesson_x"
    assert chunks[0].source_key == "file:abc"
    assert chunks[0].source_group == "file:abc"


def test_pdf_pages_are_preserved(tmp_path: Path):
    pypdf = pytest.importorskip("pypdf")
    path = tmp_path / "lesson.pdf"
    writer = pypdf.PdfWriter()
    page = writer.add_blank_page(width=200, height=200)
    # A blank page is intentionally classified as OCR_REQUIRED.
    with path.open("wb") as handle:
        writer.write(handle)
    with pytest.raises(ValueError, match="OCR_REQUIRED"):
        DocumentIngestor.ingest_pdf_file(str(path), lesson_id="lesson_pdf")


def test_local_video_transcription_preserves_timestamps(monkeypatch, tmp_path: Path):
    class Segment:
        def __init__(self, start, end, text):
            self.start, self.end, self.text = start, end, text

    class FakeModel:
        def __init__(self, *args, **kwargs):
            pass

        def transcribe(self, path, vad_filter=True):
            return iter([Segment(12.4, 28.7, "Neural networks learn representations.")]), None

    monkeypatch.setattr(ingestion, "WhisperModel", FakeModel)
    video = tmp_path / "lesson.mp4"
    video.write_bytes(b"test")
    chunks = DocumentIngestor.ingest_local_video_file(
        str(video),
        lesson_id="lesson_video",
        document_id="doc_video",
        source_key="file:test",
    )
    assert len(chunks) == 1
    assert chunks[0].document_id == "doc_video"
    assert chunks[0].start_time == 12.4
    assert chunks[0].end_time == 28.7
    assert chunks[0].source_type == "video"
