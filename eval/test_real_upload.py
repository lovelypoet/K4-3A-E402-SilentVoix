import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def _make_minimal_pdf(path: str) -> bool:
    try:
        from pypdf import PdfWriter
        writer = PdfWriter()
        writer.add_blank_page(width=200, height=200)
        with open(path, "wb") as f:
            writer.write(f)
        return True
    except Exception as e:
        print(f"[SKIP PDF create] {e}")
        return False


def test_three_post_apis_only():
    print("\n=== ONLY 3 POST INGEST APIS ===")

    # Removed aliases must not work
    res = client.post("/adaptive/lessons/link", json={"video_url": "https://www.youtube.com/watch?v=aircAruvnKk"})
    assert res.status_code in (404, 405)
    res = client.post("/adaptive/documents/upload", files={"upload": ("a.pdf", b"%PDF", "application/pdf")})
    assert res.status_code in (404, 405)
    print("[PASS] old aliases removed")

    # 1) video
    res = client.post("/adaptive/lessons/video", json={
        "video_url": "https://www.youtube.com/watch?v=PTXkJbkGtUw",
    })
    assert res.status_code == 200, res.text
    assert res.json()["source_type"] == "video"
    print("[PASS] POST /adaptive/lessons/video")

    # 2) slide
    res = client.post("/adaptive/lessons/slide", json={
        "slide_url": "https://fr.scribd.com/presentation/872620942/demo",
    })
    assert res.status_code == 200, res.text
    assert res.json()["source_type"] == "slide"
    print("[PASS] POST /adaptive/lessons/slide")

    # 3) document — body chỉ có file
    with tempfile.TemporaryDirectory() as tmp:
        pdf_path = os.path.join(tmp, "doc.pdf")
        if _make_minimal_pdf(pdf_path):
            with open(pdf_path, "rb") as f:
                res = client.post(
                    "/adaptive/upload",
                    files={"file": ("doc.pdf", f, "application/pdf")},
                )
            assert res.status_code == 200, res.text
            assert res.json()["source_type"] == "document"
            print("[PASS] POST /adaptive/upload")

    print("=== ALL PASS ===")


if __name__ == "__main__":
    test_three_post_apis_only()
