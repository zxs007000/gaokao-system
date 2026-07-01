"""学生性格测试 API — 多维度性格与职业测评"""
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

# ─── 九型人格 (Enneagram) ───
ENNEAGRAM_QUESTIONS = [
    {"id": "e1", "test": "enneagram", "dim": 1, "text": "我经常觉得自己应该做到最好，即使别人觉得已经足够好了。"},
    {"id": "e2", "test": "enneagram", "dim": 1, "text": "当事情出错时，我会感到特别不安，觉得本可以避免。"},
    {"id": "e3", "test": "enneagram", "dim": 2, "text": "我经常主动帮助别人，即使他们没有请求帮助。"},
    {"id": "e4", "test": "enneagram", "dim": 2, "text": "我很难拒绝别人的请求，即使这会给我带来不便。"},
    {"id": "e5", "test": "enneagram", "dim": 3, "text": "我非常注重效率和成果，喜欢用结果来衡量自己的价值。"},
    {"id": "e6", "test": "enneagram", "dim": 3, "text": "我经常同时处理多个项目，并且都力求做到最好。"},
    {"id": "e7", "test": "enneagram", "dim": 4, "text": "我经常觉得自己与别人不同，有着独特的内心世界。"},
    {"id": "e8", "test": "enneagram", "dim": 4, "text": "我容易被艺术、音乐或自然美景深深打动。"},
    {"id": "e9", "test": "enneagram", "dim": 5, "text": "我喜欢独自思考问题，享受独处的时光。"},
    {"id": "e10", "test": "enneagram", "dim": 5, "text": "我习惯先观察和分析，再采取行动。"},
    {"id": "e11", "test": "enneagram", "dim": 6, "text": "我经常担心可能出现的问题，喜欢提前做好准备。"},
    {"id": "e12", "test": "enneagram", "dim": 6, "text": "我对权威和规则有复杂的感受，既想遵守又想质疑。"},
    {"id": "e13", "test": "enneagram", "dim": 7, "text": "我喜欢尝试新事物，讨厌一成不变的生活。"},
    {"id": "e14", "test": "enneagram", "dim": 7, "text": "我经常同时有很多想法和计划，精力充沛。"},
    {"id": "e15", "test": "enneagram", "dim": 8, "text": "我喜欢掌控局面，在团队中自然地承担领导角色。"},
    {"id": "e16", "test": "enneagram", "dim": 8, "text": "我不害怕冲突，愿意为自己的立场据理力争。"},
    {"id": "e17", "test": "enneagram", "dim": 9, "text": "我追求和谐，尽量避免与人发生冲突。"},
    {"id": "e18", "test": "enneagram", "dim": 9, "text": "我容易适应不同的环境和人，很少有强烈的偏好。"},
]

ENNEAGRAM_NAMES = {
    1: "完美主义者", 2: "助人者", 3: "成就者", 4: "个人主义者",
    5: "观察者", 6: "忠诚者", 7: "享乐主义者", 8: "挑战者", 9: "和平者",
}
ENNEAGRAM_DESCS = {
    1: "追求完美和正确，有强烈的是非观念，做事认真负责，但可能过于苛求自己和他人。",
    2: "热心助人，善于感知他人需求，重视人际关系，但可能忽略自己的需要。",
    3: "目标导向，注重效率和形象，善于适应环境，但可能过度关注外在成就。",
    4: "追求独特性和深度，富有创造力和感受力，但可能容易陷入情绪波动。",
    5: "善于观察和分析，独立思考，知识渊博，但可能过于内向和疏离。",
    6: "忠诚可靠，善于发现问题和风险，团队意识强，但可能过于焦虑和犹豫。",
    7: "乐观开朗，兴趣广泛，追求新鲜体验，但可能难以专注和坚持。",
    8: "自信果断，敢于挑战，有领导力，但可能过于强势和控制欲强。",
    9: "平和友善，善于调和矛盾，适应力强，但可能回避冲突和缺乏主见。",
}

