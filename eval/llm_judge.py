import json

PROMPT_GROUNDEDNESS = """
Bạn là giám khảo đánh giá chất lượng tài liệu học tập.
Nhiệm vụ: Kiểm tra xem CÂU HỎI QUIZ và ĐÁP ÁN có thực sự được suy ra từ TÀI LIỆU (Document) hay không (Groundedness).
Nếu Quiz chứa thông tin ngoài tài liệu hoặc sai lệch so với tài liệu, hãy đánh Fail.

Yêu cầu đầu ra: JSON {"pass": bool, "reason": "Lý do chi tiết"}
"""

PROMPT_CITATION = """
Bạn là giám khảo đánh giá nguồn trích dẫn.
Nhiệm vụ: Kiểm tra xem NGUỒN TRÍCH DẪN (Slide X, Video Y) có thực sự chứa nội dung liên quan đến Concept được học hay không.

Yêu cầu đầu ra: JSON {"pass": bool, "reason": "Lý do chi tiết"}
"""

PROMPT_QUIZ_QUALITY = """
Bạn là giám khảo đánh giá chất lượng sư phạm.
Nhiệm vụ: Kiểm tra xem CÂU HỎI QUIZ có rõ ràng không, và các phương án sai (distractors) có hợp lý, không đánh đố quá mức hay không.

Yêu cầu đầu ra: JSON {"pass": bool, "reason": "Lý do chi tiết"}
"""
import os
from pydantic import BaseModel

try:
    from dotenv import load_dotenv
    load_dotenv()  # Nạp biến môi trường từ file .env nếu có
except ImportError:
    pass

try:
    from google import genai
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        client = genai.Client(api_key=api_key)
    else:
        client = None
except ImportError:
    client = None

class JudgeResult(BaseModel):
    pass_status: bool
    reason: str

def evaluate_with_llm_mock(prompt: str, input_data: dict, expected_pass: bool = True) -> dict:
    """
    Gọi Gemini API để làm giám khảo.
    Nếu chưa set GEMINI_API_KEY hoặc chưa cài thư viện google-genai, sẽ fallback về mock.
    """
    if not client:
        # Fallback về mock để script không bị crash
        if expected_pass:
            return {"pass": True, "reason": "[MOCK] Đạt chất lượng tốt theo rubric."}
        else:
            return {"pass": False, "reason": "[MOCK] Không đạt chất lượng theo rubric."}

    full_prompt = f"{prompt}\n\nDữ liệu cần chấm:\n{json.dumps(input_data, ensure_ascii=False)}"
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=full_prompt,
            config={
                'response_mime_type': 'application/json',
                'response_schema': JudgeResult,
                'temperature': 0.0,
            },
        )
        result = json.loads(response.text)
        return {"pass": result.get("pass_status", False), "reason": result.get("reason", "No reason provided")}
    except Exception as e:
        return {"pass": False, "reason": f"Lỗi khi gọi Gemini: {str(e)}"}
