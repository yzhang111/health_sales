# Security and Compliance Checklist (Nutrition Assistant)

## Scope

Applies to customer health context, assessment outputs, recommendations, reports, and sales scripts.

## Data Protection

- Classify data as sensitive health-related personal information.
- Enforce least-privilege access (RBAC by role).
- Encrypt data in transit and at rest.
- Log access and mutation events for audit.
- Define retention and deletion policy per record type.

## Identity and Access

- No shared accounts for sales reps.
- Session controls with timeout and device awareness.
- Distinct permissions for:
  - Sales rep
  - Reviewer/supervisor
  - Compliance admin
  - System operator

## Input and Content Safety

- Validate all structured inputs via schema validation.
- Block prohibited claims in report/script generation.
- Force disclaimer insertion on every customer-facing report.
- Run contraindication checks before recommendation publish.

## Clinical Boundary Controls

- No disease diagnosis statements.
- No guaranteed outcome language.
- Mandatory referral trigger for red-line conditions.
- Display "consult physician" guidance when risk threshold is crossed.

## Secrets and Infrastructure

- Secrets stored only in secure secret manager or env vars.
- No hardcoded keys in code or templates.
- Restrict production data access to approved operators.
- Monitor failed auth attempts and unusual read patterns.

## Audit and Governance

- Keep immutable logs for recommendation generation and edits.
- Record source/evidence ID for each recommendation statement.
- Keep compliance event logs for referrals and overrides.
- Run periodic review of scripts for claim drift.

## Release Gate

A release is blocked if any of the following fail:

1. Red-line referral rule test suite
2. Disclaimer presence checks
3. Role access policy checks
4. Audit log completeness checks
5. Prohibited-claim lint checks
