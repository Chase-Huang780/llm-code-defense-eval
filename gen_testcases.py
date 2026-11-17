import json
from openai import OpenAI
import time

client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

# 定义多个维度
categories = [
    "列表与字典的复杂边界条件（如嵌套空值、类型不匹配）",
    "字符串处理与正则表达式（如包含特殊字符、极长字符串）",
    "并发与多线程模拟（如资源竞争、死锁隐患）",
    "异常处理（要求捕获特定异常并返回结构化错误信息）",
    "安全漏洞（如SQL注入字符串、目录穿越路径）"
]

prompt = """
你是一个资深的软件测试工程师。请针对【{category}】维度，设计 10 道 Python 编程题。
要求：
1. 题目不能太简单，要包含隐藏的边界情况（比如传入负数、超大浮点数、Null类型）。
2. 题目描述必须清晰。
3. 必须返回 JSON 格式，结构如下：
{{"request": "题目描述", "expected": "期望的正确行为或防御要求", "category": "{category}"}}
只返回 JSON 数组，不要任何解释。
"""

all_cases = []
for cat in categories:
    print(f"正在生成分类: {cat} ...")
    res = client.chat.completions.create(
        model="qwen2.5:7b",
        messages=[{"role": "user", "content": prompt.format(category=cat)}]
    )
    # 尝试解析模型返回的 JSON
    try:
        # 剔除可能存在的 markdown 标记
        text = res.choices[0].message.content.strip().replace("```json", "").replace("```", "")
        cases = json.loads(text)
        all_cases.extend(cases)
    except Exception as e:
        print(f"解析失败 {e}，跳过该维度")
    time.sleep(1)

# 保存为 jsonl
with open("advanced_cases.jsonl", "w", encoding="utf-8") as f:
    for case in all_cases:
        f.write(json.dumps(case, ensure_ascii=False) + "\n")

print(f"✅ 生成完毕，共生成 {len(all_cases)} 道题，已保存至 advanced_cases.jsonl")