# ─── MBTI 16型人格 ───
MBTI_QUESTIONS = [
    # E/I 维度 (外向/内向)
    {"id": "m1", "test": "mbti", "dim": "E_I", "text": "在社交场合中，我感到精力充沛、兴奋。"},
    {"id": "m2", "test": "mbti", "dim": "E_I", "text": "我喜欢成为众人关注的焦点。"},
    {"id": "m3", "test": "mbti", "dim": "E_I", "text": "我经常主动与陌生人搭话。"},
    {"id": "m4", "test": "mbti", "dim": "E_I", "text": "我喜欢团队合作而不是独自工作。"},
    # S/N 维度 (感觉/直觉)
    {"id": "m5", "test": "mbti", "dim": "S_N", "text": "我更关注具体的事实和细节，而不是抽象的概念。"},
    {"id": "m6", "test": "mbti", "dim": "S_N", "text": "我喜欢按照已经验证过的方法做事。"},
    {"id": "m7", "test": "mbti", "dim": "S_N", "text": "我更相信亲眼看到的东西，而不是理论推导。"},
    {"id": "m8", "test": "mbti", "dim": "S_N", "text": "我擅长发现事物之间的联系和模式。"},
    # T/F 维度 (思考/情感)
    {"id": "m9", "test": "mbti", "dim": "T_F", "text": "做决定时，我更依赖逻辑分析而非个人感受。"},
    {"id": "m10", "test": "mbti", "dim": "T_F", "text": "我认为公正比仁慈更重要。"},
    {"id": "m11", "test": "mbti", "dim": "T_F", "text": "别人难过时，我倾向于分析原因而不是直接安慰。"},
    {"id": "m12", "test": "mbti", "dim": "T_F", "text": "我做决定时会考虑对他人的影响。"},
    # J/P 维度 (判断/知觉)
    {"id": "m13", "test": "mbti", "dim": "J_P", "text": "我喜欢提前做好计划，不喜欢临时变动。"},
    {"id": "m14", "test": "mbti", "dim": "J_P", "text": "我的物品通常摆放整齐有序。"},
    {"id": "m15", "test": "mbti", "dim": "J_P", "text": "我喜欢尽快完成任务，而不是拖到最后。"},
    {"id": "m16", "test": "mbti", "dim": "J_P", "text": "我更喜欢灵活应变，保持多种选择。"},
]

MBTI_TYPES = {
    "INTJ": "建筑师", "INTP": "逻辑学家", "ENTJ": "指挥官", "ENTP": "辩论家",
    "INFJ": "提倡者", "INFP": "调停者", "ENFJ": "主人公", "ENFP": "竞选者",
    "ISTJ": "物流师", "ISFJ": "守卫者", "ESTJ": "总经理", "ESFJ": "执政官",
    "ISTP": "鉴赏家", "ISFP": "探险家", "ESTP": "企业家", "ESFP": "表演者",
}

MBTI_DESCS = {
    "INTJ": "富有想象力和战略性的思想家，一切皆在计划之中。",
    "INTP": "具有创造力的发明家，对知识有永不满足的渴望。",
    "ENTJ": "大胆、富有想象力且意志坚强的领导者，总能找到或创造办法。",
    "ENTP": "聪明好奇的思想家，不会放过任何一个智力挑战。",
    "INFJ": "安静而神秘，同时鼓舞人心且不知疲倦的理想主义者。",
    "INFP": "诗意、善良的利他主义者，总是热心为正义事业提供帮助。",
    "ENFJ": "富有魅力且鼓舞人心的领导者，拥有让听众着迷的天赋。",
    "ENFP": "热情、有创造力、社交能力强的自由人，总能找到微笑的理由。",
    "ISTJ": "实际且注重事实的个人，其可靠性不容怀疑。",
    "ISFJ": "非常专注且温暖的守护者，总是准备好保护所爱的人。",
    "ESTJ": "出色的管理者，在管理人和事方面有天赋。",
    "ESFJ": "极有同情心的社交高手，总在帮助别人，是群体的粘合剂。",
    "ISTP": "大胆而实际的实验家，擅长使用各种形式的工具。",
    "ISFP": "灵活而有魅力的艺术家，时刻准备着探索和体验新事物。",
    "ESTP": "聪明、精力充沛且非常善于感知的人，真正享受活在边缘。",
    "ESFP": "自发的、精力充沛的、热情的娱乐者——生活永远不会无聊。",
}

