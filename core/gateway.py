from flask import request, jsonify, g
import json
import time
from .security import SecurityService
from .logger import FlowLogger
from config import Config

# 初始化安全服务
security_service = SecurityService(Config.SECRET_KEY)

# ==================== 🔌 WebSocket 手动调用接口 (新增) ====================

def manual_decrypt(raw_content):
    """
    供 WebSocket 逻辑手动调用：解密来自客户端的消息
    """
    if not Config.ENABLE_ENCRYPTION or not raw_content:
        return raw_content
    
    FlowLogger.security("Socket解密前", f"{raw_content[:20]}...")
    decrypted_content = security_service.decrypt(raw_content)
    
    if decrypted_content is None:
        FlowLogger.error("Socket安全", "解密失败")
        return None
    
    FlowLogger.security("Socket解密后", decrypted_content)
    return decrypted_content

def manual_encrypt(plain_text):
    """
    供 WebSocket 逻辑手动调用：加密准备发往客户端的消息
    返回: (加密后的文本, 是否已加密标记)
    """
    if not Config.ENABLE_ENCRYPTION:
        return plain_text, False
    
    FlowLogger.security("Socket加密回复", f"{plain_text[:20]}...")
    encrypted_text = security_service.encrypt(plain_text)
    return encrypted_text, True

# ==================== 🔙 HTTP 自动网关逻辑 (保持原版无损) ====================

def configure_gateway(app):
    
    # --- 进站: 解解密 ---
    @app.before_request
    def decrypt_incoming_request():
        if request.is_json:
            data = request.get_json()
            # 确保 data 是字典
            if isinstance(data, dict):
                is_encrypted = data.get('encrypted', False)
                raw_content = data.get('content', '')

                if is_encrypted and Config.ENABLE_ENCRYPTION:
                    FlowLogger.security("解密前", f"{raw_content[:20]}...")
                    decrypted_content = security_service.decrypt(raw_content)
                    
                    if decrypted_content is None:
                        FlowLogger.error("安全", "解密失败")
                        return jsonify({"error": "Decryption failed", "code": 401}), 401
                    
                    FlowLogger.security("解密后", decrypted_content)
                    request.json['content'] = decrypted_content
                    g.was_encrypted = True
                else:
                    g.was_encrypted = False
                    if raw_content:
                        FlowLogger.info("网关", "收到明文消息")

    # --- 出站: 加密 ---
    @app.after_request
    def encrypt_outgoing_response(response):
        # 只有 200 OK 且是 JSON 的响应才处理
        if response.status_code == 200 and response.is_json:
            original_data = response.get_json()
            
            # 如果不是字典，跳过
            if not isinstance(original_data, dict):
                return response

            # 检查开关
            if Config.ENABLE_ENCRYPTION:
                # 场景 A: 加密实时回复 (reply)
                # (逻辑: 如果请求是加密进来的，回复也加密出去)
                if getattr(g, 'was_encrypted', False) and 'reply' in original_data:
                    plain_reply = original_data.get('reply', '')
                    FlowLogger.security("加密回复", f"{plain_reply[:20]}...")
                    
                    encrypted_reply = security_service.encrypt(plain_reply)
                    
                    original_data['reply'] = encrypted_reply
                    original_data['encrypted'] = True

                # 场景 B: 加密历史记录 (history)
                if 'history' in original_data:
                    raw_list = original_data['history']
                    # 先把 List 转成 JSON String
                    list_str = json.dumps(raw_list, ensure_ascii=False)
                    FlowLogger.security("加密历史", f"正在打包 {len(raw_list)} 条记录...")
                    
                    encrypted_history = security_service.encrypt(list_str)
                    
                    original_data['history'] = encrypted_history
                    original_data['encrypted'] = True

            # 统一补全时间戳
            if 'time' not in original_data:
                original_data['time'] = int(time.time())
            
            # 更新响应数据
            response.set_data(json.dumps(original_data))

        return response