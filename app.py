# 必须放在最顶行
import gevent.monkey
gevent.monkey.patch_all()

import time
import sys
import warnings
import random
import re
import gevent
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from openai import OpenAI
from colorama import init, Fore, Style

init(autoreset=True)
warnings.filterwarnings("ignore", category=DeprecationWarning)

from core.gateway import configure_gateway, manual_decrypt, manual_encrypt
from core.memory import MemoryService
from core.prompt_engine import PromptEngine
from core.llm import LLMOrchestrator
from core.tool_registry import ToolRegistry
from core.tools.builtins import GetServerTimeTool
from core.router import SemanticRouter
from core.message_logger import MessageLogger
from core.logger import FlowLogger
from core.context_manager import ContextManager
from config import Config

# 引入硬件驱动 (这会自动启动后台线程)
from core.hardware.massager import massager

# ==================== 插件：消息切分 ====================
class MessageSplitter:
    def __init__(self, api_key, base_url, model):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model

    def split(self, text):
        prompt = (
            "你是一个社交消息切分专家。将下段文字切分成符合人类聊天习惯的短句。\n"
            "要求：1.每句话独立成行。2.保持原意，不要加解释。3.切分点要自然。注意:不要私自添加或修改内容\n"
            f"内容：{text}"
        )
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                timeout=10 
            )
            raw = response.choices[0].message.content.strip()
            lines = [line.strip() for line in raw.split('\n') if line.strip()]
            if len(lines) > 0: return lines
        except Exception as e:
            FlowLogger.error("Plugin", f"AI切分失败，启用正则保底: {e}")
        return [s.strip() for s in re.split(r'[。！？；…\n]', text) if s.strip()]

splitter = MessageSplitter(
    api_key="sk-da77abc6d7ee444396d2c0ea12f710ba",
    base_url="https://api.deepseek.com", 
    model="deepseek-chat"
)

# ==================== 服务初始化 ====================
app = Flask(__name__)
socketio = SocketIO(
    app, 
    cors_allowed_origins=Config.CORS_ALLOWED_ORIGINS, 
    async_mode='gevent',
    ping_timeout=10,    
    ping_interval=5,
    manage_session=False 
)

configure_gateway(app)

# 这里会初始化 ToolRegistry，进而实例化 ControlMassagerTool
# 之前的报错就是因为这里实例化失败，现在 hardware.py 修复后应该没问题了
tool_registry = ToolRegistry()

raw_router_client = OpenAI(api_key=Config.ROUTER_API_KEY, base_url=Config.ROUTER_BASE_URL)
memory_service = MemoryService(cleaning_llm_client=raw_router_client)
prompt_engine = PromptEngine()
message_logger = MessageLogger() 

llm_orchestrator = LLMOrchestrator(tool_registry=tool_registry, message_logger=message_logger) 

semantic_router = SemanticRouter()
context_manager = ContextManager()
thinking_lock = False

@socketio.on('connect')
def handle_connect():
    FlowLogger.info("Socket", f"客户端已握手连接: {request.sid}")
    emit('conn_status', {'status': 'online', 'msg': '全双工通道已开启'})

    try:
        history = message_logger.get_all_history()
        if history:
            last_msg = history[-1]
            if last_msg.get('role') == 'ai' and last_msg.get('content'):
                content = last_msg.get('content', '')
                enc_content, was_encrypted = manual_encrypt(content)
                emit('receive_message', {
                    "reply": enc_content,
                    "time": last_msg.get('time', time.time()), 
                    "is_final": True,
                    "encrypted": was_encrypted,
                    "is_sync_msg": True 
                })
                FlowLogger.info("Sync", "已从历史记录同步最后一条 AI 消息")
    except Exception as e:
        print(f"⚠️ [Sync Error] 同步检查失败: {e}")

@socketio.on('disconnect')
def handle_disconnect():
    FlowLogger.info("Socket", f"客户端已断开: {request.sid}")