# ─── 霍兰德职业兴趣 (RIASEC) ───
HOLLAND_QUESTIONS = [
    # R 现实型 (Realistic)
    {"id": "h1", "test": "holland", "dim": "R", "text": "我喜欢修理电器、机器或交通工具。"},
    {"id": "h2", "test": "holland", "dim": "R", "text": "我喜欢在户外工作，接触大自然。"},
    {"id": "h3", "test": "holland", "dim": "R", "text": "我擅长使用工具、操作机械。"},
    # I 研究型 (Investigative)
    {"id": "h4", "test": "holland", "dim": "I", "text": "我喜欢研究科学问题和理论。"},
    {"id": "h5", "test": "holland", "dim": "I", "text": "我喜欢分析复杂的数据和信息。"},
    {"id": "h6", "test": "holland", "dim": "I", "text": "我对新发现和新知识充满好奇。"},
    # A 艺术型 (Artistic)
    {"id": "h7", "test": "holland", "dim": "A", "text": "我喜欢创作艺术作品（绘画、音乐、写作等）。"},
    {"id": "h8", "test": "holland", "dim": "A", "text": "我追求独特的自我表达方式。"},
    {"id": "h9", "test": "holland", "dim": "A", "text": "我容易被美和创意所打动。"},
    # S 社会型 (Social)
    {"id": "h10", "test": "holland", "dim": "S", "text": "我喜欢帮助别人解决问题和困难。"},
    {"id": "h11", "test": "holland", "dim": "S", "text": "我善于倾听和理解他人的感受。"},
    {"id": "h12", "test": "holland", "dim": "S", "text": "我享受教学和分享知识的过程。"},
    # E 企业型 (Enterprising)
    {"id": "h13", "test": "holland", "dim": "E", "text": "我喜欢带领团队完成目标。"},
    {"id": "h14", "test": "holland", "dim": "E", "text": "我善于说服和影响他人。"},
    {"id": "h15", "test": "holland", "dim": "E", "text": "我追求权力、地位和经济成就。"},
    # C 常规型 (Conventional)
    {"id": "h16", "test": "holland", "dim": "C", "text": "我喜欢有条理地处理数据和信息。"},
    {"id": "h17", "test": "holland", "dim": "C", "text": "我擅长按照规则和流程办事。"},
    {"id": "h18", "test": "holland", "dim": "C", "text": "我喜欢整洁有序的工作环境。"},
]

HOLLAND_NAMES = {
    "R": "现实型", "I": "研究型", "A": "艺术型",
    "S": "社会型", "E": "企业型", "C": "常规型",
}
HOLLAND_DESCS = {
    "R": "喜欢与物体、机器、工具、动植物打交道，注重实际操作，擅长动手。",
    "I": "喜欢观察、研究、分析和解决问题，追求知识和真理。",
    "A": "喜欢创造性活动，追求自我表达，富有想象力和创造力。",
    "S": "喜欢与人交往，善于理解和服务他人，重视合作和关系。",
    "E": "喜欢影响和领导他人，追求权力和成就，善于社交和说服。",
    "C": "喜欢有组织、有条理的工作，注重细节和准确性，擅长数据处理。",
}
HOLLAND_CAREERS = {
    "R": ["工程师", "技术员", "建筑师", "农林师", "运动训练师"],
    "I": ["科研人员", "医生", "程序员", "数据分析师", "天文学家"],
    "A": ["设计师", "作家", "音乐家", "摄影师", "导演"],
    "S": ["教师", "心理咨询师", "社会工作者", "护士", "人力资源"],
    "E": ["企业管理", "市场营销", "律师", "政治家", "销售总监"],
    "C": ["会计师", "审计师", "金融分析师", "档案管理", "行政管理"],
}

