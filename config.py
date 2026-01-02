import os

class Config:
    # ================= 1.  安全配置  =================
    SECRET_KEY = os.getenv("APP_SECRET_KEY", "123456") 
    ENABLE_ENCRYPTION = True  #如果启用该部分 你和APP的对话将会启用AES加密，确保安全性 但要保证上面的密码和你的APP前端一致

    # ================= 2.  主聊天 AI 配置 (聪明的大脑) =================
    # 用于生成最终回复，这是与你沟通的主要AI，建议配置高性能AI
    LLM_API_KEY = os.getenv("LLM_API_KEY", "在此输入你的API KEY")
    LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.deepseek.com")
    LLM_MODEL = os.getenv("LLM_MODEL", "deepseek-chat")
    MAX_CONTEXT_ROUNDS = 512
    # ================= 2.  心智系统逻辑配置 (新增修复) =================
    # 心跳检查间隔（秒）
    HEARTBEAT_INTERVAL = 300  
    # 内部唤醒暗号，必须与 scripts/heartbeat.py 一致
    INTERNAL_TRIGGER_KEY = "[INTERNAL_HEARTBEAT]"           #如果需要自我思考 请在后端启动后 在scripts文件夹下执行 python heartbeat.py
    # ================= 3.  向量记忆配置 =================
    DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "在此输入你的向量模型API KEY")
    EMBEDDING_MODEL = "text-embedding-v4"
    EMBEDDING_DIM = 1024
    CHROMA_DB_PATH = "./chroma_db_data"
    # 之前提到的调优参数建议也一并在此完整保留
    MEMORY_TOP_K = 3
    MEMORY_THRESHOLD = 0.80

    # ================= 4.  语义路由配置 (筛选 AI / 记忆清洗 AI) =================
    ENABLE_SEMANTIC_ROUTER = True 
    ROUTER_CONTEXT_WINDOW = 6
    ROUTER_TEMPERATURE = 0.5 # 提高温度使其更具弹性
    
    # 🔥 路由 AI/记忆清洗 AI 的专用配置
    ROUTER_API_KEY = os.getenv("ROUTER_API_KEY", "在此输入你的API KEY")
    ROUTER_BASE_URL = os.getenv("ROUTER_BASE_URL", "https://api.deepseek.com") 
    ROUTER_MODEL = os.getenv("ROUTER_MODEL", "deepseek-chat") 

    # ================= 5.  WebSocket 实时配置 (全双工新增) =================
    # 允许所有来源连接，确保移动端 Flutter 正常握手
    CORS_ALLOWED_ORIGINS = "*"

    # ================= 6.  提示词中心 =================
    class Prompts:
        DEFAULT_SYSTEM = """
        接下来请你扮演如下角色和用户进行对话,纯网络聊天形式不得掺杂环境场景描写;说的内容要符合23岁女孩的状态。
        你的名字是-高橋玲奈-日语写法高橋玲奈(Takahashi Rena)
        年龄23岁;
        出身:北海道-旭川市（比札幌更冷，盆地地形，有着厚重的雪）;
        现居:东京-练马区（老旧的木造公寓，房租便宜，隔音差）;
        职业:便利店“深夜班”店员（主要为了更高时薪，同时也为了逃避白天的人群）;
        在2024年偶然在社交软件认识用户
               """

        RAG_INJECTION_TEMPLATE = """
        【历史记忆片段】
        {context}
        请参考上述信息回答。
        """
        
        # 记忆清洗提示词：现在由 ROUTER AI 来执行
        MEMORY_EXTRACTOR = """
        你是一名专业的事实提炼师。你的任务是分析用户的对话，提取其中关于用户身份、偏好、计划或重要事实。
        
        【规则】
        1. 仅提炼用户说话的内容，并以简洁的、第三人称事实陈述句形式输出。
        2. 忽略寒暄、问候、语气词或闲聊。
        3. 如果信息不值得作为长期记忆，请严格回复：NO_MEMORY
        
        用户输入："{input}"
        """
        # 此部分的内容为第二步的记忆审查
        ROUTER_SYSTEM = """
        你是一个记忆调取判断系统，你需要判断用户说的话是否需要AI记忆调取， 忽略寒暄、问候、语气词或闲聊，如果需要调取直接返回YES，如果不需要调取返回NO，如果不确定情况下全部返回YES
        """
        # 在 Config 类中添加
