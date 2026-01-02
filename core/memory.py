import uuid
import chromadb
from openai import OpenAI
from config import Config

class MemoryService:
    # 🔥 更改参数名称，接受专门的清洗客户端
    def __init__(self, cleaning_llm_client=None): 
        """
        初始化记忆服务
        :param cleaning_llm_client: 用于记忆清洗的 LLM 客户端实例 (现在使用 Router AI)
        """
        # 1. 初始化百炼 (DashScope) 客户端 - 用于 Embedding
        self.ai_client = OpenAI(
            api_key=Config.DASHSCOPE_API_KEY,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )

        # 2. 初始化 ChromaDB (持久化存储)
        self.chroma_client = chromadb.PersistentClient(path=Config.CHROMA_DB_PATH)
        
        # 3. 获取或创建集合
        self.collection = self.chroma_client.get_or_create_collection(name="chat_history")
        
        # 4. 保存 LLM 客户端用于记忆清洗
        self.cleaning_llm_client = cleaning_llm_client # 🔥 保存 Router 客户端

    def _get_embedding(self, text):
        """
        私有方法：将文本转化为向量
        """
        try:
            completion = self.ai_client.embeddings.create(
                model=Config.EMBEDDING_MODEL,
                input=text,
                dimensions=Config.EMBEDDING_DIM,
                encoding_format="float"
            )
            return completion.data[0].embedding
        except Exception as e:
            print(f"Embedding failed: {e}")
            return None

    def add_memory(self, text, role="user"):
        """
        清洗文本，生成向量并存入数据库。
        返回 True 表示成功存入，False 表示忽略。
        """
        final_text_to_save = text
        is_saved = False # 默认未存入

        # === 🌟 智能清洗逻辑: 使用 Router LLM 判断记忆价值 ===
        if self.cleaning_llm_client and role == "user": 
            try:
                # 从 Config 获取清洗提示词
                prompt = Config.Prompts.MEMORY_EXTRACTOR.format(input=text)
                
                # 调用 Router LLM
                response = self.cleaning_llm_client.chat.completions.create(
                    model=Config.ROUTER_MODEL,  
                    messages=[{"role": "user", "content": prompt}],
                    temperature=Config.ROUTER_TEMPERATURE 
                )
                result = response.choices[0].message.content.strip()

                # 如果 AI 说没价值，直接跳过
                if "NO_MEMORY" in result:
                    print(f"🗑️ [记忆层] 忽略无效信息: {text}")
                    return False 
                
                # 如果有价值，存储 AI 提炼后的事实
                final_text_to_save = result
                print(f"✨ [记忆层] 提炼事实: {final_text_to_save}")

            except Exception as e:
                print(f"⚠️ 记忆清洗失败，降级为直接存储: {e}")
                return False 
        # ========================================

        vector = self._get_embedding(final_text_to_save)
        if vector:
            self.collection.add(
                documents=[final_text_to_save],
                embeddings=[vector],
                metadatas=[{"role": role}],
                ids=[str(uuid.uuid4())]
            )
            print(f"💾 [记忆层] 已写入库: {final_text_to_save[:20]}...")
            is_saved = True 
            
        return is_saved

    def search_memory(self, query_text, top_k=3, threshold=0.35):
        """
        检索记忆并根据相似度阈值过滤
        :param query_text: 用户输入的查询文本
        :param top_k: 检索的最邻近条目数
        :param threshold: 距离阈值。ChromaDB默认使用L2距离，值越小越相似。
                          建议范围 0.3 - 0.4。
        """
        vector = self._get_embedding(query_text)
        if not vector:
            return []

        # 🔥 include 必须包含 'distances'
        results = self.collection.query(
            query_embeddings=[vector],
            n_results=top_k,
            include=['documents', 'distances'] 
        )

        # 提取结果列表
        documents = results.get('documents', [])[0] if results.get('documents') else []
        distances = results.get('distances', [])[0] if results.get('distances') else []

        # 🔥 相似度过滤逻辑
        filtered_docs = []
        for doc, dist in zip(documents, distances):
            if dist <= threshold:
                filtered_docs.append(doc)
                print(f"✅ [记忆检索] 匹配成功 (距离: {dist:.4f} <= 阈值: {threshold})")
            else:
                # 距离过大，判定为无关干扰信息
                print(f"📡 [记忆检索] 过滤无关条目 (距离: {dist:.4f} > 阈值: {threshold}) 内容: {doc[:20]}...")

        return filtered_docs