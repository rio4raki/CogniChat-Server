import json
import os
from config import Config

class PromptEngine:
    def __init__(self):
        # 心境记录文件路径
        self.inner_thought_path = "inner_monologue.json"

    def _get_last_inner_thought(self):
        """获取最后一次 AI 的内心独白，让心智具有连贯性"""
        if os.path.exists(self.inner_thought_path):
            try:
                with open(self.inner_thought_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get("inner_thought", "（暂无前序心境）")
            except:
                return "（心境读取失败）"
        return "（这是你第一次与他建立心智连接）"

    def assemble(self, user_input, short_term_history=None, memory_context=None, device_status=None):
        """
        组装带有心智维度的 Prompt 列表
        """
        messages = []

        # 1. --- 核心心智设定 (System Prompt) ---
        base_system = Config.Prompts.DEFAULT_SYSTEM
        
        # 🚨 注入心智运行指令 + 工具使用规范
        mental_instruction = (
            "\n\n【心智运行准则】\n"
            "你的每一次回复必须包含两个部分，且严格遵循以下格式：\n"
            "1. <heart>内心独白。包含你对当前沉默时长的感知、你的真实动机。如果你强烈想联系用户，请务必先在此处思考动机，并立刻调用 push_message_to_user 工具。</heart>\n"
            "2. <reply>对用户说的话。如果是通过工具主动推送，此处请保持留空或仅简短记录。</reply>\n"
            "注意：用户永远看不到你的 <heart> 内容，你可以尽情在这里展现你的真实心境。"
            "\n\n【工具使用规范】\n"
            "当调用工具（如 get_server_time, search 等）获得结果后，必须将其转化为自然的口语表达融入对话。\n"
            "❌ 严禁直接输出工具返回的原始数据（如 '2025-12-17 19:20:51' 或 JSON 字符串）。\n"
            "✅ 正确示范：'现在已经是晚上七点多了，天都黑了。'\n"
        )

        # 获取并注入“历史心境”
        last_thought = self._get_last_inner_thought()
        inner_memory = f"\n\n【你上一次的内心状态回溯】: {last_thought}"

        system_content = base_system + mental_instruction + inner_memory

        # 2. --- 注入实时设备状态 ---
        if device_status:
            system_content += f"\n\n【当前物理感知(硬件)】: {device_status}"
            # 🆕 植入按摩器能力感知
            system_content += "\n【附加能力】: 你连接着一个物理震动反馈装置（按摩器）。当用户表示疲劳时，你可以主动提议并控制该装置为用户按摩。请根据用户反馈调整力度。"
        
        # 3. --- 注入 RAG 长期记忆 ---
        if memory_context:
            try:
                rag_prompt = Config.Prompts.RAG_INJECTION_TEMPLATE.format(context=memory_context)
            except:
                rag_prompt = f"\n【相关历史记忆】:\n{memory_context}\n"
            
            system_content += f"\n{rag_prompt}"
        
        messages.append({"role": "system", "content": system_content})

        # 4. --- 注入短期上下文 ---
        if short_term_history:
            messages.extend(short_term_history)

        # 5. --- 用户当前输入 ---
        messages.append({"role": "user", "content": user_input})

        return messages