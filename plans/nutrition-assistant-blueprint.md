# Nutrition Assistant Blueprint

## Objective

Build a compliant assistant for nutrition sales reps to collect customer context, assess possible nutrition gaps, and generate customer-facing reports plus compliant sales guidance.

## Execution Mode

- Mode: direct project execution
- Baseline context: `NUTRITION_SOLUTION_BUSINESS_FLOW.md`
- Skill order: `blueprint -> market-research -> api-design -> security-review`

## Dependency Graph

1. Step 1 Product scope and boundaries
2. Step 2 Data model and workflow states
3. Step 3 Research evidence base
4. Step 4 Recommendation logic
5. Step 5 Report and script generation
6. Step 6 API contract and service boundaries
7. Step 7 Compliance and security controls
8. Step 8 Pilot readiness gate

Dependencies:
- 1 -> 2, 3
- 2 + 3 -> 4
- 4 -> 5, 6
- 2 + 5 + 6 -> 7
- 7 -> 8

Parallelizable:
- Steps 2 and 3 can run in parallel after step 1.
- Steps 5 and 6 can run in parallel after step 4.

## Step Plan

### Step 1: Product Scope and Boundaries

Context brief:
- Define what the system can recommend and what it must never claim.
- Separate nutrition support from medical diagnosis/treatment.

Tasks:
- Finalize MVP user journey for the two scenarios (sleep and post-surgery).
- Define red-line conditions that require physician referral.

Exit criteria:
- Approved capability boundary document.
- Approved escalation policy for risky cases.

### Step 2: Data Model and Workflow States

Context brief:
- Convert business flow into state transitions and required fields.

Tasks:
- Define entities: customer profile, assessment, recommendation, report, follow-up.
- Define required vs optional fields per stage.

Exit criteria:
- Canonical field dictionary.
- Workflow state machine approved.

### Step 3: Research Evidence Base

Context brief:
- Build traceable evidence to support each recommendation type.

Tasks:
- Build claim catalog with source requirements.
- Tag each recommendation with evidence level and recency.

Exit criteria:
- Evidence schema and source policy approved.
- Initial evidence backlog prioritized.

### Step 4: Recommendation Logic

Context brief:
- Create explainable, rule-first recommendation outputs.

Tasks:
- Build scoring rules for probable nutrition gaps.
- Define contraindications and interaction checks.

Exit criteria:
- Versioned rule matrix with test examples.
- Fail-safe behavior for low-confidence cases.

### Step 5: Report and Script Generation

Context brief:
- Generate two outputs: customer report and rep sales script.

Tasks:
- Define report template with mandatory disclaimer blocks.
- Define script template with compliant language patterns.

Exit criteria:
- Templates approved by business and compliance reviewers.
- Output quality checklist agreed.

### Step 6: API Contract and Service Boundaries

Context brief:
- Define APIs that support intake, assessment, recommendation, reporting, and follow-up.

Tasks:
- Specify endpoints, payloads, errors, idempotency, and audit hooks.
- Define async jobs for report generation and re-assessment.

Exit criteria:
- MVP API spec v1 approved.
- Consumer integration notes published.

### Step 7: Compliance and Security Controls

Context brief:
- Apply least-privilege and auditable handling for health-related personal data.

Tasks:
- Define RBAC model, data retention rules, and access logging.
- Define policy checks for risky content and prohibited claims.

Exit criteria:
- Security checklist passed.
- Compliance checklist passed.

### Step 8: Pilot Readiness Gate

Context brief:
- Validate the end-to-end workflow before production rollout.

Tasks:
- Run pilot with controlled customer samples.
- Measure report quality, escalation accuracy, and rep usability.

Exit criteria:
- Go/No-go decision with metrics.
- Production rollout plan with rollback path.

## Anti-Patterns To Avoid

- Generating diagnosis-like conclusions in customer reports.
- Recommendation without evidence tags or contraindication checks.
- Sales scripts that overpromise outcomes.
- Missing audit trail for who viewed or edited sensitive records.
