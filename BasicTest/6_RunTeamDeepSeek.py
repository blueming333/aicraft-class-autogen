import os
import asyncio
import json
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.ui import Console
from autogen_core.models import UserMessage, ModelFamily
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware  # 添加这一行
import uvicorn
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import inspect


# os.environ["OPENAI_BASE_URL"] = "https://api.deepseek.com"
# os.environ["OPENAI_API_KEY"] = "sk-"
os.environ["OPENAI_BASE_URL"] = "https://dashscope.aliyuncs.com/compatible-mode/v1"
os.environ["OPENAI_API_KEY"] = "sk-d6e9066e7a834a9e82e57177f1a2385c"


# 定义LLM
model_client = OpenAIChatCompletionClient(
    model="deepseek-r1",
    model_info={
        "function_calling": False,
        "json_output": False,
        "vision": False,
        "family": ModelFamily.R1,
    },
    max_tokens=4096,
)

# Define FastAPI app
app = FastAPI()

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有域，生产环境中应该限制为特定域
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有头信息
)

# Define request model similar to OpenAI's API
class Message(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str = "agent-team"
    messages: List[Message]
    stream: bool = True
    max_tokens: Optional[int] = None


# Create team function to reuse for different requests
def create_reflection_team():
    # 定义Agent
    primary_agent = AssistantAgent(
        name="primary",
        model_client=model_client,
        system_message="你是一个乐于助人的AI智能助手。",
        model_client_stream=True
    )

    # 定义Agent
    critic_agent = AssistantAgent(
        name="critic",
        model_client=model_client,
        system_message='提供建设性反馈意见。记住只有当你的反馈意见得到处理后再允许回复 "AiCraft"。',
        model_client_stream=True
    )

    # 定义终止条件  如果提到特定文本则终止对话
    text_termination = TextMentionTermination("AiCraft")
    # 定义终止条件，在5条信息后停止任务
    max_message_termination = MaxMessageTermination(3)
    # 使用`|` 运算符组合终止条件，在满足任一条件时停止任务
    termination = text_termination | max_message_termination

    # 定义Team Team的类型选择为RoundRobinGroupChat
    return RoundRobinGroupChat(
        participants=[primary_agent, critic_agent], 
        termination_condition=termination, 
        max_turns=None
    )


# 添加一个辅助函数，确保对象可以被JSON序列化
def make_serializable(obj):
    """递归地将对象转换为可JSON序列化的格式"""
    if isinstance(obj, (str, int, float, bool, type(None))):
        return obj
    elif isinstance(obj, (list, tuple)):
        return [make_serializable(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: make_serializable(value) for key, value in obj.items()}
    elif hasattr(obj, 'json'):
        # 如果对象有json方法，尝试使用它
        try:
            return json.loads(obj.json())
        except:
            pass
    elif hasattr(obj, 'dict'):
        # 如果对象有dict方法，尝试使用它
        try:
            return make_serializable(obj.dict())
        except:
            pass
    elif hasattr(obj, '__dict__'):
        # 提取对象的属性
        obj_dict = {}
        for key, value in obj.__dict__.items():
            if not key.startswith('_'):  # 跳过私有属性
                obj_dict[key] = make_serializable(value)
        return obj_dict
    
    # 如果都不行，转为字符串
    return str(obj)


# Stream endpoint
@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    # Extract the last user message as the task
    user_messages = [msg for msg in request.messages if msg.role == "user"]
    if not user_messages:
        return {"error": "No user message found"}
    
    task = user_messages[-1].content
    
    # Create team
    reflection_team = create_reflection_team()
    
    # Create streaming response with simple JSON format
    async def stream_response():
        async for message in reflection_team.run_stream(task=task):
            # 打印原始消息对象信息
            print(f"Message Type: {type(message)}")
            print(f"Message Content: {message}")
            
            # 提取基本信息
            message_json = {
                "type": message.__class__.__name__
            }
            
            # 处理常见属性
            if hasattr(message, 'content'):
                message_json['content'] = str(message.content)
                
            if hasattr(message, 'sender') and message.sender:
                if hasattr(message.sender, 'name'):
                    message_json['sender_name'] = message.sender.name
                else:
                    message_json['sender'] = str(message.sender)
                    
            if hasattr(message, 'recipient') and message.recipient:
                if hasattr(message.recipient, 'name'):
                    message_json['recipient_name'] = message.recipient.name
                else:
                    message_json['recipient'] = str(message.recipient)
            
            # 添加任何其他可能的属性
            for attr in ['cost', 'metadata', 'timestamp', 'role']:
                if hasattr(message, attr) and getattr(message, attr) is not None:
                    message_json[attr] = str(getattr(message, attr))
            
            # 发送JSON格式的消息
            yield json.dumps(message_json) + "\n"
    
    return StreamingResponse(stream_response(), media_type="application/json")


async def main() -> None:
    # 定义Agent
    primary_agent = AssistantAgent(
        name="primary",
        model_client=model_client,
        system_message="你是一个乐于助人的AI智能助手。",
        model_client_stream=True
    )

    # 定义Agent
    critic_agent = AssistantAgent(
        name="critic",
        model_client=model_client,
        system_message='提供建设性反馈意见。记住只有当你的反馈意见得到处理后再允许回复 "AiCraft"。',
        model_client_stream=True
    )

    # 定义终止条件  如果提到特定文本则终止对话
    text_termination = TextMentionTermination("AiCraft")
    # 定义终止条件，在5条信息后停止任务
    max_message_termination = MaxMessageTermination(3)
    # 使用`|` 运算符组合终止条件，在满足任一条件时停止任务
    termination = text_termination | max_message_termination

    # 定义Team Team的类型选择为RoundRobinGroupChat
    reflection_team = RoundRobinGroupChat(participants=[primary_agent, critic_agent], termination_condition=termination, max_turns=None)

    # 运行team并将消息转换为JSON格式输出
    async for message in reflection_team.run_stream(task="写一首七言绝句，关于秋天"):
        # 打印原始消息对象信息
        # print(f"Message Type: {type(message)}")
        
        # 提取基本信息
        message_json = {
            "type": message.__class__.__name__
        }
        print(message_json)
        
        # 处理常见属性
        if hasattr(message, 'content'):
            message_json['content'] = str(message.content)
            
        if hasattr(message, 'sender') and message.sender:
            if hasattr(message.sender, 'name'):
                message_json['sender_name'] = message.sender.name
            else:
                message_json['sender'] = str(message.sender)
                
        if hasattr(message, 'recipient') and message.recipient:
            if hasattr(message.recipient, 'name'):
                message_json['recipient_name'] = message.recipient.name
            else:
                message_json['recipient'] = str(message.recipient)
        
        # 添加任何其他可能的属性
        for attr in ['cost', 'metadata', 'timestamp', 'role']:
            if hasattr(message, attr) and getattr(message, attr) is not None:
                message_json[attr] = str(getattr(message, attr))
        
        # 打印JSON格式的消息
        print(json.dumps(message_json, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    # Run the FastAPI server when script is executed directly
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "serve":
        uvicorn.run("6_RunTeamDeepSeek:app", host="0.0.0.0", port=8000, reload=True)
    else:
        # Otherwise run the original main function
        asyncio.run(main())

