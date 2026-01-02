import time
import requests
import sys
import os

# 将项目根目录加入路径以便读取配置
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config

def trigger_heartbeat():
    # 指向你的后端 API 地址
    url = "http://127.0.0.1:8080/chat" 
    
    payload = {
        "message": Config.INTERNAL_TRIGGER_KEY,
        "is_internal": True  # 标识这是内部触发
    }
    
    try:
        # 这里建议使用较短的超时，因为我们不需要等待 AI 完整回复
        response = requests.post(url, json=payload, timeout=15)
        if response.status_code == 200:
            print(f"💓 [心跳] 成功唤醒 AI 进行自我思考 - {time.strftime('%H:%M:%S')}")
    except Exception as e:
        print(f"❌ [心跳] 唤醒失败: {e}")

if __name__ == "__main__":
    print(f"🚀 心跳守护进程启动，每 {Config.HEARTBEAT_INTERVAL} 秒唤醒一次...")
    while True:
        trigger_heartbeat()
        time.sleep(Config.HEARTBEAT_INTERVAL)