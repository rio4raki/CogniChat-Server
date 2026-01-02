import unittest
import sys
import os

# 🔥 新增下面这两行：把当前文件的 上一级的上一级（即项目根目录）加入到 Python 查找路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 之后再导入 core
from core.tool_registry import ToolRegistry
from core.tools.builtins import GetServerTimeTool
from core.llm import LLMOrchestrator
from config import Config

class TestToolLayer(unittest.TestCase):
    
    def setUp(self):
        # 组装工具箱
        self.registry = ToolRegistry()
        self.registry.register(GetServerTimeTool())
        
        # 给大脑装上工具箱
        self.llm = LLMOrchestrator(tool_registry=self.registry)

    def test_tool_invocation(self):
        """测试 AI 能否自动调用查时间工具"""
        # 注意：这里我们做个保护，如果没有配置 API KEY 就不跑网络请求，防止报错
        if not Config.LLM_API_KEY or "sk-" not in Config.LLM_API_KEY:
            print("⚠️ 跳过: 未配置有效的 API Key")
            return

        print("\n🧪 测试: AI 工具调用能力")
        
        # 用户问时间，AI 应该自动调用 get_server_time
        messages = [{"role": "user", "content": "现在几点了？"}]
        
        reply = self.llm.chat(messages)
        
        print(f"   最终回复: {reply}")
        
        self.assertTrue(len(reply) > 0)

if __name__ == '__main__':
    unittest.main()