import datetime
import os
from colorama import Fore, Style, init

# 初始化 colorama
init(autoreset=True)

class FlowLogger:
    """
    全链路彩色日志记录器 (恢复图标版)
    """
    
    @staticmethod
    def _timestamp():
        return datetime.datetime.now().strftime("%H:%M:%S")

    @staticmethod
    def info(stage, message):
        """普通信息 (白色)"""
        print(f"[{FlowLogger._timestamp()}] {Style.BRIGHT}[INFO] {Style.NORMAL}[{stage}] {message}", flush=True)

    @staticmethod
    def receive(message):
        """接收消息 (蓝色)"""
        print(f"{Fore.BLUE}[{FlowLogger._timestamp()}] [RECV] 📥 {message}{Style.RESET_ALL}", flush=True)

    @staticmethod
    def security(action, message):
        """安全层操作 (紫色)"""
        print(f"{Fore.MAGENTA}[{FlowLogger._timestamp()}] [SEC] 🛡️ {action}: {message}{Style.RESET_ALL}", flush=True)

    @staticmethod
    def router(decision, reason=""):
        """路由决策 (黄色)"""
        print(f"{Fore.YELLOW}[{FlowLogger._timestamp()}] [ROUTER] 🚦 {decision} {reason}{Style.RESET_ALL}", flush=True)

    @staticmethod
    def memory(action, content):
        """记忆操作 (青色)"""
        print(f"{Fore.CYAN}[{FlowLogger._timestamp()}] [MEM] 🧠 {action}: {content}{Style.RESET_ALL}", flush=True)

    @staticmethod
    def brain(action, content=""):
        """大脑思考 (绿色)"""
        print(f"{Fore.GREEN}[{FlowLogger._timestamp()}] [BRAIN] 🤖 {action} {content}{Style.RESET_ALL}", flush=True)
    
    @staticmethod
    def tool(name, args):
        """工具调用 (粉色)"""
        print(f"{Fore.LIGHTMAGENTA_EX}[{FlowLogger._timestamp()}] [TOOL] 🛠️ 调用: {name} 参数: {args}{Style.RESET_ALL}", flush=True)

    @staticmethod
    def error(stage, message):
        """错误 (红色)"""
        print(f"{Fore.RED}{Style.BRIGHT}[{FlowLogger._timestamp()}] [ERROR] ❌ [{stage}] {message}{Style.RESET_ALL}", flush=True)