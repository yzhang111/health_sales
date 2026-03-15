# Skills 总览（项目本地）

本文件汇总当前项目 `.agents/skills/` 下全部 skills 的用途概略，按技能名 A-Z 排序。

## 快速用法

在对话里直接点名 skill + 任务即可：

```text
请使用 tdd-workflow skill，帮我为用户登录功能先写测试再实现。
请使用 security-review skill，对我这次改动做一次安全审查。
请使用 market-research skill，做日本健康 SaaS 竞品研究。
```

## 全量技能清单

| # | Skill | 能做什么（概略） |
|---:|---|---|
| 1 | `agent-harness-construction` | 设计和优化 AI Agent 的动作空间、工具定义与观察格式，提高任务完成率。 |
| 2 | `agentic-engineering` | 用代理工程方法做复杂任务拆解、评估优先和成本感知执行。 |
| 3 | `ai-first-engineering` | 建立 AI 优先的工程协作模式，适合高比例 AI 产出的团队。 |
| 4 | `android-clean-architecture` | Android/KMP 的整洁架构实践：分层、依赖边界、仓储与用例设计。 |
| 5 | `api-design` | REST API 设计规范：资源命名、状态码、分页过滤、版本与限流。 |
| 6 | `article-writing` | 长文写作与润色：博客、教程、指南、专栏，强调风格一致和可读性。 |
| 7 | `autonomous-loops` | 自动化代理循环的架构模式，从串行流程到多代理 DAG 编排。 |
| 8 | `backend-patterns` | 后端工程模式：接口设计、数据层优化、服务端结构与稳定性实践。 |
| 9 | `blueprint` | 把目标拆成可执行路线图，适合多阶段、多会话、多 PR 的复杂项目。 |
| 10 | `carrier-relationship-management` | 承运商关系管理：运价谈判、绩效评估、运力分配与合作策略。 |
| 11 | `claude-api` | Claude API 集成实践：消息、流式、工具调用、视觉、缓存与 SDK 使用。 |
| 12 | `clickhouse-io` | ClickHouse 分析型数据库实践：建模、查询优化与高性能分析管道。 |
| 13 | `coding-standards` | 通用编码规范：TS/JS/React/Node 的代码风格、可维护性与一致性。 |
| 14 | `compose-multiplatform-patterns` | Compose Multiplatform 模式：状态管理、导航、主题与跨平台 UI。 |
| 15 | `configure-ecc` | ECC 交互式安装与配置，按项目或全局选择技能、规则并验证结构。 |
| 16 | `content-engine` | 多平台内容引擎：把一个素材改写为 X/LinkedIn/TikTok/YouTube 等版本。 |
| 17 | `content-hash-cache-pattern` | 基于内容哈希的缓存模式，避免重复处理并自动失效更新。 |
| 18 | `continuous-agent-loop` | 持续运行的代理闭环：质量门禁、评估反馈与故障恢复控制。 |
| 19 | `continuous-learning` | 从历史会话中提炼可复用模式，沉淀为可持续复用的技能。 |
| 20 | `continuous-learning-v2` | 带置信度的“本能学习”系统，按项目隔离沉淀为技能/命令/代理。 |
| 21 | `cost-aware-llm-pipeline` | LLM 成本优化流水线：按任务路由模型、预算控制、重试与缓存。 |
| 22 | `cpp-coding-standards` | 现代 C++ 编码标准，强调安全、可读性与长期维护。 |
| 23 | `cpp-testing` | C++ 测试体系：GoogleTest/CTest、覆盖率、稳定性和问题定位。 |
| 24 | `crosspost` | 跨平台分发策略：同一主题按平台特性改写，不做生硬一稿多发。 |
| 25 | `customs-trade-compliance` | 关务与贸易合规：归类、报关、税费优化、禁限清单与合规审查。 |
| 26 | `database-migrations` | 数据库迁移最佳实践：结构变更、数据迁移、回滚与零停机发布。 |
| 27 | `deep-research` | 深度研究工作流：多源检索、证据汇总、引用标注与结论输出。 |
| 28 | `deployment-patterns` | 部署与发布模式：CI/CD、容器化、健康检查、回滚与上线清单。 |
| 29 | `django-patterns` | Django/DRF 架构实践：模型、接口、缓存、中间件与工程组织。 |
| 30 | `django-security` | Django 安全实践：认证授权、CSRF/XSS/SQL 注入防护与安全部署。 |
| 31 | `django-tdd` | Django 测试驱动实践：pytest-django、工厂、Mock、覆盖率与 API 测试。 |
| 32 | `django-verification` | Django 发布前验证闭环：迁移检查、测试覆盖、安全扫描与就绪校验。 |
| 33 | `dmux-workflows` | 多代理并行协作工作流：用 dmux/tmux 管理任务分工与同步。 |
| 34 | `docker-patterns` | Docker/Compose 工程模式：开发环境、网络卷、安全与多服务编排。 |
| 35 | `e2e-testing` | Playwright 端到端测试模式：页面对象、CI 接入、产物与防脆弱策略。 |
| 36 | `energy-procurement` | 能源采购策略：电气合同、费率优化、需求管理与可再生能源评估。 |
| 37 | `enterprise-agent-ops` | 企业级代理运维：可观测性、安全边界、生命周期与运行治理。 |
| 38 | `eval-harness` | 评估驱动开发框架：为代理任务建立可量化评测与持续改进机制。 |
| 39 | `exa-search` | Exa 神经搜索实践：网页/代码/公司信息检索与研究增强。 |
| 40 | `fal-ai-media` | fal.ai 多媒体生成：图像、视频、语音的生成与转换工作流。 |
| 41 | `foundation-models-on-device` | Apple 端侧 FoundationModels 实践：本地推理、工具调用与流式输出。 |
| 42 | `frontend-patterns` | 前端工程模式：React/Next 状态管理、性能优化与 UI 结构实践。 |
| 43 | `frontend-slides` | 高质量 HTML 演示稿制作与 PPT 转网页，含动画与讲演型版式。 |
| 44 | `golang-patterns` | Go 工程实践：结构化项目、并发、错误处理与可维护性。 |
| 45 | `golang-testing` | Go 测试方法：表驱动、子测试、基准、模糊测试与覆盖率。 |
| 46 | `inventory-demand-planning` | 库存与需求计划：预测、安全库存、补货策略与促销影响评估。 |
| 47 | `investor-materials` | 融资材料制作：Pitch Deck、一页纸、财务模型、里程碑与口径统一。 |
| 48 | `investor-outreach` | 投资人沟通文案：冷启动邮件、暖介绍、跟进更新与个性化触达。 |
| 49 | `iterative-retrieval` | 迭代式检索策略：逐轮收敛上下文，提升复杂任务的信息命中率。 |
| 50 | `java-coding-standards` | Java/Spring Boot 编码规范：命名、不可变、异常处理与项目组织。 |
| 51 | `jpa-patterns` | JPA/Hibernate 实践：实体关系、查询优化、事务、索引与分页。 |
| 52 | `kotlin-coroutines-flows` | Kotlin 协程与 Flow 实践：结构化并发、状态流与测试方案。 |
| 53 | `kotlin-exposed-patterns` | JetBrains Exposed ORM 实践：DSL 查询、事务、迁移与仓储封装。 |
| 54 | `kotlin-ktor-patterns` | Ktor 服务端实践：路由、插件、认证、序列化与测试。 |
| 55 | `kotlin-patterns` | Kotlin 工程模式：惯用写法、空安全、DSL 与可维护架构。 |
| 56 | `kotlin-testing` | Kotlin 测试体系：Kotest/MockK、协程测试、性质测试与覆盖率。 |
| 57 | `liquid-glass-design` | iOS Liquid Glass 设计体系：玻璃质感、动态交互与组件化落地。 |
| 58 | `logistics-exception-management` | 物流异常处置：延误/破损/丢失/索赔/争议的流程与判断框架。 |
| 59 | `market-research` | 市场研究与竞品分析：规模测算、情报汇总、结论与行动建议。 |
| 60 | `nanoclaw-repl` | NanoClaw REPL 使用与扩展：会话感知、零依赖命令行工作流。 |
| 61 | `nutrient-document-processing` | 文档处理能力：OCR、提取、转换、脱敏、签署与表单填充。 |
| 62 | `perl-patterns` | 现代 Perl 开发实践：编码风格、模块化、可读性与可维护性。 |
| 63 | `perl-security` | Perl 安全实践：输入校验、安全执行、参数化查询与常见漏洞防护。 |
| 64 | `perl-testing` | Perl 测试模式：Test2/Test::More、Mock、覆盖率与 TDD 流程。 |
| 65 | `plankton-code-quality` | 写时代码质量守护：自动格式化、Lint 与智能修复流程。 |
| 66 | `postgres-patterns` | PostgreSQL 实践：模式设计、索引、查询优化与安全策略。 |
| 67 | `production-scheduling` | 生产排程方法：作业排序、换线优化、瓶颈管理与扰动响应。 |
| 68 | `project-guidelines-example` | 项目级技能模板示例，用于快速搭建团队自己的规范技能。 |
| 69 | `prompt-optimizer` | 提示词优化器：分析意图与缺口，产出更可执行的高质量 Prompt。 |
| 70 | `python-patterns` | Python 工程实践：PEP 8、类型标注、结构设计与可维护开发。 |
| 71 | `python-testing` | Python 测试方法：pytest、夹具、参数化、Mock 与覆盖率。 |
| 72 | `quality-nonconformance` | 质量不合格管理：根因分析、纠正预防、SPC 与审计流程。 |
| 73 | `ralphinho-rfc-pipeline` | RFC 驱动的多代理流水线：DAG 编排、质量门禁与合并队列。 |
| 74 | `regex-vs-llm-structured-text` | 结构化文本解析决策：先正则，复杂低置信场景再引入 LLM。 |
| 75 | `returns-reverse-logistics` | 退货逆向物流：授权、验收分级、退款决策、反欺诈与质保处理。 |
| 76 | `search-first` | 先检索再编码：优先复用现成方案、库和模式，减少重复造轮子。 |
| 77 | `security-review` | 安全审查技能：认证、输入处理、密钥管理、接口与敏感流程检查。 |
| 78 | `security-scan` | 对 Claude 配置进行安全扫描，发现注入风险与配置薄弱点。 |
| 79 | `skill-stocktake` | 技能与命令资产盘点：快速扫描或全量审计，输出质量评估。 |
| 80 | `springboot-patterns` | Spring Boot 后端模式：分层架构、数据访问、缓存、异步与日志。 |
| 81 | `springboot-security` | Spring 安全实践：鉴权、校验、CSRF、密钥、头部与依赖风险控制。 |
| 82 | `springboot-tdd` | Spring Boot 的 TDD 工作流：JUnit/Mockito/MockMvc/Testcontainers。 |
| 83 | `springboot-verification` | Spring Boot 验证闭环：构建、静态检查、测试覆盖与安全扫描。 |
| 84 | `strategic-compact` | 上下文压缩策略：在关键节点手动压缩，保持长任务的连续性。 |
| 85 | `swift-actor-persistence` | Swift Actor 持久化模式：线程安全缓存与文件存储协同。 |
| 86 | `swift-concurrency-6-2` | Swift 6.2 并发实践：默认单线程语义与显式并发模型。 |
| 87 | `swift-protocol-di-testing` | Swift 协议化依赖注入与可测试架构设计。 |
| 88 | `swiftui-patterns` | SwiftUI 架构模式：状态管理、导航、性能与现代 UI 组织。 |
| 89 | `tdd-workflow` | 测试驱动开发流程：先写测试再实现，覆盖单测/集成/E2E。 |
| 90 | `verification-loop` | 通用验证闭环：构建、测试、检查、回归，确保改动可发布。 |
| 91 | `video-editing` | AI 辅助视频编辑全流程：剪辑、增强、配音、合成与发布前优化。 |
| 92 | `videodb` | 视频音频智能处理：采集、理解、检索、转码、编辑与实时告警。 |
| 93 | `visa-doc-translate` | 签证材料翻译：图像文档转英文并生成双语对照 PDF。 |
| 94 | `x-api` | X/Twitter API 集成：发帖、线程、检索、时间线与数据分析。 |

## 说明

- 本文是项目本地技能导览，方便快速选择 skill。
- 想要我按你的场景给“推荐 skill 组合”，直接告诉我目标即可。
