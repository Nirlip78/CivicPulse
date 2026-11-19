# CivicPulse geographic intelligence

Geographic data is stored only when a citizen explicitly submits GPS or a
manual map-selected coordinate. Textual location mentions never create a map
pin. `GET /admin/geography/complaints` returns only real records with stored
coordinates. The payload rounds coordinates to three decimals for dashboard
maps.

`GET /admin/geography/heatmap` aggregates rounded coordinate cells from real
records. Cells with one report are suppressed and never shown as a heat point.
Category, status, and locality filters are server-side. A heatmap measures
reported complaint density—not confirmed incidents or service failures.

The current application does not call Nominatim automatically. A future
geocoding implementation requires a service policy-compliant, rate-limited
server-side adapter and explicit user confirmation before storing results.
