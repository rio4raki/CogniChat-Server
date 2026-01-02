import unittest
import json
from app import app
from core.security import SecurityService
from config import Config

class TestGatewaySecurity(unittest.TestCase):
    
    def setUp(self):
        # 初始化测试环境
        self.app = app.test_client()
        self.security = SecurityService(Config.SECRET_KEY)
        self.test_msg = "Hello Backend, this is a secret!"

    def test_1_crypto_logic(self):
        """测试核心加密解密算法是否闭环"""
        print("\n🧪 测试 1: 核心加解密算法")
        encrypted = self.security.encrypt(self.test_msg)
        print(f"   密文: {encrypted}")
        self.assertIn(":", encrypted) # 必须包含 IV 分隔符
        
        decrypted = self.security.decrypt(encrypted)
        print(f"   解密: {decrypted}")
        self.assertEqual(decrypted, self.test_msg)

    def test_2_gateway_integration(self):
        """测试网关是否能自动解密请求并加密响应"""
        print("\n🧪 测试 2: 网关中间件集成")
        
        # 1. 模拟前端：先把消息加密
        encrypted_input = self.security.encrypt(self.test_msg)
        
        # 2. 发送请求 (模拟 App 发送)
        payload = {
            "content": encrypted_input,
            "encrypted": True
        }
        response = self.app.post('/chat', 
                                 data=json.dumps(payload),
                                 content_type='application/json')
        
        # 3. 验证响应
        self.assertEqual(response.status_code, 200)
        res_data = response.get_json()
        
        print(f"   后端返回原始数据: {res_data}")
        
        # 验证后端是否设置了 encrypted 标志
        self.assertTrue(res_data.get('encrypted'))
        
        # 4. 模拟前端：解密后端的回复
        encrypted_reply = res_data.get('reply')
        decrypted_reply = self.security.decrypt(encrypted_reply)
        print(f"   前端解密后内容: {decrypted_reply}")
        
        # 验证内容是否正确 (app.py 里写的逻辑是重复一遍用户的话)
        expected_reply = f"我是后端AI，我听懂了你说：{self.test_msg}"
        self.assertEqual(decrypted_reply, expected_reply)

if __name__ == '__main__':
    unittest.main()