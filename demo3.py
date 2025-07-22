
import asyncio
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.models import ModelFamily

# 创建一个专门用于写恐怖小故事的工具函数
async def generate_horror_elements(theme: str) -> str:
    """根据主题生成恐怖故事元素"""
    horror_elements = {
        "黑暗": "深夜、废弃建筑、地下室、阴暗角落",
        "超自然": "鬼魂、诅咒、灵异现象、神秘力量",
        "心理": "恐惧、偏执、幻觉、内心阴暗面",
        "悬疑": "未知威胁、神秘失踪、诡异事件、不可解释的现象"
    }
    
    # 简单的元素匹配，实际应用中可以更复杂
    elements = []
    for key, value in horror_elements.items():
        if key in theme:
            elements.append(value)
    
    return f"恐怖元素建议: {', '.join(elements) if elements else '经典恐怖氛围、神秘感、紧张气氛'}"

# 创建OpenAI模型客户端
model_client = OpenAIChatCompletionClient(
            model="deepseek-chat",
            base_url="https://api.deepseek.com",
            api_key="sk-36a3fb92e2414794bd9785014e4a1d84",
            model_info={
                "function_calling": True,
                "json_output": True,
                "vision": False,
                "stream": True,
                "family": ModelFamily.UNKNOWN,
                "structured_output": True,
            }
        )



# 创建专门写恐怖小故事的助手代理
horror_story_agent = AssistantAgent(
    name="恐怖小说家",
    model_client=model_client,
    tools=[generate_horror_elements],
    system_message="""
    你是一位专业的恐怖小说作家。你的任务是根据用户提供的文本或主题，创作引人入胜的恐怖小故事。

    创作要求：
    1. 故事要有清晰的情节结构：开端、发展、高潮、结局
    2. 营造恐怖氛围，但避免过于血腥暴力的描述
    3. 注重心理恐怖和悬疑感
    4. 字数控制在500-800字左右
    5. 使用生动的描写和对话增强故事感染力
    6. 可以使用工具获取恐怖元素建议来丰富故事内容

    请根据用户输入的主题或文本片段，创作一个完整的恐怖小故事。
    """,
)

async def create_horror_story(input_text: str):
    result = await horror_story_agent.run(
        task=f"请根据以下文本或主题创作一个恐怖小故事：{input_text}"
    )
    print(result)
    return result

# 示例使用
async def main():
    """主函数演示"""
    # 示例输入文本
    example_texts = [
        "一个人在深夜听到楼上传来奇怪的脚步声"
    ]
    
    print("🎃 欢迎使用恐怖小故事生成器！")
    print("以下是一些示例：")
    
    # 选择一个示例进行演示
    selected_text = example_texts[0]
    await create_horror_story(selected_text)
    
    print("\n" + "="*50)
    print("💡 提示：您可以输入任何主题或文本片段来生成恐怖故事")
    print("例如：'废弃医院'、'午夜十二点'、'陌生的敲门声' 等")

# 如果直接运行此文件，执行示例
if __name__ == "__main__":
    asyncio.run(main())
