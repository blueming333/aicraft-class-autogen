# 导入所需库
import json
from openai import OpenAI

# 设置API密钥和DeepSeek的API地址（请替换为你自己的API密钥）
api_key = "sk-bbac7524061c4acfb485f953e4074f66"
base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"

# 创建OpenAI客户端
client = OpenAI(
    api_key=api_key,
    base_url=base_url,
)

# 系统提示，告诉模型如何输出JSON格式
system_prompt = """
你将收到一段考试文本，请解析出其中的“question”和“answer”，并以JSON格式输出。

示例输入：
Which is the highest mountain in the world? Mount Everest.

示例JSON输出：
{
    "question": "Which is the highest mountain in the world?",
    "answer": "Mount Everest"
}
"""

# 用户输入内容
user_prompt = "Which is the longest river in the world? The Nile River."

# 构造消息列表
messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": user_prompt}
]

# 调用DeepSeek大模型，要求输出JSON对象
response = client.chat.completions.create(
    model="qwen-max-latest",
    messages=messages,
    response_format={
        'type': 'json_object'  # 关键参数，要求输出为JSON对象
    },
    max_tokens=256  # 防止输出被截断
)

# 解析并打印模型输出的JSON内容
print(json.loads(response.choices[0].message.content))
