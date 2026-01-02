import re
from openai import OpenAI

class MessageSplitterPlugin:
    def __init__(self, api_key, base_url, model):
        # 独立 API 配置
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model

    def split_text(self, text):
        """
        使用独立 AI 将长回复切分为自然的单句列表
        """
        # 如果文本很短，直接返回
        if len(text) < 15:
            return [text]

        prompt = (
            "你是一个聊天消息切分助手。你的唯一任务是将一段长回复切分成符合人类聊天习惯的短句。\n"
            "规则：\n"
            "1. 每句话独立成行，不要有任何序号或前缀。\n"
            "2. 保持原话内容，只做切分，不做总结或改写。\n"
            "3. 按照自然的语意停顿切分（如：你好呀。今天天气不错。我们要不要出去玩？）。\n"
            "4. 严禁输出任何解释性文字。\n\n"
            f"待切分内容：{text}"
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                timeout=10
            )
            raw_output = response.choices[0].message.content.strip()
            # 按行切分并过滤空行
            sentences = [line.strip() for line in raw_output.split('\n') if line.strip()]
            return sentences if sentences else [text]
        except Exception as e:
            print(f"❌ [Splitter] 插件调用失败: {e}")
            # 保底方案：使用标点符号正则切分
            return [s.strip() for s in re.split(r'[。！？；\n]', text) if s.strip()]