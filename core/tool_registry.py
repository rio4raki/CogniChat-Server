from core.tools.base import BaseTool
from core.tools.builtins import GetServerTimeTool, NotifyUserTool
# 导入新的按摩器工具
from core.tools.hardware import ControlMassagerTool

class ToolRegistry:
    def __init__(self):
        self._tools = {}
        # 注册基础工具
        self.register(GetServerTimeTool())
        self.register(NotifyUserTool())
        # 注册硬件工具
        self.register(ControlMassagerTool())

    def register(self, tool: BaseTool):
        if tool.name in self._tools:
            print(f"⚠️ 工具 {tool.name} 已存在，将被覆盖")
        self._tools[tool.name] = tool
        print(f"🛠️ [工具层] 已加载工具: {tool.name}")

    def get_tool(self, name):
        return self._tools.get(name)

    def get_openai_tools(self):
        return [tool.to_openai_schema() for tool in self._tools.values()]