"""FastAPI 入口"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import recommend, trends, compare, stats, universities, ai, analysis, ai_chat, personality, crawler_admin

app = FastAPI(title="高考数据分析 API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(recommend.router, prefix="/api")
app.include_router(trends.router, prefix="/api")
app.include_router(compare.router, prefix="/api")
app.include_router(stats.router, prefix="/api")
app.include_router(universities.router, prefix="/api")
app.include_router(ai.router, prefix="/api")
app.include_router(analysis.router, prefix="/api")
app.include_router(ai_chat.router, prefix="/api")
app.include_router(personality.router, prefix="/api")
app.include_router(crawler_admin.router, prefix="/api")


@app.get("/api/health")
def health():
    return {"status": "ok"}
