from collections import deque
from openai import OpenAI
from config import Config

class SemanticRouter:
    def __init__(self):
        # 🔥 修改点：使用 Router 专用的配置初始化
        # 这样就和主聊天 AI 完全解耦了，可以用不同的 Key，甚至不同的服务商
        self.client = OpenAI(
            api_key=Config.ROUTER_API_KEY,
            base_url=Config.ROUTER_BASE_URL
        )
        self.model = Config.ROUTER_MODEL
        
        # 初始化短期记忆队列
        self.short_term_history = deque(maxlen=Config.ROUTER_CONTEXT_WINDOW)

    def should_retrieve_memory(self, user_input):
        """
        判断是否需要检索记忆
        :return: True (需要检索) / False (跳过检索)
        """
        if not Config.ENABLE_SEMANTIC_ROUTER:
            print("🚦 [路由] 模块已关闭，默认允许检索")
            return True

        try:
            messages = [
                {"role": "system", "content": Config.Prompts.ROUTER_SYSTEM}
            ]

            if self.short_term_history:
                history_str = "\n".join(self.short_term_history)
                messages.append({"role": "system", "content": f"【短期上下文参考】:\n{history_str}"})

            messages.append({"role": "user", "content": f"用户输入: {user_input}"})

            # 使用专用模型进行判断
            response = self.client.chat.completions.create(
                model=self.model,  # 使用配置里的小模型
                messages=messages,
                temperature=Config.ROUTER_TEMPERATURE,
                stream=False
            )

            result = response.choices[0].message.content.strip().upper()
            
            # 更新短期记忆
            self.short_term_history.append(user_input)

            if "YES" in result:
                print(f"🚦 [路由] ({self.model}) 判定: ✅ YES")
                return True
            else:
                print(f"🚦 [路由] ({self.model}) 判定: ⛔ NO")
                return False

        except Exception as e:
            print(f"⚠️ [路由] 判断出错，降级为默认检索: {e}")
            return True