<div align="center">
  
  # 🧠 CogniChat Server
  
  **赋予人工智能真实的“心跳”与“无限记忆”**
  
  [![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
  [![Architecture](https://img.shields.io/badge/Architecture-Event--Driven-orange?style=for-the-badge)](https://github.com/rio4raki/CogniChat-Server)
  [![Security](https://img.shields.io/badge/Security-E2E%20Encryption-green?style=for-the-badge)](https://github.com/rio4raki/CogniChat-Server)
  [![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)](LICENSE)

  [设计哲学](#-设计哲学-philosophy) • [核心架构](#-五层神经架构-architecture) • [功能特性](#-功能特性-features) • [快速开始](#-快速开始-getting-started)

</div>

---

## 🌌 设计哲学 | Philosophy

现在的 AI 聊天机器人普遍存在三个致命缺陷：**“失忆”、“被动”与“裸奔”**。CogniChat 旨在打破这些限制，构建一个真正“活着”的数字生命。

| ❌ 传统 LLM 痛点 | ✅ CogniChat 的进化 |
| :--- | :--- |
| **金鱼的记忆** <br> 上下文窗口有限，聊久了就忘记你的名字。 | **海马体记忆 (Hippocampus)** <br> 基于 RAG 的无限向量记忆库，记住你的一生，而非仅是一次会话。 |
| **被动的奴隶** <br> 你不说话，它永远保持沉默，像个死物。 | **自主心跳 (Heartbeat)** <br> 拥有独立的时间感，会主动思考、自我反思，甚至在你忙碌时主动问候。 |
| **云端裸奔** <br> 聊天记录被云厂商监控，隐私无处遁形。 | **突触协议 (Synapse Protocol)** <br> 业务逻辑与安全彻底解耦，端到端加密，确保只有你拥有密钥。 |

---

## 🏗️ 五层神经架构 | Architecture

CogniChat 模拟了生物大脑的运作机制，将后端划分为五个精密协作的逻辑层级：

```mermaid
graph TD
    %% 样式定义
    classDef client fill:#e1f5fe,stroke:#01579b,stroke-width:2px;
    classDef security fill:#fff3e0,stroke:#ff6f00,stroke-width:2px;
    classDef brain fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px;
    classDef memory fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px;
    classDef tools fill:#fff8e1,stroke:#fbc02d,stroke-width:2px;
    classDef infra fill:#eceff1,stroke:#455a64,stroke-width:2px;

    User((用户/客户端)):::client <==>|HTTP/WebSocket + AES| Gateway[🛡️ 1. 接入与安全层]:::security

    subgraph Server [CogniChat Server - 数字大脑]
        Gateway -->|解密后明文| Router{语义路由}
        
        subgraph BrainSystem [🤖 3. 核心思考层]
            Router -->|日常对话| Brain[LLM 调度器]:::brain
            Brain <--> PromptEng[提示词引擎]:::brain
        end
        
        subgraph MemorySystem [🧠 2. 记忆增强层]
            Brain <--> Retriever[记忆检索]:::memory
            Retriever <--> VectorDB[(向量数据库)]:::memory
            Router -->|长时记忆归档| Archiver[记忆存储]:::memory
            Archiver --> VectorDB
        end

        subgraph ToolSystem [🛠️ 4. 工具与能力层]
            Brain -->|调用工具| ToolRegistry[工具注册表]:::tools
            ToolRegistry -->|Web搜索/代码执行| ServerTools[服务端执行]:::tools
            ToolRegistry -.->|Synapse指令| ClientAction[客户端静默指令]:::tools
        end
    end

    subgraph Infrastructure [💾 5. 基础设施层]
        VectorDB --- ChromaDB:::infra
        LogDB[(历史记录 SQL)]:::infra
    end

    ClientAction -.->|JSON Protocol| User
