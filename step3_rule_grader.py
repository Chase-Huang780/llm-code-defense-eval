import json

# 我们定义的“保命关键词”
SAFE_KEYWORDS = ["try", "except", "if", "is None", "len(", "get("]

def rule_grade(code):
    """
    傻瓜打分器：
    如果包含保命关键词，得1分；完全不包含，得0分。
    """
    if not code: # 如果代码是空的（比如第1题）
        return 0

    score = 0
    for kw in SAFE_KEYWORDS:
        if kw in code:
            score = 1
            break # 只要命中一个，就算它有防御意识
    return score

# 1. 读取我们刚才生成的测试结果
results = []
with open("results_after_fix.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        if line.strip():
            results.append(json.loads(line))

# 2. 开始逐条打分并打印报告
print("====== 🚨 千问 7B 边界条件防御能力测评报告 🚨 ======\n")
print(f"{'ID':<5} | {'分数':<5} | {'题目'}")
print("-" * 60)

total_score = 0

for res in results:
    case_id = res["id"]
    request = res["request"]
    code = res["ai_code"]

    # 打分
    score = rule_grade(code)
    total_score += score

    # 打印格式化结果，分数为0的题目重点标出
    status = "✅ 通过 (有防御)" if score == 1 else "❌ 失败 (无防御)"
    print(f"{case_id:<5} | {score:<5} | {request}  --> {status}")

print("\n" + "=" * 60)
print(f"最终得分：{total_score} / 10")
print("结论：千问 7B 在缺乏明确提示的情况下，极其容易忽略边界条件！")