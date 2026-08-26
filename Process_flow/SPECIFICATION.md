# Kudos Specification

## User Stories

- As a team member, I want to select a colleague and write a short message of appreciation so that I can recognize their contribution.
- As a team member, I want to see recently submitted kudos on the dashboard so that recognition is visible to the wider team.
- As an administrator, I want to hide or delete inappropriate kudos messages so that the public feed remains respectful and appropriate.

## Acceptance Criteria: Administrator Moderation

- Administrators can hide a kudos message from the public feed without changing its original content.
- Administrators can permanently delete a kudos message when it violates team guidelines.
- Hidden kudos are excluded from the public dashboard feed.
- Only users with administrator permissions can hide or delete kudos.
- The system confirms the action before a kudos is permanently deleted.

## Data Model

### `users`

| Field | Type | Constraints | Description |
| --- | --- | --- | --- |
| `role` | VARCHAR(20) | Required, default: `member` | Authorization role. Supported values are `member` and `admin`; only administrators can moderate kudos. |

### `kudos`

| Field | Type | Constraints | Description |
| --- | --- | --- | --- |
| `id` | UUID | Primary key | Unique identifier for the kudos message. |
| `sender_id` | UUID | Required, foreign key | User who submitted the kudos. |
| `recipient_id` | UUID | Required, foreign key | User being recognized. |
| `message` | TEXT | Required | Short appreciation message. |
| `is_visible` | BOOLEAN | Required, default: `true` | Whether the kudos appears in the public feed. Administrators can set this to `false` to hide inappropriate content. |
| `created_at` | TIMESTAMP | Required | Time the kudos was submitted. |

Permanent deletion removes the row from `kudos`. Hiding a message preserves the row and sets `is_visible` to `false`, allowing moderation history and future review.

## Feed Query

The public dashboard should return only visible kudos, ordered newest first:

```sql
SELECT id, sender_id, recipient_id, message, created_at
FROM kudos
WHERE is_visible = TRUE
ORDER BY created_at DESC;
```