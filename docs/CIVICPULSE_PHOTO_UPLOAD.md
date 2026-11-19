# CivicPulse photo evidence

Citizens may upload JPEG, PNG, or WebP image evidence through
`POST /complaints/{id}/attachments`. The server checks authenticated ownership,
declared media type, configured byte limit (`UPLOAD_MAX_BYTES`), generates a
UUID storage name, and records the original display name separately. Files are
kept outside public static routing in `uploads/` by default and downloaded only
through a permission-checked endpoint.

The system never accepts executable uploads, exposes storage paths, or lets a
citizen delete another citizen’s evidence. Administrators can inspect evidence;
the uploader or an administrator can delete it. OCR and speech input remain
unavailable until separately installed, tested local models are supplied.
