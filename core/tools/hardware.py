from core.tools.base import BaseTool
from core.hardware.massager import massager

class ControlMassagerTool(BaseTool):
    name = "control_massager"
    description = (
        "控制物理震动按摩器。该设备具备专业的按摩节奏程序。"
        "当用户需要放松时，请根据情境选择合适的阶段模式。"
        "调用后会返回触觉反馈描述。"
    )
    parameters = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["start", "stop", "adjust"],
                "description": "操作类型：start(启动/切换), stop(停止), adjust(调整力度)"
            },
            "mode": {
                "type": "string",
                "enum": ["stage1", "stage2", "stage3", "stage4", "full"],
                "description": (
                    "按摩模式："
                    "stage1 (预热呼吸 ); "
                    "stage2 (深层指压); "
                    "stage3 (波浪推拿 - 适合极度疲劳); "
                    "stage4 (舒缓收尾 - 适合睡前); "
                    "full (10分钟完整理疗流程)"
                )
            },
            "intensity": {
                "type": "number",
                "description": "全局力度系数，默认1.0。若用户觉得太重可调为0.8，太轻可调为1.2。"
            }
        },
        "required": ["action"]
    }

    def execute(self, action, mode="stage1", intensity=1.0):
        if action == "stop":
            msg = massager.set_vibration("stop")
            return "[触觉反馈] 按摩器已停止。"
        
        else:
            status_msg = massager.set_vibration(mode, intensity)
            
            # 返回给 AI 的感官描述
            feedback = ""
            if mode == "stage1":
                feedback = "手柄正在进行轻柔的呼吸式震动，节奏舒缓。"
            elif mode == "stage2":
                feedback = "手柄正在模拟深层指压，有明显的敲击感。"
            elif mode == "stage3":
                feedback = "手柄产生像海浪一样的波动感，起伏很大。"
            elif mode == "stage4":
                feedback = "手柄进入微弱的收尾震动，非常平滑。"
            elif mode == "full":
                feedback = "已启动长程理疗模式，震动节奏将随时间变化。"
            
            return f"{status_msg}。物理感知：{feedback}"