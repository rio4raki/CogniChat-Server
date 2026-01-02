import unittest
import shutil
import os
from core.memory import MemoryService
from config import Config

class TestMemoryLayer(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # 测试前，先清理掉旧的数据库，保证环境干净
        if os.path.exists(Config.CHROMA_DB_PATH):
            shutil.rmtree(Config.CHROMA_DB_PATH)
        print("\n🧪 初始化记忆服务...")
        cls.memory = MemoryService()

    def test_1_embedding(self):
        """测试 DashScope 接口是否通畅"""
        print("\n🧪 测试 1: 向量生成")
        text = "测试文本"
        vector = self.memory._get_embedding(text)
        
        self.assertIsNotNone(vector, "向量生成失败，请检查 API KEY")
        self.assertEqual(len(vector), 1024, "向量维度不对，应该是 1024")
        print("✅ 向量生成成功，维度 1024")

    def test_2_add_and_search(self):
        """测试 存入 -> 检索 流程"""
        print("\n🧪 测试 2: 存储与语义检索")
        
        # 1. 存入一些关于水果的记忆
        self.memory.add_memory("苹果是红色的，很好吃")
        self.memory.add_memory("香蕉是黄色的，弯弯的")
        self.memory.add_memory("特斯拉是一辆电动车") # 干扰项

        # 2. 搜索 "水果" 相关的
        # 注意：我没搜"苹果"，但我搜"红色的水果"，向量应该能匹配到"苹果"
        query = "红色的水果" 
        results = self.memory.search_memory(query, top_k=1)
        
        print(f"   搜索词: {query}")
        print(f"   搜索结果: {results}")

        self.assertTrue(len(results) > 0)
        # 语义匹配：应该搜到苹果，而不是特斯拉
        self.assertIn("苹果", results[0])
        print("✅ 语义检索成功")

if __name__ == '__main__':
    unittest.main()