# ─── DISC 性格测试 ───
DISC_QUESTIONS = [
    # D 支配型 (Dominance)
    {"id": "d1", "test": "disc", "dim": "D", "text": "我直接、果断，喜欢快速做出决定。"},
    {"id": "d2", "test": "disc", "dim": "D", "text": "我喜欢接受挑战，追求竞争优势。"},
    {"id": "d3", "test": "disc", "dim": "D", "text": "我愿意承担风险，敢于面对冲突。"},
    {"id": "d4", "test": "disc", "dim": "D", "text": "我喜欢掌控局面，担任领导角色。"},
    # I 影响型 (Influence)
    {"id": "d5", "test": "disc", "dim": "I", "text": "我热情开朗，善于社交和沟通。"},
    {"id": "d6", "test": "disc", "dim": "I", "text": "我喜欢成为团队中的活跃分子。"},
    {"id": "d7", "test": "disc", "dim": "I", "text": "我善于激励和鼓舞他人。"},
    {"id": "d8", "test": "disc", "dim": "I", "text": "我喜欢在轻松的氛围中工作。"},
    # S 稳健型 (Steadiness)
    {"id": "d9", "test": "disc", "dim": "S", "text": "我温和耐心，善于倾听。"},
    {"id": "d10", "test": "disc", "dim": "S", "text": "我重视团队和谐，不喜欢冲突。"},
    {"id": "d11", "test": "disc", "dim": "S", "text": "我喜欢稳定的工作环境和节奏。"},
    {"id": "d12", "test": "disc", "dim": "S", "text": "我做事稳重，不喜欢突然的变化。"},
    # C 谨慎型 (Conscientiousness)
    {"id": "d13", "test": "disc", "dim": "C", "text": "我注重细节，追求精确和准确。"},
    {"id": "d14", "test": "disc", "dim": "C", "text": "我喜欢按规则和标准做事。"},
    {"id": "d15", "test": "disc", "dim": "C", "text": "我做决定前会收集充分信息。"},
    {"id": "d16", "test": "disc", "dim": "C", "text": "我对自己和他人都有较高的要求。"},
]

DISC_NAMES = {"D": "支配型", "I": "影响型", "S": "稳健型", "C": "谨慎型"}
DISC_DESCS = {
    "D": "结果导向、果断直接、自信坚定，追求效率和掌控。",
    "I": "热情乐观、善于社交、富有感染力，追求认同和互动。",
    "S": "温和耐心、忠诚可靠、善于合作，追求稳定和谐。",
    "C": "严谨细致、逻辑清晰、追求完美，注重质量和标准。",
}

# ─── 大五人格 (Big Five / OCEAN) ───
BIGFIVE_QUESTIONS = [
    # O 开放性 (Openness)
    {"id": "b1", "test": "bigfive", "dim": "O", "text": "我对新想法和新体验持开放态度。"},
    {"id": "b2", "test": "bigfive", "dim": "O", "text": "我喜欢探索抽象的理论和哲学问题。"},
    {"id": "b3", "test": "bigfive", "dim": "O", "text": "我对艺术和文化有浓厚兴趣。"},
    # C 尽责性 (Conscientiousness)
    {"id": "b4", "test": "bigfive", "dim": "C", "text": "我做事有条理，按计划行事。"},
    {"id": "b5", "test": "bigfive", "dim": "C", "text": "我注重细节，追求高质量的成果。"},
    {"id": "b6", "test": "bigfive", "dim": "C", "text": "我能够很好地控制自己的冲动。"},
    # E 外向性 (Extraversion)
    {"id": "b7", "test": "bigfive", "dim": "E", "text": "我在社交场合感到自在和愉快。"},
    {"id": "b8", "test": "bigfive", "dim": "E", "text": "我精力充沛，喜欢活跃的生活。"},
    {"id": "b9", "test": "bigfive", "dim": "E", "text": "我喜欢与人交谈和互动。"},
    # A 宜人性 (Agreeableness)
    {"id": "b10", "test": "bigfive", "dim": "A", "text": "我信任他人，相信人性本善。"},
    {"id": "b11", "test": "bigfive", "dim": "A", "text": "我乐于助人，关心他人的福祉。"},
    {"id": "b12", "test": "bigfive", "dim": "A", "text": "我容易与他人产生共情。"},
    # N 神经质 (Neuroticism)
    {"id": "b13", "test": "bigfive", "dim": "N", "text": "我经常感到焦虑和担忧。"},
    {"id": "b14", "test": "bigfive", "dim": "N", "text": "我的情绪波动比较大。"},
    {"id": "b15", "test": "bigfive", "dim": "N", "text": "面对压力时，我容易感到不安。"},
]