@socketio.on('send_message')
def handle_socket_chat(data):
    global thinking_lock
    thinking_lock = True 

    is_encrypted = data.get('encrypted', False)
    raw_content = data.get('content', '')

    user_input = raw_content
    if is_encrypted and Config.ENABLE_ENCRYPTION:
        user_input = manual_decrypt(raw_content)
        if user_input is None:
            FlowLogger.error("Socket", "解密失败")
            emit('error', {'msg': '解密失败'})
            thinking_lock = False
            return

    FlowLogger.receive(user_input)
    message_logger.save_message("user", user_input, time.time())

    should_search = semantic_router.should_retrieve_memory(user_input)
    memory_str = ""
    if should_search:
        memories = memory_service.search_memory(user_input, top_k=Config.MEMORY_TOP_K)
        if memories:
            memory_str = "; ".join(memories)
            FlowLogger.memory("检索成功", f"找到 {len(memories)} 条相关记忆")

    FlowLogger.brain("正在生成完整回复...")
    messages = prompt_engine.assemble(
        user_input=user_input,
        short_term_history=context_manager.get_messages(),
        memory_context=memory_str,
        device_status="Connected"
    )
    
    full_ai_reply = llm_orchestrator.chat(messages)
    
    is_memory_saved = memory_service.add_memory(user_input, role="user") 
    context_manager.add_user_message(user_input)
    context_manager.add_ai_message(full_ai_reply)
    
    sentences = splitter.split(full_ai_reply)
    pre_think_delay = (len(sentences[0]) * 0.2) + random.uniform(0.1, 0.3)
    gevent.sleep(pre_think_delay)

    for i, sentence in enumerate(sentences):
        final_reply, was_encrypted = manual_encrypt(sentence)
        ai_ts = time.time()
        is_last_packet = (i == len(sentences) - 1)

        message_logger.save_message("ai", sentence, ai_ts)

        emit('receive_message', {
            "reply": final_reply,
            "time": ai_ts,
            "is_memory_saved": is_memory_saved if i == 0 else False,
            "encrypted": was_encrypted,
            "is_final": is_last_packet,
            "is_typing": not is_last_packet 
        })

        if not is_last_packet:
            next_len = len(sentences[i+1])
            typing_delay = (next_len * 0.2) + random.uniform(0.1, 0.3)
            gevent.sleep(typing_delay) 
    
    thinking_lock = False

@app.route('/chat', methods=['POST'])
def chat_controller():
    global thinking_lock
    data = request.get_json()
    
    is_internal = data.get('is_internal', False)
    user_input = data.get('message', '')

    if is_internal and user_input == Config.INTERNAL_TRIGGER_KEY:
        if thinking_lock:
            return jsonify({"status": "busy", "reason": "AI is talking to user"})
        
        print(f"{Fore.MAGENTA}💓 [心跳] 触发 AI 深度自省...{Style.RESET_ALL}")
        internal_prompt = (
            "（系统提示：自省时间。若需主动联系用户，请调用 push_message_to_user。保持沉默则无需操作。）"
        )
        messages = prompt_engine.assemble(
            user_input=internal_prompt, 
            short_term_history=context_manager.get_messages(),
            device_status="Idle"
        )
        llm_orchestrator.chat(messages)
        return jsonify({"status": "heartbeat_processed"})

    FlowLogger.receive(user_input)
    messages = prompt_engine.assemble(user_input=user_input, short_term_history=context_manager.get_messages(), device_status="80%")
    ai_reply = llm_orchestrator.chat(messages)
    return jsonify({"reply": ai_reply, "time": time.time()})

@app.route('/history', methods=['GET'])
def get_history():
    history_list = message_logger.get_all_history()
    return jsonify({"history": history_list})

@app.route('/history', methods=['DELETE'])
def clear_history():
    message_logger.clear_history()
    context_manager.clear()
    FlowLogger.info("SYSTEM", "所有历史记录已清除")
    return jsonify({"status": "success", "message": "云端及上下文已清空"})

@app.route('/status', methods=['GET'])
def server_status():
    return jsonify({"status": "online", "server_time": time.time()})

if __name__ == '__main__':
    print(f"{Fore.CYAN}🌟 心智系统拦截器已就绪，等待心跳守护进程...{Style.RESET_ALL}")
    # 这里会尝试连接手柄
    massager._try_connect()
    socketio.run(app, host='0.0.0.0', port=8080, debug=False)