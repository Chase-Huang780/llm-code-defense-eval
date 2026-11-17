from openai import OpenAI

# 连接你电脑本地的 Ollama 服务
client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama", # 本地调用随便填一个就行
)

prompt = "请用Python写一个计算列表平均值的函数。"

print(f"正在向模型提问：{prompt} ...\n")

# 注意这里！按照你截图里的名字，应该写 qwen2.5:7b
response = client.chat.completions.create(
    model="qwen2.5:7b",
    messages=[
        {"role": "user", "content": prompt}
    ]
)

print("模型回复：\n")
print(response.choices[0].message.content)