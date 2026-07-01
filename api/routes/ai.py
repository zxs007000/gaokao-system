"""AI 配置 API"""
from fastapi import APIRouter
from pydantic import BaseModel
from openai import OpenAI

router = APIRouter()


class AIConfig(BaseModel):
    apiKey: str
    model: str
    baseUrl: str


@router.post("/ai/test")
def test_ai_connection(config: AIConfig):
    try:
        client = OpenAI(base_url=config.baseUrl, api_key=config.apiKey)
        resp = client.chat.completions.create(
            model=config.model,
            messages=[{"role": "user", "content": "hi"}],
            max_tokens=5,
        )
        return {"ok": True, "message": f"连接成功！模型回复：{resp.choices[0].message.content}"}
    except Exception as e:
        return {"ok": False, "message": str(e)[:200]}
