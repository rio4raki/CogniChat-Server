import unittest
from core.prompt_engine import PromptEngine
from core.llm import LLMOrchestrator
from config import Config

class TestBrainLayer(unittest.TestCase):
    
    def setUp(self):
        self.engine = PromptEngine()
        self.llm = LLMOrchestrator()

    def test_1_prompt_assembly(self):
        """测试 Prompt 组装逻辑"""
        print("\n🧪 测试 1: Prompt 组装")
        msgs = self.engine.assemble(
            user_input="你好", 
            memory_context="用户喜欢吃苹果",
            device_status="电量10%"
        )
        
        # 验证是否包含了系统人设、记忆、用户输入
        print(f"   组装结果: {msgs}")
        self.assertEqual(len(msgs), 3) # System(含设备) + Memory + User
        self.assertIn("电量10%", msgs[0]['content'])
        self.assertIn("用户喜欢吃苹果", msgs[1]['content'])

    def test_2_llm_connection(self):
        """测试 LLM 实际调用 (需要真实的 API KEY)"""
        print("\n🧪 测试 2: LLM 连接测试")
        if "sk-" not in Config.LLM_API_KEY:
            print("⚠️ 跳过: 未配置有效的 API Key")
            return

        messages = [{"role": "user", "content": "请回复'测试成功'这四个字"}]
        reply = self.llm.chat(messages)
        
        print(f"   AI 回复: {reply}")
        self.assertIsNotNone(reply)
        self.assertTrue(len(reply) > 0)

if __name__ == '__main__':
    unittest.main()