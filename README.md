<div align="center">
  <a href="./README.md">简体中文</a> | <a href="./README_JP.md">日本語</a>
</div>

<div align="center">
  
  #  CogniChat Server
  
  **赋予人工智能真实的“心跳”与“无限记忆”**
  
  [![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
  [![Architecture](https://img.shields.io/badge/Architecture-Event--Driven-orange?style=for-the-badge)](https://github.com/rio4raki/CogniChat-Server)
  [![Security](https://img.shields.io/badge/Security-E2E%20Encryption-green?style=for-the-badge)](https://github.com/rio4raki/CogniChat-Server)
  [![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)](LICENSE)

  [设计哲学](#-设计哲学-philosophy) • [核心架构](#-五层神经架构-architecture) • [功能特性](#-功能特性-features) • [快速开始](#-快速开始-getting-started)

</div>

---

## 🌌 设计哲学 | Philosophy

现在的 AI 聊天机器人普遍存在三个致命缺陷：**“失忆”、“被动”与“裸奔”**。CogniChat 项目应运而生 旨在打破这些限制，构建一个真正“活着”的数字生命。

| ❌ 传统 LLM 痛点 | ✅ CogniChat 的进化 |
| :--- | :--- |
| **短暂记忆** <br> 上下文窗口有限，它无法长期持有你的记忆。 | **海马体记忆 (Hippocampus)** <br> 基于 RAG 的无限向量记忆库，记住你的一生，而非仅是一次会话。 |
| **被动的奴隶** <br> 你不说话，它永远保持沉默，像个死物。 | **自主心跳 (Heartbeat)** <br> 拥有独立的时间感，会主动思考、自我反思，甚至在你忙碌时主动问候。 |
| **云端裸奔** <br> 聊天记录被云厂商监控，隐私无处遁形。 | **突触协议 (Synapse Protocol)** <br> 业务逻辑与安全彻底解耦，端到端加密，确保只有你拥有密钥。 |

---
## 🧬 发展历程 | Evolution

CogniChat 项目并非一蹴而就的代码堆砌，而是一个逐步“点亮”各个神经中枢的过程：

* **2024.12 - [起源]**
    * 通过长期对SillyTavern等AI聊天服务的追踪研究，虽然短期内实用有新鲜感，但因其没有长期记忆、独立思考，无法做到长久陪伴，决定开始设计CogniChat原型
    * 项目启动。最初它只是一个简单的 Python 应答脚本，局限于API接入的128K上下文。
    * 虽然完成基础 LLM 接入，但这仅仅是“应答机”，而非有灵魂的“智能体”。

* **2025.01 - [雏形]**
    * 参考 SillyTavern 运行机制，引入了**提示词工程**(Prompt Engineering)与**角色卡**系统(Character Card)，AI 开始有了性格。
    * 构建了首个基于 **PyQt5** 的桌面客户端（虽界面简陋，仅能在本地运行）。
    * 2月完成了服务端上云部署，虽然仍局限于 PC 端交互，但“脱离本地、独立存活”的构想开始萌芽。

* **2025.04 - [跨越平台的尝试]**
    * 为了实现“随身携带的ChatAI”的愿景，起初尝试接入微信与 QQ。但面对严苛的内容审查与封闭的插件政策，不得不寻找新的土壤。
    * 通过自学一定的TGBot API后开始转向 Telegram Bot API。这是系统首次习得 **Function Calling (函数调用)** 能力，学会了帮用户查询天气和时间。这也是项目首次引入 **Docker** 容器化部署技术。
    * 虽然成功上线（见早期验证项目 [TelegramBot_AI](https://github.com/rio4raki/TelegramBot_AI)），但受限于跨国网络通信的不稳定性，响应延迟极高。这次实验让我意识到：必须构建一套独立、稳定且加密的通信协议和属于自己的Android App。

* **2025.06 - [瓶颈]**
    * 在了解AI调用函数机制后，开始重心放在AI的函数调用与记忆力提升上。
    * 为了突破上下文限制，开始设计第一代记忆数据库方案——“定期摘要”(Rolling Summary) ，将长对话经过AI大模型压缩后塞回 Prompt提示词内，以达到注意力聚焦。
    * 虽然短暂提升了记忆长度，但是过度的压缩导致记忆细节丢失，AI仍然记不住关键情感细节，效果未达到预期。

* **2025.07 - [试错]**
    * 设计了第二代记忆数据库方案。尝试通过“对话关键词”触发数据库检索，并引入“连带记忆”机制。
    * 对话关键词系统在特定情况下确实状况良好，但是如果遇到长期深层记忆，一次检索后配合连带记忆往往带出大量冗余历史，瞬间挤爆上下文窗口。
    * 过载的记忆数据压缩了 AI 的思考空间，导致“自我意识”反而被淹没，让AI变成只能复读的机器。

* **2025.11 - [解明]**
    * 偶然发现早期的记忆方案其实就是**向量数据库**的原始雏形。意识到真正的突破口在于引入 Embedding 层的**语义判断 (Semantic Judgment)** 能力，而非死板的关键词匹配。
    * 随着编程能力的质变，对AI函数工具调用的的理解不再浮于表面，开始构思基于语义路由的第三代记忆系统。
    * 虽然内心蓝图已定，但受限于繁重的学业压力，项目开发被迫按下暂停键。这段空白期反而让我从架构层面重新审视了系统的合理性。

* **2025.12初 - [重构]**
    * 正式启动后端重写与第三代记忆数据库开发。彻底抛弃了单体 AI 蛮干的模式。
    * 创新性地提出了“多层级 AI 协作”的构想。将系统拆解为路由层、思考层与执行层，让不同的模型各司其职，这直接奠定了 CogniChat 现今“五层神经架构”的基石。
    * 自此，CogniChat 的后端构建基本完成。

* **2025.12(Late) - [新生]**
    * 补全 AI 的最后一块拼图，从零构建了基于 **Flutter** 的移动端应用。这标志着项目正式进化为 **CogniChat V3.0**——一个完整的“大脑+躯体”生态系统。
    * 完成了后端与 App 的深度适配。实现了**端到端加密通信**与**云端历史同步**，确保了数据像血液一样在安全的管道中流转。
    * 引入了核心的 **Heartbeat (心跳思考机制)**。AI 不再是推一下动一下的死物，它开始学会“自省”——思考自己的所作所为，并在合适的时机主动联系用户。
    * 虽然目前的 V3.0 版本仍有待完善，但随着硬件感知（电量、震动控制）接口的预留，它已经为未来“虚拟人”打破次元壁、真正介入用户生活留下了无限的想象空间。

---
## 🧠 工作流程演示 | Workflow Demo

> 深入观察 CogniChat 的“思维链”与“记忆体”是如何协同工作的。

### 场景一：日常对话与自我思考 (Routine Chat & Self-Reflection)

左侧前端的每一次输入，都会触发后端（右侧）一系列复杂的“思维链”反应，包括**心跳自省**、**语义路由判断**、**工具调用**以及**内心独白**生成。

| 📱 前端视角 (Client View) | 🧠 后端视角 (Server View) |
| :---: | :---: |
| <img src="./assets/client_chat_flow.jpg" width="320" alt="Frontend Chat Flow"> | <img src="./assets/server_chat_flow.png" width="100%" alt="Backend Chat & Thought Process"> |
| *用户发送消息，AI 进行多段式回复* | *后端日志展示：心跳触发 -> 内心独白 -> 路由判断 -> 工具调用* |

### 场景二：记忆的形成与反馈 (Memory Formation & Feedback)

当用户发出明确的记忆指令时，后端的**记忆层 (Memory Layer)** 会被激活，自动提炼关键事实并存入向量数据库。前端会实时收到“已存入记忆”的反馈标记。

| 📱 前端视角 (Client View) | 🧠 后端视角 (Server View) |
| :---: | :---: |
| <img src="./assets/client_memory_flow.jpg" width="320" alt="Frontend Memory Feedback"> | <img src="./assets/server_memory_flow.png" width="100%" alt="Backend Memory Extraction"> |
| *用户指令：“请记住我喜欢吃寿喜烧！”<br>系统反馈：“已存入记忆”标签* | *后端日志展示：识别记忆指令 -> 提炼事实：“用户喜欢吃寿喜烧” -> 写入向量库* |

---
## ✨ 功能特性 | Features

我们提供了一整套完善的工具链，涵盖安全、记忆、扩展性与硬件交互：

- [x] **🛡️ 核心安全**
    - [x] **AES 端到端加密**: 聊天内容全程高强度加密，密钥仅由用户持有。
    - [x] **云端记录同步**: 支持多端加密漫游，无缝切换设备。

- [x] **🧠 记忆与意识**
    - [x] **自动记忆提取/录入**: 智能分析对话流，自动提炼关键事实存入长期记忆库。
    - [x] **自定义记忆管理**: 支持“上帝模式”，可手动植入或精准删除特定记忆片段。
    - [x] **自我意识触发**: 基于心跳 (Heartbeat) 的主动思考与反思机制。
    - [x] **聊天自动分片**: 智能切分长文本，优化上下文窗口 (Context Window) 利用率。

- [x] **🛠️ 扩展与工具**
    - [x] **函数工具调用**: AI 可自主决策调用外部函数（如联网搜索、系统指令）。
    - [x] **高可扩展性**: 模块化设计，支持用户编写 Python 脚本自定义插件。

- [x] **🎮 物理感知**
    - [x] **硬件控制**: 打通虚拟与现实，目前已支持 **XBOX 手柄** 震动反馈控制。

    ---
## 📂 目录结构 | Structure

```text
CogniChat-Server/
├── assets/                 # README 展示用的图片资源
├── chroma_db_data/         # 向量数据库数据文件
├── core/                   # 核心代码库
│   ├── hardware/           # 硬件控制模块
│   │   └── massager.py     # 硬件驱动逻辑
│   ├── tools/              # 工具函数集
│   │   ├── __init__.py
│   │   ├── base.py         # 工具基类
│   │   ├── builtins.py     # 通用工具
│   │   └── hardware.py     # 硬件工具封装
│   ├── __init__.py
│   ├── context_manager.py  # 上下文管理器
│   ├── gateway.py          # 网关接口层
│   ├── llm.py              # 大模型调用层
│   ├── logger.py           # 日志记录模块
│   ├── memory.py           # 记忆层 (RAG核心)
│   ├── message_logger.py   # 消息日志处理
│   ├── prompt_engine.py    # 提示词引擎
│   ├── router.py           # 语义路由
│   ├── security.py         # 安全加密层
│   └── tool_registry.py    # 工具注册表
├── plugins/                # 插件扩展
│   └── message_splitter.py # 消息分片插件
├── scripts/                # 脚本文件
│   ├── heartbeat.py        # 心跳守护进程
│   ├── inject_memory.py    # 记忆注入脚本
│   ├── reset_vector_db.py  # 重置向量库脚本
│   └── view_memory.py      # 查看记忆脚本
├── tests/                  # 测试用例
│   ├── test_llm.py
│   ├── test_memory.py
│   ├── test_security.py
│   └── test_tools.py
├── .gitignore              # Git 忽略配置
├── app.py                  # 主程序入口
├── chat_database.json      # 聊天记录数据库
├── config.py               # 项目配置文件
└── inner_monologue.json    # 内心独白日志
```
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
