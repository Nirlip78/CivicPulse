# CivicPulse database changes

The additive SQLite migration in `backend.app.database.session.migrate_schema`
preserves existing records and adds complaint reference, title, preferred and
detected language, original location, locality, landmark, geocoded address,
location source, latitude/longitude, supporting information, intent, priority,
and resolution timestamp. It creates category/status and coordinate indexes.

`attachments` is a new related table with safe storage metadata. Existing
predictions and status history are retained. This lightweight migration is
appropriate for the current SQLite MVP; a production deployment should replace
it with versioned Alembic migrations and a managed database backup process.