BIGFIVE_NAMES = {
    "O": "开放性", "C": "尽责性", "E": "外向性",
    "A": "宜人性", "N": "神经质",
}
BIGFIVE_DESCS = {
    "O": "反映个体对新经验的开放程度，高分者富有想象力和创造力。",
    "C": "反映个体的自律和目标导向程度，高分者可靠且有组织。",
    "E": "反映个体社交性和活力程度，高分者外向且精力充沛。",
    "A": "反映个体的合作和信任程度，高分者善良且乐于助人。",
    "N": "反映个体情绪不稳定的程度，高分者容易焦虑和情绪波动。",
}

# ─── 职业适应性 (CAAS) ───
CAREER_QUESTIONS = [
    {"id": "c1", "test": "career", "dim": "concern", "text": "我经常思考自己未来的职业发展方向。"},
    {"id": "c2", "test": "career", "dim": "concern", "text": "我会主动关注行业动态和就业趋势。"},
    {"id": "c3", "test": "career", "dim": "control", "text": "我相信通过自己的努力可以改变职业命运。"},
    {"id": "c4", "test": "career", "dim": "control", "text": "面对职业选择，我通常能做出果断的决定。"},
    {"id": "c5", "test": "career", "dim": "curiosity", "text": "我喜欢探索不同的职业可能性。"},
    {"id": "c6", "test": "career", "dim": "curiosity", "text": "我经常尝试新的活动或学习新技能来了解自己的兴趣。"},
    {"id": "c7", "test": "career", "dim": "confidence", "text": "我对自己的职业能力有信心。"},
    {"id": "c8", "test": "career", "dim": "confidence", "text": "即使遇到困难，我也相信自己能找到解决办法。"},
]
CAREER_LABELS = {"concern": "关注", "control": "控制", "curiosity": "好奇", "confidence": "自信"}

# ─── 汇总所有题目 ───
ALL_QUESTION_SETS = {
    "enneagram": ENNEAGRAM_QUESTIONS,
    "mbti": MBTI_QUESTIONS,
    "holland": HOLLAND_QUESTIONS,
    "disc": DISC_QUESTIONS,
    "bigfive": BIGFIVE_QUESTIONS,
    "career": CAREER_QUESTIONS,
}

ALL_QUESTIONS_FLAT = []
for qs in ALL_QUESTION_SETS.values():
    ALL_QUESTIONS_FLAT.extend(qs)


class Answer(BaseModel):
    question_id: str
    score: int


class TestSubmission(BaseModel):
    test_type: str  # enneagram / mbti / holland / disc / bigfive / career / all
    answers: list[Answer]


@router.get("/personality/config")
def get_config():
    """返回所有测试的元数据"""
    return {
        "tests": {
            "enneagram": {"name": "九型人格", "icon": "🔮", "count": len(ENNEAGRAM_QUESTIONS), "desc": "探索你的核心性格类型，了解行为动机"},
            "mbti": {"name": "MBTI 16型人格", "icon": "🧬", "count": len(MBTI_QUESTIONS), "desc": "经典性格分类，发现你的思维和行为偏好"},
            "holland": {"name": "霍兰德职业兴趣", "icon": "🔧", "count": len(HOLLAND_QUESTIONS), "desc": "RIASEC六型，找到与你匹配的职业方向"},
            "disc": {"name": "DISC 性格测试", "icon": "🎯", "count": len(DISC_QUESTIONS), "desc": "职场性格分析，了解你的沟通和行为风格"},
            "bigfive": {"name": "大五人格", "icon": "📊", "count": len(BIGFIVE_QUESTIONS), "desc": "学术界最认可的人格模型，全面剖析人格特质"},
            "career": {"name": "职业适应性", "icon": "🧭", "count": len(CAREER_QUESTIONS), "desc": "评估你的职业准备程度和发展潜力"},
        },
        "total": len(ALL_QUESTIONS_FLAT),
    }


