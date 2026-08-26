# Kudos System Specification

Status: Approved

## Functional Requirements

### User Stories

1. As an authenticated employee, I can select another active colleague from a list.
2. As an authenticated employee, I can write and submit a short message of appreciation.
3. As an employee, I can see recently submitted visible kudos on the public dashboard feed.
4. As an administrator, I can hide an inappropriate kudos message without changing its original content.
5. As an administrator, I can permanently delete an inappropriate kudos message after confirmation.
6. As an administrator, I can review moderation status and the reason for a moderation action.

### Acceptance Criteria

- Users must be authenticated before they can load colleagues, submit kudos, or access moderation actions.
- The recipient list contains active colleagues only; a user cannot give kudos to themselves.
- A message is required, trimmed before storage, and limited to 500 characters.
- Empty, whitespace-only, oversized, or invalid submissions return a clear validation error and are not stored.
- Successful submissions appear at the top of the feed and are stored with the sender, recipient, and creation time.
- The public feed shows only records where `is_visible = TRUE`, ordered newest first, with pagination.
- The system rejects obvious duplicate submissions from the same sender to the same recipient with the same normalized message within 24 hours.
- Basic spam controls apply: rate-limit submissions per user and reject messages containing disallowed content according to the team moderation policy.
- Administrators can hide content by setting `is_visible` to `FALSE`; hidden content is excluded from the public feed.
- Hiding preserves the original kudos and records the administrator, timestamp, and reason.
- Deletion requires explicit confirmation, is restricted to administrators, and records an audit event before permanent removal.
- Non-administrators receive an authorization error and never see moderation controls.
- The interface provides loading, success, empty, validation, authorization, and server-error states.
- The interface remains usable on desktop, tablet, and mobile screen sizes without horizontal scrolling.

## Technical Design

### Authentication and Authorization

The production app uses the employee identity provider for sign-in and session management. Every API request carries a validated session or bearer token. Users have a role of `member` or `admin`; authorization is enforced server-side for every moderation endpoint. The frontend admin mode is only a prototype representation and must not be treated as a security boundary.

### Database Schema

#### `users`

| Field | Type | Constraints | Description |
| --- | --- | --- | --- |
| `id` | UUID | Primary key | Unique user identifier. |
| `display_name` | VARCHAR(120) | Required | Name shown in the application. |
| `email` | VARCHAR(255) | Required, unique | Employee identity and notification address. |
| `role` | VARCHAR(20) | Required, default: `member` | Authorization role: `member` or `admin`. |
| `is_active` | BOOLEAN | Required, default: `true` | Whether the user can give or receive kudos. |

#### `kudos`

| Field | Type | Constraints | Description |
| --- | --- | --- | --- |
| `id` | UUID | Primary key | Unique kudos identifier. |
| `sender_id` | UUID | Required, foreign key to `users.id` | User who submitted the kudos. |
| `recipient_id` | UUID | Required, foreign key to `users.id` | User being recognized. |
| `message` | VARCHAR(500) | Required | Sanitized appreciation message. |
| `is_visible` | BOOLEAN | Required, default: `true` | Whether the message appears in the public feed. |
| `moderated_by` | UUID | Nullable, foreign key to `users.id` | Administrator who hid the message. |
| `moderated_at` | TIMESTAMP | Nullable | Time of the moderation action. |
| `reason_for_moderation` | VARCHAR(500) | Nullable | Reason for hiding or deleting content. |
| `created_at` | TIMESTAMP | Required | Time the kudos was submitted. |

Add indexes on `(is_visible, created_at DESC)`, `sender_id`, and `recipient_id`. Enforce foreign keys and reject self-recognition at the service layer or with a database constraint.

#### `moderation_events`

| Field | Type | Constraints | Description |
| --- | --- | --- | --- |
| `id` | UUID | Primary key | Audit event identifier. |
| `kudos_id` | UUID | Required | Identifier of the affected kudos. |
| `admin_id` | UUID | Required, foreign key to `users.id` | Administrator who acted. |
| `action` | VARCHAR(20) | Required | `hidden` or `deleted`. |
| `reason` | VARCHAR(500) | Required | Moderation rationale. |
| `created_at` | TIMESTAMP | Required | Time the action occurred. |

Hiding updates `kudos.is_visible` and moderation metadata. Deletion writes a `moderation_events` record before removing the kudos row. The public feed query is:

