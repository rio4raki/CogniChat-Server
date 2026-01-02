import os
import sys
import chromadb

# 将项目根目录添加到 Python 路径，以便导入 config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config

def view_vector_database_content():
    """
    连接到 ChromaDB，查看 Collection 中所有可读的文档内容和元数据。
    """
    db_path = Config.CHROMA_DB_PATH
    collection_name = "chat_history" 
    
    print("-" * 50)
    print("🧠 向量数据库内容查看工具 (Memory Viewer)")
    print(f"数据库路径: {db_path}")
    print(f"集合名称: {collection_name}")
    print("-" * 50)

    try:
        # 1. 初始化 ChromaDB 客户端
        chroma_client = chromadb.PersistentClient(path=db_path)
        
        # 2. 获取 Collection
        try:
            collection = chroma_client.get_collection(name=collection_name)
        except Exception:
            print(f"❌ 错误：集合 '{collection_name}' 不存在或无法连接。请先运行应用或重置脚本。")
            return

        # 3. 获取 Collection 的总数量
        count = collection.count()
        if count == 0:
            print("ℹ️ 向量数据库中没有任何条目（0 条记忆）。")
            return
            
        print(f"✅ 成功连接。集合中共有 {count} 条记忆。")
        print("-" * 50)

        # 4. 查询所有数据 (使用 get 方法，不进行相似度搜索)
        # limit/offset 可用于分页，这里获取全部
        results = collection.get(
            ids=None, # 获取所有 ID
            include=['documents', 'metadatas'] # 确保包含文档内容和元数据
        )

        documents = results.get('documents', [])
        metadatas = results.get('metadatas', [])
        ids = results.get('ids', [])

        # 5. 格式化并打印结果
        for i in range(len(documents)):
            doc = documents[i]
            meta = metadatas[i]
            item_id = ids[i]
            
            # 从元数据中获取角色（role）
            role = meta.get('role', 'unknown')

            print(f"--- 条目 {i + 1}/{count} --- (ID: {item_id[:8]}...)")
            print(f"角色/来源: {role.upper()}")
            print(f"** 文档内容 **: {doc}")
            print("-" * 20)

        print("-" * 50)
        print("查看完毕。")

    except Exception as e:
        print(f"\n❌ 严重错误：查看数据库失败。请检查 ChromaDB 路径和权限。")
        print(f"详细错误: {e}")

if __name__ == "__main__":
    view_vector_database_content()