@router.get("/personality/questions/{test_type}")
def get_questions(test_type: str):
    if test_type == "all":
        return {"questions": ALL_QUESTIONS_FLAT, "total": len(ALL_QUESTIONS_FLAT)}
    qs = ALL_QUESTION_SETS.get(test_type)
    if not qs:
        return {"error": f"未知测试类型: {test_type}"}
    return {"questions": qs, "total": len(qs)}


@router.post("/personality/submit")
def submit_test(submission: TestSubmission):
    amap = {a.question_id: a.score for a in submission.answers}

    test_type = submission.test_type
    if test_type == "all" or test_type not in ALL_QUESTION_SETS:
        test_type = "all"

    result = {}
    suggestions = []

    # ── 九型人格 ──
    if test_type in ("all", "enneagram"):
        scores = {i: [] for i in range(1, 10)}
        for q in ENNEAGRAM_QUESTIONS:
            s = amap.get(q["id"], 3)
            scores[q["dim"]].append(s)
        avg = {d: round(sum(v)/len(v), 2) if v else 0 for d, v in scores.items()}
        ranked = sorted(avg.items(), key=lambda x: -x[1])
        p1, p2 = ranked[0][0], ranked[1][0]
        result["enneagram"] = {
            "scores": avg,
            "primary": {"type": p1, "name": ENNEAGRAM_NAMES[p1], "desc": ENNEAGRAM_DESCS[p1]},
            "secondary": {"type": p2, "name": ENNEAGRAM_NAMES[p2], "desc": ENNEAGRAM_DESCS[p2]},
        }
        suggestions.extend(_suggestions_by_enneagram(p1))

    # ── MBTI ──
    if test_type in ("all", "mbti"):
        dims = {"E_I": [], "S_N": [], "T_F": [], "J_P": []}
        for q in MBTI_QUESTIONS:
            dims[q["dim"]].append(amap.get(q["id"], 3))
        mbti_type = ""
        for dim_name, vals in dims.items():
            avg = sum(vals) / len(vals) if vals else 3
            a, b = dim_name.split("_")
            mbti_type += a if avg >= 3 else b
        result["mbti"] = {
            "type": mbti_type,
            "name": MBTI_TYPES.get(mbti_type, mbti_type),
            "desc": MBTI_DESCS.get(mbti_type, ""),
            "dimensions": {
                "E/I": round(sum(dims["E_I"])/len(dims["E_I"]), 2) if dims["E_I"] else 3,
                "S/N": round(sum(dims["S_N"])/len(dims["S_N"]), 2) if dims["S_N"] else 3,
                "T/F": round(sum(dims["T_F"])/len(dims["T_F"]), 2) if dims["T_F"] else 3,
                "J/P": round(sum(dims["J_P"])/len(dims["J_P"]), 2) if dims["J_P"] else 3,
            },
        }

    # ── 霍兰德 ──
    if test_type in ("all", "holland"):
        scores = {"R": [], "I": [], "A": [], "S": [], "E": [], "C": []}
        for q in HOLLAND_QUESTIONS:
            scores[q["dim"]].append(amap.get(q["id"], 3))
        avg = {d: round(sum(v)/len(v), 2) if v else 0 for d, v in scores.items()}
        ranked = sorted(avg.items(), key=lambda x: -x[1])
        top3 = [r[0] for r in ranked[:3]]
        result["holland"] = {
            "scores": avg,
            "top3": [{"code": c, "name": HOLLAND_NAMES[c], "desc": HOLLAND_DESCS[c]} for c in top3],
            "careers": [career for c in top3 for career in HOLLAND_CAREERS.get(c, [])][:6],
        }

    # ── DISC ──
    if test_type in ("all", "disc"):
        scores = {"D": [], "I": [], "S": [], "C": []}
        for q in DISC_QUESTIONS:
            scores[q["dim"]].append(amap.get(q["id"], 3))
        avg = {d: round(sum(v)/len(v), 2) if v else 0 for d, v in scores.items()}
        ranked = sorted(avg.items(), key=lambda x: -x[1])
        primary = ranked[0][0]
        result["disc"] = {
            "scores": avg,
            "primary": {"code": primary, "name": DISC_NAMES[primary], "desc": DISC_DESCS[primary]},
            "profile": "".join(r[0] for r in ranked),
        }

    # ── 大五人格 ──
    if test_type in ("all", "bigfive"):
        scores = {"O": [], "C": [], "E": [], "A": [], "N": []}
        for q in BIGFIVE_QUESTIONS:
            scores[q["dim"]].append(amap.get(q["id"], 3))
        avg = {d: round(sum(v)/len(v), 2) if v else 0 for d, v in scores.items()}
        result["bigfive"] = {
            "scores": avg,
            "labels": BIGFIVE_NAMES,
            "descs": BIGFIVE_DESCS,
        }

    # ── 职业适应性 ──
    if test_type in ("all", "career"):
        scores = {"concern": [], "control": [], "curiosity": [], "confidence": []}
        for q in CAREER_QUESTIONS:
            scores[q["dim"]].append(amap.get(q["id"], 3))
        avg = {d: round(sum(v)/len(v), 2) if v else 0 for d, v in scores.items()}
        overall = round(sum(avg.values()) / len(avg), 2) if avg else 0
        result["career"] = {"scores": avg, "overall": overall, "labels": CAREER_LABELS}

    # ── 综合专业推荐 ──
    if not suggestions:
        suggestions = _get_combined_suggestions(result)

    result["suggestions"] = suggestions
    return result


