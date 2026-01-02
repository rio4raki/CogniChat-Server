import json
import traceback
import re
import os
import datetime
from openai import OpenAI
from config import Config

class LLMOrchestrator:
    def __init__(self, tool_registry=None, message_logger=None):
        mask_key = Config.LLM_API_KEY[:4] + "****" if Config.LLM_API_KEY else "None"
        print(f"🔧 [LLM初始化] Base: {Config.LLM_BASE_URL} | Model: {Config.LLM_MODEL} | Key: {mask_key}")
        
        self.client = OpenAI(
            api_key=Config.LLM_API_KEY,
            base_url=Config.LLM_BASE_URL
        )
        self.model = Config.LLM_MODEL
        self.tool_registry = tool_registry
        self.message_logger = message_logger 
        self.mental_log_path = "inner_monologue.json" 

    def _record_mental_state(self, thought, tool_summary=None):
        """记录内心独白"""
        try:
            log_entry = {
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "thought": thought,
                "tool_calls": tool_summary if tool_summary else []
            }

            if os.path.exists(self.mental_log_path):
                with open(self.mental_log_path, 'r', encoding='utf-8') as f:
                    try:
                        data = json.load(f)
                    except:
                        data = {"performance_log": []}
            else:
                data = {"performance_log": []}

            data["last_updated"] = log_entry["timestamp"]
            data["inner_thought"] = thought
            data["performance_log"].append(log_entry)
            data["performance_log"] = data["performance_log"][-50:]

            with open(self.mental_log_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"⚠️ [存储失败] 无法写入心智日志: {e}")

    def _mental_interceptor(self, raw_content, tool_summary=None):
        """
        🧠 强力清洗版：确保入库的数据是干净的
        包含针对 DeepSeek 特殊 Token 的过滤
        """
        if not raw_content:
            return ""

        # 1. 提取并记录内心独白
        heart_match = re.search(r'<heart>(.*?)</heart>', raw_content, re.DOTALL)
        if heart_match:
            inner_thought = heart_match.group(1).strip()
            print(f"🖤 [内心独白] {inner_thought}")
            self._record_mental_state(inner_thought, tool_summary)

        # 2. 清洗逻辑
        clean_text = raw_content

        # A. 移除内心独白块 <heart>...</heart>
        clean_text = re.sub(r'<heart>.*?</heart>', '', clean_text, flags=re.DOTALL)
        
        # B. 移除自定义的 <reply> 标签
        clean_text = re.sub(r'</?reply>', '', clean_text)
        
        # C. 🆕 [新增] 移除 DeepSeek 特有的 DSML 工具调用乱码
        # 匹配 <｜DSML｜...> 和 </｜DSML｜...> 这种特殊全角符号标签
        # 注意：这里同时匹配全角｜和半角|，以防万一
        clean_text = re.sub(r'<[｜|]DSML[｜|].*?>', '', clean_text, flags=re.DOTALL)
        clean_text = re.sub(r'</[｜|]DSML[｜|].*?>', '', clean_text, flags=re.DOTALL)
        
        # D. 移除可能的残留空白
        return clean_text.strip()

    def chat(self, messages):
        from __main__ import socketio, manual_encrypt

        tools_schema = self.tool_registry.get_openai_tools() if self.tool_registry else None
        tool_execution_summary = [] 
        
        print("🤖 [思考] AI 正在思考...")
        try:
            # 1. 第一轮思考
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools_schema if tools_schema else None,
                stream=False
            )
            
            response_msg = response.choices[0].message
            
            # 2. 工具处理逻辑
            if response_msg.tool_calls:
                messages.append(response_msg)
                
                for tool_call in response_msg.tool_calls:
                    func_name = tool_call.function.name
                    func_args = json.loads(tool_call.function.arguments)
                    tool_execution_summary.append(func_name)
                    
                    print(f"🔧 [工具] AI 调用: {func_name}")
                    
                    tool_instance = self.tool_registry.get_tool(func_name)
                    tool_result = tool_instance.execute(**func_args) if tool_instance else "Error"
                    
                    # 处理主动推送时，先存库！
                    if str(tool_result).startswith("[INTERNAL_PUSH]"):
                        push_content = tool_result.replace("[INTERNAL_PUSH]", "").strip()
                        print(f"💓 [主动推送] 内容: {push_content}")
                        
                        current_ts = datetime.datetime.now().timestamp()
                        
                        # A. 先存入历史记录
                        if self.message_logger:
                            self.message_logger.save_message("ai", push_content, current_ts)
                            print(f"💾 [持久化] 消息已预先写入数据库")

                        # B. 再尝试 Socket 推送
                        encrypted_content, _ = manual_encrypt(push_content)
                        socketio.emit('receive_message', {
                            "reply": encrypted_content,
                            "time": current_ts,
                            "is_final": True,
                            "encrypted": True,
                            "is_internal_push": True 
                        })
                        tool_result = "[INTERNAL] 消息已存档并尝试推送。"

                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": str(tool_result)
                    })

                print("🤖 [思考] AI 总结反馈...")
                final_response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    stream=False
                )
                
                raw_text = final_response.choices[0].message.content
                return self._mental_interceptor(raw_text, tool_execution_summary)
            
            else:
                return self._mental_interceptor(response_msg.content)

        except Exception as e:
            print(f"❌ LLM 致命错误: {e}")
            traceback.print_exc()
            return "我突然有点恍惚，刚才说到哪了？"