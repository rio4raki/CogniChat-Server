import os
import sys
import chromadb

# 🔥 核心修改：将项目根目录添加到 Python 路径中
# 这允许脚本从父目录导入 config 模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 现在可以正常导入 config 了
from config import Config

def reset_vector_database():
    """
    连接到 ChromaDB 并永久删除指定的 Collection (向量集合)
    """
    db_path = Config.CHROMA_DB_PATH
    collection_name = "chat_history" # 你的 MemoryService 中使用的名称

    print("-" * 50)
    print(f"警告: 正在尝试重置向量数据库...")
    print(f"数据库路径: {db_path}")
    print(f"集合名称: {collection_name}")
    print("-" * 50)

    # 再次确认，防止误操作
    confirm = input("请确认是否要永久删除所有向量数据？(输入 'YES' 继续): ").strip()
    
    if confirm.upper() != 'YES':
        print("操作已取消。")
        return

    try:
        # 1. 初始化 ChromaDB 客户端 (持久化模式)
        chroma_client = chromadb.PersistentClient(path=db_path)
        
        # 2. 检查集合是否存在
        all_collections = chroma_client.list_collections()
        
        if collection_name in [c.name for c in all_collections]:
            # 3. 删除集合
            chroma_client.delete_collection(name=collection_name)
            
            # 4. 重新创建一个空的集合 (可选，但推荐)
            chroma_client.get_or_create_collection(name=collection_name)

            print("\n成功！向量数据库集合已重置。")
            print(f"'{collection_name}' 集合已被删除并重新创建。")
        else:
            print("\n提示: 指定的向量集合不存在，无需删除。")

    except Exception as e:
        print(f"\n错误：重置数据库失败。请检查 ChromaDB 路径和权限。")
        print(f"详细错误: {e}")

if __name__ == "__main__":
    if not os.path.exists('config.py'):
        # 这个检查可能因为路径修改而失效，但我们保持主逻辑不变
        pass 
    
    reset_vector_database()