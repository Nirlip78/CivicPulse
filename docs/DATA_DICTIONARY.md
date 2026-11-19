# Data dictionary

| Entity | Key fields | Purpose |
| --- | --- | --- |
| User | email, password_hash, role | Minimal account identity; role is citizen/admin. |
| Complaint | description, optional location, category, sentiment, urgency, status | Original citizen report and reviewed operational fields. |
| Prediction | field, value, confidence, method, human_correction | Preserves model advice separately from a reviewer correction. |
| StatusHistory | status, note, changed_by_id, created_at | Immutable status-change trail. |
| CitizenResponse | author_id, message, created_at | Administrator message for a citizen. |

No raw dataset rows are writable through the application.
