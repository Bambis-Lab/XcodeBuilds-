# Security policy

- This is a PUBLIC repository. No certificates, provisioning profiles, credentials, real app artifacts or private sources may be committed.
- All workflows use `permissions: contents: read` and no inherited secrets; no `pull_request_target` or untrusted shell expression evaluation.
- `CODE_SIGNING_ALLOWED=NO`; never export signed IPA/DMG or deploy.
- Public-hosted macOS standard runners are free **only when the calling repository is public**. Private caller workflows count against private minutes. Larger `-xlarge` runners are not selected.
- Inputs are passed via environment variables and Python subprocess argument vectors. Runtime source paths must stay inside checkout; cross-repo tool checkout is under `.xcodebuilds-tools`.
- Pin workflow reference and tooling checkout to the SAME reviewed full SHA for third-party consumption. `main` and mutable tags are discouraged for consumers.
- Artifact export rejects symlinks; SHA-256 indexes provide provenance not signatures. Artifacts may still contain sensitive screenshot content: configure callers accordingly and review before publishing.
- Repo maintainers should enforce branch protection, CODEOWNERS, reviews, Actions restrictions and storage budget separately through GitHub Settings; this code does not pretend to change those settings.
- Never copy or run services against live Factory, HA, BlackGlass or the original iOS Next branch during XB-01–XB-04.
