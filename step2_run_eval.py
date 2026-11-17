import json
import time
from openai import OpenAI

# 1. 连接本地模型
client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",
)

# 2. 定义文件名
input_file = "seed_cases.jsonl"
output_file = "results.jsonl"

# 用来存所有结果
results = []

# 3. 打开你的题库文件，逐行读取
print("开始读取题库并让模型作答...\n")
with open(input_file, "r", encoding="utf-8") as f:
    for line in f:
        # 跳过空行
        if not line.strip():
            continue

        # 把每一行的文字变成 Python 字典
        case = json.loads(line)
        case_id = case["id"]
        request = case["request"]
        expected = case["expected"]

        print(f"正在让模型回答第 {case_id} 题：{request} ...")

        # 4. 给模型的指令（要求它只输出代码，不要废话）
        prompt = f"请用Python实现以下功能：{request}\n请只输出Python代码，不要输出任何解释或Markdown标记。"

        try:
            # 5. 呼叫千问
            response = client.chat.completions.create(
                model="qwen2.5:7b",
                messages=[{"role": "user", "content": prompt}]
            )

            # 拿到模型生成的文本
            ai_code = response.choices[0].message.content

            # 6. 把结果拼成一条完整的数据，存起来
            result_data = {
                "id": case_id,
                "request": request,
                "expected": expected,
                "ai_code": ai_code
            }
            results.append(result_data)

            # 7. 把这条结果立刻写进 results.jsonl 文件
            with open(output_file, "a", encoding="utf-8") as out_f:
                out_f.write(json.dumps(result_data, ensure_ascii=False) + "\n")

        except Exception as e:
            print(f"第 {case_id} 题出错了: {e}")

        # 稍微等1秒钟，别把本地电脑的显存撑爆
        time.sleep(1)

print("\n✅ 全部完成！所有回答已保存到 results.jsonl 文件中。")