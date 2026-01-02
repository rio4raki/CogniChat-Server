import pygame
import threading
import time
import math

# ================= 移植自 xxx.py 的核心节奏数据 =================

# 1. 预热单元 (Stage 1)
base_warmup = [
    (0.2, 0.0, 0.5), (0.0, 0.0, 1.0), # 呼吸
    (0.2, 0.0, 0.5), (0.0, 0.0, 1.0),
    (0.3, 0.0, 0.5), (0.0, 0.0, 1.5), # 停顿
]

# 2. 深层按摩单元 (Stage 2)
base_deep = [
    (0.4, 0.0, 0.3), (0.0, 0.0, 0.2), # 咚...
    (0.0, 0.0, 1.5), 
    (0.4, 0.0, 0.3), (0.0, 0.0, 0.1), # 咚-咚...
    (0.5, 0.0, 0.3), (0.0, 0.0, 2.0), 
    (0.3, 0.0, 1.0), (0.0, 0.2, 1.0), (0.0, 0.0, 1.0), # 蠕动
]

# 3. 波动单元 (Stage 3)
base_wave = [
    (0.3, 0.1, 2.0), (0.5, 0.1, 2.0), (0.3, 0.1, 2.0), (0.0, 0.0, 3.0),
    (0.4, 0.0, 2.0), (0.6, 0.0, 1.5), (0.3, 0.0, 2.0), (0.0, 0.0, 4.0),
]

# 4. 收尾单元 (Stage 4)
base_cooldown = [
    (0.3, 0.0, 2.0), (0.0, 0.0, 2.0), (0.1, 0.0, 3.0), (0.0, 0.0, 1.0),
]

# 完整 10分钟流程 (Full)
PATTERN_FULL = (base_warmup * 20) + (base_deep * 25) + (base_wave * 10) + (base_cooldown * 3)

# ===========================================================

class MassagerDriver:
    _instance = None
    _lock = threading.Lock()

    # 模式映射表
    ROUTINES = {
        "stage1": base_warmup,   # 预热呼吸
        "stage2": base_deep,     # 深层指压
        "stage3": base_wave,     # 波浪推拿
        "stage4": base_cooldown, # 舒缓收尾
        "full":   PATTERN_FULL   # 完整流程
    }

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(MassagerDriver, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized: return
        self._initialized = True
        
        self.joystick = None
        
        # 播放器状态
        self.current_routine = None  # 当前播放的列表
        self.pattern_index = 0       # 当前播放到第几步
        self.step_start_time = 0     # 当前步开始的时间戳
        self.intensity_scale = 1.0   # 全局力度缩放
        
        pygame.init()
        pygame.joystick.init()

        self.thread = threading.Thread(target=self._daemon_loop, daemon=True)
        self.thread.start()

    def _try_connect(self):
        try:
            pygame.event.pump()
            if pygame.joystick.get_count() > 0:
                self.joystick = pygame.joystick.Joystick(0)
                self.joystick.init()
                print(f"🎮 [硬件层] 已连接手柄: {self.joystick.get_name()}")
                return True
            return False
        except Exception as e:
            print(f"⚠️ [硬件层] 连接尝试失败: {e}")
            return False

    def set_vibration(self, mode_name="stop", intensity_modifier=1.0):
        """AI 调用的接口"""
        if mode_name == "stop":
            self.current_routine = None
            self.stop()
            return "按摩器已停止。"

        if mode_name in self.ROUTINES:
            # 切换新模式
            self.current_routine = self.ROUTINES[mode_name]
            self.pattern_index = 0
            self.step_start_time = time.time()
            self.intensity_scale = intensity_modifier
            return f"震动方案 [{mode_name}] 已启动 (强度系数: {intensity_modifier})"
        
        return "未知模式"

    def stop(self):
        if self.joystick:
            self.joystick.stop_rumble()

    def _daemon_loop(self):
        """高级序列播放器循环"""
        print("🎮 [硬件层] 节奏播放器已启动")
        
        while True:
            pygame.event.pump()

            # 1. 连接保活
            if not self.joystick:
                if self._try_connect():
                    time.sleep(1)
                else:
                    time.sleep(2)
                    continue
            
            # 2. 序列播放逻辑
            if self.current_routine:
                current_time = time.time()
                
                # 越界保护
                if self.pattern_index >= len(self.current_routine):
                    self.pattern_index = 0
                
                # 获取当前步的数据 (左力度, 右力度, 持续时间)
                base_l, base_r, duration = self.current_routine[self.pattern_index]
                
                # 应用 AI 指定的力度缩放
                final_l = min(base_l * self.intensity_scale, 1.0)
                final_r = min(base_r * self.intensity_scale, 1.0)
                
                # 执行震动
                try:
                    if final_l > 0.05 or final_r > 0.05:
                        # 持续时间给稍微多一点(200ms)，覆盖循环间隙，防止断触
                        self.joystick.rumble(final_l, final_r, 200)
                    else:
                        self.joystick.stop_rumble()
                except:
                    self.joystick = None

                # 时间步进检查
                if current_time - self.step_start_time >= duration:
                    self.pattern_index += 1
                    self.step_start_time = current_time
                    
                    # 循环播放
                    if self.pattern_index >= len(self.current_routine):
                        self.pattern_index = 0
                        #如果是Full模式，也许可以打印个日志，不过这里保持静默循环即可
            
            else:
                # 待机状态
                if self.joystick: self.joystick.stop_rumble()
            
            # 3. 刷新率 (与 xxx.py 保持一致的 50Hz 左右，保证节奏精确)
            time.sleep(0.02)

# 全局单例
massager = MassagerDriver()