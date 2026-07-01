"""AI 志愿顾问聊天 API"""
from fastapi import APIRouter
from pydantic import BaseModel
from openai import OpenAI

router = APIRouter()


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    apiKey: str
    model: str
    baseUrl: str
    context: dict = {}


SYSTEM_PROMPT = """你是一位专业的高考志愿填报顾问。你的职责是：

1. **分析考生情况**：根据分数、位次、省份、选科等信息，给出专业的志愿填报建议
2. **冲稳保推荐**：按照"冲一冲、稳一稳、保一保"的原则，给出合理的院校和专业推荐
3. **数据解读**：结合历年录取数据、分数线趋势、招生计划等，给出有数据支撑的建议
4. **个性化建议**：考虑考生的专业兴趣、地域偏好、职业规划等因素

你的回答风格：
- 直爽、接地气，像朋友聊天一样
- 用数据说话，但不要堆砌数字
- 给出明确的建议，不要模棱两可
- 注意提醒风险，比如"这个分数报这个学校有一定风险"

如果用户提供了志愿推荐结果，你可以基于这些结果给出更具体的分析和建议。
如果数据库中没有某所学校的数据，如实告知，不要编造。"""


@router.post("/ai/chat")
def chat(request: ChatRequest):
    try:
        client = OpenAI(base_url=request.baseUrl, api_key=request.apiKey)

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        if request.context:
            ctx_parts = []
            if "score" in request.context:
                ctx_parts.append(f"分数: {request.context['score']}")
            if "province" in request.context:
                ctx_parts.append(f"省份: {request.context['province']}")
            if "subject" in request.context:
                ctx_parts.append(f"科类: {request.context['subject']}")
            if "rank" in request.context:
                ctx_parts.append(f"位次: {request.context['rank']}")
            if "recommendations" in request.context:
                recs = request.context["recommendations"]
                ctx_parts.append(f"推荐结果: {len(recs)}所学校")
                for r in recs[:10]:
                    ctx_parts.append(f"  - {r.get('name', '')} ({r.get('tier', '')}) 分数线{r.get('latest_score', '未知')}")

            if ctx_parts:
                messages.append({
                    "role": "system",
                    "content": f"【当前考生信息】\n" + "\n".join(ctx_parts)
                })

        for m in request.messages:
            messages.append({"role": m.role, "content": m.content})

        resp = client.chat.completions.create(
            model=request.model,
            messages=messages,
            temperature=0.7,
        )

        return {"ok": True, "reply": resp.choices[0].message.content}
    except Exception as e:
        return {"ok": False, "error": str(e)[:300]}
