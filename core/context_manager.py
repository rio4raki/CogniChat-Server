from collections import deque
from config import Config

class ContextManager:
    def __init__(self):
        # 使用 deque (双端队列) 实现滑动窗口，自动挤出旧消息
        self.history = deque(maxlen=Config.MAX_CONTEXT_ROUNDS)

    def add_user_message(self, content):
        """添加用户消息"""
        self.history.append({"role": "user", "content": content})

    def add_ai_message(self, content):
        """添加 AI 回复"""
        self.history.append({"role": "assistant", "content": content})

    def get_messages(self):
        """获取当前上下文列表 (转为 list)"""
        return list(self.history)

    def clear(self):
        """清空上下文 (用于重置对话)"""
        self.history.clear()