```sql
SELECT id, sender_id, recipient_id, message, created_at
FROM kudos
WHERE is_visible = TRUE
ORDER BY created_at DESC
LIMIT :page_size OFFSET :offset;
```

### API Endpoints

All endpoints require authentication. JSON errors use a consistent shape: `{ "error": "code", "message": "human-readable message" }`.

| Method | Endpoint | Purpose | Success |
| --- | --- | --- | --- |
| `GET` | `/api/users?active=true` | Load selectable colleagues. | `200` with user summaries. |
| `GET` | `/api/kudos?page=1&page_size=20` | Load the public visible feed. | `200` with items and pagination metadata. |
| `POST` | `/api/kudos` | Create a kudos. Body: `{ recipient_id, message }`. | `201` with the created kudos. |
| `GET` | `/api/admin/kudos?visible=false` | List hidden or all content for moderation. Admin only. | `200` with moderation metadata. |
| `PATCH` | `/api/admin/kudos/:id/visibility` | Hide a kudos. Body: `{ is_visible: false, reason }`. Admin only. | `200` with updated status. |
| `DELETE` | `/api/admin/kudos/:id` | Permanently delete a kudos after confirmation. Admin only. | `204` after audit logging. |

Expected errors include `400` for invalid input, `401` for unauthenticated requests, `403` for non-admin moderation requests, `404` for missing records, `409` for duplicate submissions, and `429` for rate limits.

### Frontend Components and Interactions

- `Dashboard`: coordinates the feed and composer and handles loading/error states.
- `KudosFeed`: displays paginated public kudos and refreshes after submission.
- `KudosComposer`: provides colleague selection, message input, character count, validation, and submit feedback.
- `AdminMode` and `ModerationActions`: visible only when the authenticated user has the admin role; provide hide/delete actions and confirmation.
- `PeopleSummary`: shows participation information without exposing inactive users.

The current static prototype maps these responsibilities to `index.html`, `styles.css`, and `app.js`, with `localStorage` standing in for the API and database. Production components must call the authenticated API instead.

### Security, Performance, and Operations

- Validate authorization on the server, never only in the browser.
- Sanitize or safely encode user-generated message text before rendering to prevent XSS.
- Use parameterized queries, CSRF protection where applicable, secure session cookies, HTTPS, and strict content security policy.
- Apply per-user rate limits, duplicate detection, maximum payload sizes, and moderation keyword or policy checks.
- Paginate the feed, fetch only required fields, use the visibility/created index, and cache short-lived feed responses where appropriate.
- Log authentication failures, validation failures, rate limits, moderation actions, and server errors without logging sensitive tokens or unnecessary message content.
- Return correlation IDs for server errors and monitor latency, error rate, feed load failures, and moderation activity.

## Implementation Plan

1. Approve this specification and confirm the identity-provider role mapping.
2. Create users, kudos, and moderation event migrations. This blocks API implementation.
3. Implement authentication middleware, role authorization, validation, duplicate detection, and rate limiting.
4. Implement user, feed, creation, hide, and delete API endpoints with audit logging.
5. Connect the frontend composer and public feed to the API.
6. Add the administrator moderation view, reason capture, confirmation dialog, and hidden-content states.
7. Add automated tests, security checks, accessibility checks, and responsive browser tests.
8. Deploy migrations and the API behind staging authentication, run acceptance tests, then promote to production with monitoring enabled.

## Testing Strategy

- Unit test message trimming, length limits, self-recognition, duplicate detection, visibility changes, and role checks.
- API test successful creation, pagination, hidden-content filtering, validation errors, `401`/`403` authorization failures, `409` duplicates, and `429` rate limits.
- Test that hide preserves content and writes moderation metadata, while delete requires confirmation and writes an audit event.
- Run browser tests for composer submission, public feed refresh, admin hide/delete, error states, keyboard access, and mobile layouts.
- Perform security testing for XSS payloads, unauthorized endpoint access, CSRF, injection, and abusive request rates.

## Deployment Considerations

- Run database migrations before deploying API code that depends on new fields.
- Store identity-provider and database credentials in the deployment secret manager.
- Use separate staging and production environments with backups and rollback procedures.
- Serve the frontend over HTTPS and configure the API origin, CSP, and authentication callback URLs per environment.
- Roll out moderation features behind an administrator-only feature flag and monitor audit events after release.