# CivicPulse analytics

`GET /admin/analytics` derives all statistics from live `Complaint` records:
category, status, locality, language, sentiment, department, time-series,
unresolved count, and high-priority count. Filters apply server-side and are
returned in the response. `GET /admin/exports/complaints.csv` exports only
operational fields, not citizen credentials, descriptions, or exact GPS data.

`GET /admin/assistant` is a permission-scoped, structured query helper, not an
LLM. It cites matching complaint references and date range, and states that
complaint counts are reports rather than verified incidents.
