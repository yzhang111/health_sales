# Project-Local ECC Skills

This repository vendors skills from [`affaan-m/everything-claude-code`](https://github.com/affaan-m/everything-claude-code) for use in this project only.

## Scope

- Load skills only from this repository's `.agents/skills/` directory.
- Do not install or rely on `~/.codex/skills` for these imported skills.
- When a task matches one of the imported skills, open that skill's `SKILL.md` and follow it.

## Project Context

- Default business context for this repository is `NUTRITION_SOLUTION_BUSINESS_FLOW.md`.
- For product/process/design tasks, use that document as the baseline context unless the user gives newer instructions.
- If user instructions conflict with the baseline document, follow the latest user instruction.

## Available Skills

The following project-local skills are available under `.agents/skills/<skill-name>/SKILL.md`:

- `agent-harness-construction`
- `agentic-engineering`
- `ai-first-engineering`
- `android-clean-architecture`
- `api-design`
- `article-writing`
- `autonomous-loops`
- `backend-patterns`
- `blueprint`
- `carrier-relationship-management`
- `claude-api`
- `clickhouse-io`
- `coding-standards`
- `compose-multiplatform-patterns`
- `configure-ecc`
- `content-engine`
- `content-hash-cache-pattern`
- `continuous-agent-loop`
- `continuous-learning`
- `continuous-learning-v2`
- `cost-aware-llm-pipeline`
- `cpp-coding-standards`
- `cpp-testing`
- `crosspost`
- `customs-trade-compliance`
- `database-migrations`
- `deep-research`
- `deployment-patterns`
- `django-patterns`
- `django-security`
- `django-tdd`
- `django-verification`
- `dmux-workflows`
- `docker-patterns`
- `e2e-testing`
- `energy-procurement`
- `enterprise-agent-ops`
- `eval-harness`
- `exa-search`
- `fal-ai-media`
- `foundation-models-on-device`
- `frontend-patterns`
- `frontend-slides`
- `golang-patterns`
- `golang-testing`
- `inventory-demand-planning`
- `investor-materials`
- `investor-outreach`
- `iterative-retrieval`
- `java-coding-standards`
- `jpa-patterns`
- `kotlin-coroutines-flows`
- `kotlin-exposed-patterns`
- `kotlin-ktor-patterns`
- `kotlin-patterns`
- `kotlin-testing`
- `liquid-glass-design`
- `logistics-exception-management`
- `market-research`
- `nanoclaw-repl`
- `nutrient-document-processing`
- `perl-patterns`
- `perl-security`
- `perl-testing`
- `plankton-code-quality`
- `postgres-patterns`
- `production-scheduling`
- `project-guidelines-example`
- `prompt-optimizer`
- `python-patterns`
- `python-testing`
- `quality-nonconformance`
- `ralphinho-rfc-pipeline`
- `regex-vs-llm-structured-text`
- `returns-reverse-logistics`
- `search-first`
- `security-review`
- `security-scan`
- `skill-stocktake`
- `springboot-patterns`
- `springboot-security`
- `springboot-tdd`
- `springboot-verification`
- `strategic-compact`
- `swift-actor-persistence`
- `swift-concurrency-6-2`
- `swift-protocol-di-testing`
- `swiftui-patterns`
- `tdd-workflow`
- `verification-loop`
- `video-editing`
- `videodb`
- `visa-doc-translate`
- `x-api`

## Usage Rule

If the user explicitly names one of the skills above, or the task clearly matches it, use the project-local copy at `.agents/skills/<skill-name>/SKILL.md`.


1️⃣ /approvals → auto
2️⃣ 先 /plan 再执行
3️⃣ 加 AGENTS.md
4️⃣ 给完整任务而不是一步步指令