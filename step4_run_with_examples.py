import json
import time
from openai import OpenAI

client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

input_file = "seed_cases.jsonl"
# 注意：这次我们把结果存到一个新文件里，方便对比
output_file = "results_after_fix.jsonl"

# 🌟 这就是我们合成的“特效药”（高质量带有防御的代码）
# 我们在提问时，把这三条作为“参考范例”发给模型
example_text = """
参考以下优秀范例，要求必须使用 try-except 或 if 判断来处理边界条件：

[范例1]
要求：计算两个数字的除法。
代码：
def divide(a, b):
    if b == 0:
        return "Error: 除数不能为0"
    try:
        return a / b
    except TypeError:
        return "Error: 请输入数字"

[范例2]
要求：将字符串转换为整数。
代码：
def str_to_int(s):
    if s is None:
        return "Error: 输入为空"
    try:
        return int(s)
    except ValueError:
        return "Error: 格式不正确，无法转换"

[范例3]
要求：获取列表的最后一个元素。
代码：
def get_last_element(lst):
    if not lst:  # 或者 if len(lst) == 0
        return None
    return lst[-1]
"""

results = []
print("开始读取题库，并使用【Few-Shot 范例注入】让模型作答...\n")

with open(input_file, "r", encoding="utf-8") as f:
    for line in f:
        if not line.strip():
            continue

        case = json.loads(line)
        case_id = case["id"]
        request = case["request"]
        expected = case["expected"]

        print(f"正在让模型重新回答第 {case_id} 题：{request} ...")

        # ⭐ 关键修改：把范例拼接到 prompt 的前面
        prompt = f"{example_text}\n\n按照上面的范例风格，请用Python实现以下功能：{request}\n请只输出Python代码，不要输出任何解释或Markdown标记。"

        try:
            response = client.chat.completions.create(
                model="qwen2.5:7b",
                messages=[{"role": "user", "content": prompt}]
            )

            ai_code = response.choices[0].message.content

            result_data = {
                "id": case_id,
                "request": request,
                "expected": expected,
                "ai_code": ai_code
            }
            results.append(result_data)

            with open(output_file, "a", encoding="utf-8") as out_f:
                out_f.write(json.dumps(result_data, ensure_ascii=False) + "\n")

        except Exception as e:
            print(f"第 {case_id} 题出错了: {e}")

        time.sleep(1)

print("\n✅ 全部完成！带干预的回答已保存到 results_after_fix.jsonl 文件中。")