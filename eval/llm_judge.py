import json

PROMPT_GROUNDEDNESS = """
Bạn là giám khảo đánh giá chất lượng tài liệu học tập.
Nhiệm vụ: Kiểm tra xem CÂU HỎI QUIZ và ĐÁP ÁN có thực sự được suy ra từ TÀI LIỆU (Document) hay không (Groundedness).
Nếu Quiz chứa thông tin ngoài tài liệu hoặc sai lệch so với tài liệu, hãy đánh Fail.

Yêu cầu đầu ra: JSON {"pass_status": bool, "reason": "Lý do chi tiết"}
"""

PROMPT_CITATION = """
Bạn là giám khảo đánh giá nguồn trích dẫn.
Nhiệm vụ: Kiểm tra xem NGUỒN TRÍCH DẪN (Slide X, Video Y) có thực sự chứa nội dung liên quan đến Concept được học hay không.

Yêu cầu đầu ra: JSON {"pass_status": bool, "reason": "Lý do chi tiết"}
"""

PROMPT_QUIZ_QUALITY = """
Bạn là giám khảo đánh giá chất lượng sư phạm.
Nhiệm vụ: Kiểm tra xem CÂU HỎI QUIZ có rõ ràng không, và các phương án sai (distractors) có hợp lý, không đánh đố quá mức hay không.

Yêu cầu đầu ra: JSON {"pass_status": bool, "reason": "Lý do chi tiết"}
"""
import os
from pydantic import BaseModel

try:
    from dotenv import load_dotenv
    load_dotenv()  # Nạp biến môi trường từ file .env nếu có
except ImportError:
    pass

try:
    from openai import OpenAI
    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        client = OpenAI(api_key=api_key)
    else:
        client = None
except ImportError:
    client = None

class JudgeResult(BaseModel):
    pass_status: bool
    reason: str

def evaluate_with_llm_mock(prompt: str, input_data: dict, expected_pass: bool = True) -> dict:
    """
    Gọi OpenAI API để làm giám khảo.
    Nếu chưa set OPENAI_API_KEY hoặc chưa cài thư viện openai, sẽ fallback về mock.
    """
    if not client:
        # Fallback về mock để script không bị crash
        if expected_pass:
            return {"pass": True, "reason": "[MOCK] Đạt chất lượng tốt theo rubric."}
        else:
            return {"pass": False, "reason": "[MOCK] Không đạt chất lượng theo rubric."}

    full_prompt = f"{prompt}\n\nDữ liệu cần chấm:\n{json.dumps(input_data, ensure_ascii=False)}"
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Bạn là giám khảo đánh giá chất lượng hệ thống AI. Đầu ra của bạn BẮT BUỘC là định dạng JSON duy nhất."},
                {"role": "user", "content": full_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.0
        )
        result = json.loads(response.choices[0].message.content)
        return {"pass": result.get("pass_status", False), "reason": result.get("reason", "No reason provided")}
    except Exception as e:
        return {"pass": False, "reason": f"Lỗi khi gọi OpenAI: {str(e)}"}
