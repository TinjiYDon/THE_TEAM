# 系统架构图草稿

```mermaid
graph TD
    subgraph Client[终端用户]
        Web[Web 浏览器]
        Mobile[移动设备]
    end

    subgraph Frontend[前端应用 (React + Ant Design)]
        UI[SPA 界面]
        State[状态管理 Hooks]
        APIClient[API 请求封装]
    end

    subgraph Backend[后端服务 (FastAPI)]
        Router[REST 路由层]
        Service[业务服务层]
        AIModule[AI 服务模块]
        Billing[账单/预算模块]
        Community[社群与内容模块]
        OCR[发票 OCR 接口]
    end

    subgraph DataLayer[数据层]
        SQLite[(SQLite / PostgreSQL)]
        Models[(SQLAlchemy ORM)]
        Files[(上传文件 / OCR 缓存)]
    end

    subgraph AIStack[AI/数据处理]
        Cleaning[数据清洗]
        Profile[用户画像]
        Recommend[推荐引擎]
        Analysis[消费分析与洞察]
        Forecast[趋势预测]
    end

    subgraph Integrations[外部/可选集成]
        PaymentAPI[第三方支付接口]
        Notification[通知服务 (Mail/SMS)]
        Storage[对象存储]
    end

    Web --> UI
    Mobile --> UI
    UI --> APIClient
    APIClient -->|HTTPS/JSON| Router
    Router --> Service
    Service --> Billing
    Service --> Community
    Service --> OCR
    Service --> AIModule

    AIModule --> Cleaning
    AIModule --> Profile
    AIModule --> Recommend
    AIModule --> Analysis
    AIModule --> Forecast

    Billing --> SQLite
    Community --> SQLite
    OCR --> Files
    AIModule --> Models
    Models --> SQLite

    Cleaning --> Models
    Profile --> Models
    Recommend --> Models
    Analysis --> Models
    Forecast --> Models

    Service --> Notification
    Service --> Storage
    Service --> PaymentAPI
```

> 说明：
> - **客户端**：浏览器或移动端访问 React 前端。
> - **前端层**：单页应用负责界面渲染、状态管理、调用后端 API。
> - **后端层**：FastAPI 提供路由、业务服务，调用账单、社群、OCR 与 AI 模块。
> - **数据层**：SQLite/PostgreSQL 存储核心数据，SQLAlchemy 管理模型，文件系统存储上传/OCR 缓存。
> - **AI/数据处理**：数据清洗、用户画像、推荐、分析、预测等子模块。
> - **外部集成**：可扩展第三方支付、通知、存储等服务。