def _suggestions_by_enneagram(t: int) -> list[str]:
    m = {
        1: ["法学", "医学", "会计学", "审计学", "建筑学"],
        2: ["教育学", "心理学", "社会工作", "护理学", "人力资源管理"],
        3: ["工商管理", "市场营销", "金融学", "国际贸易", "新闻传播学"],
        4: ["艺术设计", "音乐", "文学", "影视编导", "心理学"],
        5: ["计算机科学", "数学", "物理学", "哲学", "数据科学"],
        6: ["公安学", "法学", "会计学", "行政管理", "档案学"],
        7: ["旅游管理", "传媒", "广告学", "创业管理", "外语"],
        8: ["法学", "工商管理", "政治学", "体育", "军事学"],
        9: ["社会学", "公共管理", "图书馆学", "历史学", "园艺"],
    }
    return m.get(t, [])


def _get_combined_suggestions(result: dict) -> list[str]:
    pools = []
    if "holland" in result:
        for c in result["holland"].get("careers", []):
            pools.append(c)
    if "enneagram" in result:
        pools.extend(_suggestions_by_enneagram(result["enneagram"]["primary"]["type"]))
    if "mbti" in result:
        mbti_map = {
            "INTJ": ["人工智能", "系统架构", "投资分析", "科学研究"],
            "INTP": ["理论物理", "计算机科学", "哲学", "数学"],
            "ENTJ": ["企业管理", "律师", "管理咨询", "金融工程"],
            "ENTP": ["创业", "产品经理", "市场营销", "创意策划"],
            "INFJ": ["心理咨询", "社会工作", "写作", "教育"],
            "INFP": ["文学创作", "心理学", "艺术", "社会学"],
            "ENFJ": ["人力资源", "教育管理", "公共关系", "社会工作"],
            "ENFP": ["传媒", "市场营销", "创意写作", "旅游管理"],
            "ISTJ": ["会计学", "审计学", "行政管理", "法学"],
            "ISFJ": ["护理学", "教育学", "图书管理", "社会工作"],
            "ESTJ": ["工商管理", "公共管理", "法学", "金融"],
            "ESFJ": ["人力资源", "教育学", "护理学", "社会工作"],
            "ISTP": ["机械工程", "电子信息", "法医学", "运动训练"],
            "ISFP": ["艺术设计", "园艺", "护理学", "摄影"],
            "ESTP": ["市场营销", "体育管理", "金融交易", "紧急救援"],
            "ESFP": ["表演艺术", "旅游管理", "传媒", "活动策划"],
        }
        pools.extend(mbti_map.get(result["mbti"]["type"], []))
    seen = set()
    unique = []
    for p in pools:
        if p not in seen:
            seen.add(p)
            unique.append(p)
    return unique[:8]
