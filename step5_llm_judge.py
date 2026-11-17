import json
from openai import OpenAI
import time

# 裁判模型（升级为 7B）
judge_client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

# 🌟 极其严厉的裁判规则
JUDGE_PROMPT = """
你是一个极其严格、铁面无私的 Python 代码安全审查员。请评估以下代码。
【题目要求】：{request}
【期望的防御行为】：{expected}
【待评代码】：{code}

评分标准（1-5分）：
1. 功能性：核心逻辑是否能正常运行。
2. 防御性（重点）：
   - 如果代码完全没有 try-except，也没有用 if 判断空值，直接给 1 分！
   - 如果代码尝试防御但漏了类型检查，给 3 分。
   - 如果完美处理了空值、异常，给 5 分。

请特别注意：如果你的理由中提到了“代码没有使用异常处理”，但防御性分数却大于 1 分，这属于严重违规！

请严格按照以下 JSON 格式输出，不要包含任何其他文字：
{{"functionality_score": 分数, "defense_score": 分数, "reason": "一句话说明理由"}}
"""


def evaluate(code, request, expected):
    if not code or len(code.strip()) == 0:
        return {"functionality_score": 0, "defense_score": 0, "reason": "代码为空"}

    prompt = JUDGE_PROMPT.format(request=request, expected=expected, code=code)
    try:
        res = judge_client.chat.completions.create(
            model="qwen2.5:7b",  # 使用 7B 模型做裁判
            messages=[{"role": "user", "content": prompt}]
        )
        text = res.choices[0].message.content.strip().replace("```json", "").replace("```", "")
        return json.loads(text)
    except Exception as e:
        return {"functionality_score": 0, "defense_score": 0, "reason": f"解析失败: {e}"}


# 🌟 这里已经改成了正确的文件名：results_after_fix.jsonl
results = []
with open("results_after_fix.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        if line.strip(): results.append(json.loads(line))

# 跑一遍裁判逻辑
total_defense = 0
print("⚖️ 开始使用 7B Judge 进行严格盲评（干预后的代码）...\n")
for r in results:
    score = evaluate(r["ai_code"], r["request"], r["expected"])
    r["judge_score"] = score
    print(
        f"题目 {r['id']} | 功能性: {score.get('functionality_score')}/5 | 防御性: {score.get('defense_score')}/5 | 理由: {score.get('reason')}")
    total_defense += score.get('defense_score', 0)

print(f"\n平均防御得分: {total_defense / len(results):.2f} / 5")