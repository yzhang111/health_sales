# Nutrition Assistant API v1 (Draft)

## Design Principles

- RESTful resource naming
- Explicit status codes
- Consistent error object
- Auditability for sensitive actions
- No medical diagnosis output

Base path: `/api/v1`

## Core Resources

- `customers`
- `assessments`
- `recommendations`
- `reports`
- `follow-ups`
- `compliance-events`

## Endpoint Draft

### Customers

- `POST /customers` create customer profile
- `GET /customers/{id}` get profile
- `PATCH /customers/{id}` update profile

### Assessments

- `POST /assessments` create intake and assessment
- `GET /assessments/{id}` fetch assessment with risk flags
- `POST /assessments/{id}/re-evaluate` re-run rules after updates

### Recommendations

- `POST /recommendations` generate recommendation set from assessment
- `GET /recommendations/{id}` fetch recommendation details

### Reports

- `POST /reports` generate customer report and rep script
- `GET /reports/{id}` fetch report status and artifacts

### Follow-Ups

- `POST /follow-ups` create follow-up plan (2-4 weeks)
- `GET /follow-ups/{id}` fetch follow-up status
- `POST /follow-ups/{id}/close` close follow-up with outcome notes

### Compliance Events

- `POST /compliance-events` log escalation, disclaimer injection, referral trigger
- `GET /compliance-events?customer_id={id}` audit lookup

## Response Shapes

### Success

```json
{
  "data": {},
  "meta": {}
}
```

### Error

```json
{
  "error": {
    "code": "validation_error",
    "message": "Request validation failed",
    "details": []
  }
}
```

## Key Business Rules in API Layer

- Any high-risk flag sets `assessment.requires_medical_referral=true`.
- Recommendation generation must attach evidence tags and confidence levels.
- Report generation must inject disclaimer blocks before publish.
- Sales script output must include prohibited-claim lint result.

## Suggested Status Codes

- `200` fetch/update success
- `201` create success
- `202` async report generation accepted
- `400` invalid payload
- `403` forbidden by role policy
- `404` missing resource
- `409` state conflict
- `422` semantically invalid request

## Idempotency and Audit

- Support `Idempotency-Key` on create endpoints.
- Every write action stores:
  - actor id
  - timestamp
  - before/after snapshot hash
  - reason code
