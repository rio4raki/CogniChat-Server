import datetime
from .base import BaseTool

class GetServerTimeTool(BaseTool):
    @property
    def name(self):
        return "get_server_time"

    @property
    def description(self):
        return "获取服务器当前的准确时间。当用户询问'几点了'或'现在时间'时使用。"

    @property
    def parameters(self):
        return {"type": "object", "properties": {}, "required": []}

    def execute(self, **kwargs):
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"当前服务器时间是: {now}"

class NotifyUserTool(BaseTool):
    @property
    def name(self):
        return "push_message_to_user"

    @property
    def description(self):
        return "【主动联系专用】当你经过自省思考，强烈想要打破沉默、主动发消息给用户时使用。此工具会将你的话直接推送到用户的手机屏幕。"

    @property
    def parameters(self):
        return {
            "type": "object",
            "properties": {
                "content": {
                    "type": "string", 
                    "description": "你想对用户说的话，字数不宜过多，要自然、像真实微信聊天。"
                }
            },
            "required": ["content"]
        }

    def execute(self, content, **kwargs):
        # 返回带有特殊标识的字符串，app.py 会拦截它并触发 Socket 发送
        return f"[INTERNAL_PUSH] {content}"