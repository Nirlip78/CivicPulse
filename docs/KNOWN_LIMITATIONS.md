# Known limitations

- Civic transcript provenance and every dataset licence are unconfirmed.
- Translation has no training split; no translation model is trained.
- Urgency and sentiment in the complaint workflow are explicitly rule-based
  estimates requiring human review, not validated civic predictors.
- Optional pretrained models are intentionally absent; the application remains
  usable offline through local fallbacks.
- The current UI is a small React research MVP; it does not include uploads,
  maps, user management or a production deployment configuration.
