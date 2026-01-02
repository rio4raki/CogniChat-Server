import json
import os
import time

class MessageLogger:
    def __init__(self, db_file='chat_database.json'):
        self.db_file = db_file

    def _load_history(self):
        if not os.path.exists(self.db_file):
            return []
        try:
            with open(self.db_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []

    def save_message(self, role, content, timestamp=None):
        """
        保存单条消息到 JSON
        :param role: 'user' 或 'ai'
        :param content: 消息内容
        :param timestamp: 时间戳 (如果不传则使用当前时间)
        """
        if timestamp is None:
            timestamp = time.time()
            
        history = self._load_history()
        history.append({
            "role": role,
            "text": content,
            "time": timestamp
        })
        
        # 写入文件
        with open(self.db_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

    def get_all_history(self):
        return self._load_history()

    def clear_history(self):
        with open(self.db_file, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)