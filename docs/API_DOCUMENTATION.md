# API documentation

Interactive OpenAPI documentation is at `/docs` when the API runs.

| Endpoint | Purpose | Access |
| --- | --- | --- |
| `GET /health` | Readiness check | Public |
| `POST /auth/register`, `/auth/login` | Create account / obtain signed bearer token | Public |
| `POST /nlp/preprocess`, `/nlp/analyse` | Local Unit I / unified analysis | Public |
| `POST /research/embeddings` | Train small CBOW or Skip-gram demo | Public |
| `POST /research/attention`, `/research/summarise` | Local educational demonstrations | Public |
| `GET /datasets` | Safe dataset inventory | Public |
| `POST /complaints`, `GET /complaints/me` | Citizen workflow | Citizen token |
| `GET/PATCH /admin/complaints` | Review and management | Admin token |
| `POST /research/evaluate/civic-baseline` | Generate actual baseline JSON | Admin token |
