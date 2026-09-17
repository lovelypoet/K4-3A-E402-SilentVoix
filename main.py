from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from adaptive_learning.api import adaptive_router

app = FastAPI(
    title="Lesson Studio — Adaptive Learning & Knowledge Mapping API",
    description="Backend API cung cấp Đồ thị tri thức, Source Mapping và Học thích ứng.",
    version="1.0.0"
)

# Cấu hình CORS để Frontend (index.html) gọi API không bị vướng origin policy
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Tích hợp Router
app.include_router(adaptive_router)

@app.get("/")
def root():
    return {
        "status": "online",
        "message": "Lesson Studio API Server đang hoạt động!",
        "docs_url": "http://127.0.0.1:8000/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
