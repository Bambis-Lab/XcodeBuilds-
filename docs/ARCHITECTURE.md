# Architecture — XB-01 to XB-04

Source repositories remain authoritative. Reusable workflows are invoked by caller repositories with `workflow_call`; an Actions run is executed and billed in the **caller context**. The central public repository holds workflows, script tooling, project metadata and synthetic test fixtures. It does not clone/apply configuration to Factory, HA, BlackGlass or iOS Next.

1. XB-01: registry and JSON profiles; all signing disabled, ios-next disabled.
2. XB-02: `xcode-27` hosted ARM64 image, environment log + genuine Swift compile/test.
3. XB-03: cross-repository reusable unsigned build/test: checkout caller first; checkout pinned central tooling separately; invoke Python subprocess argument arrays, never shell-evaluate inputs.
4. XB-04: `xcresult` attachment export (optional), validation of exact named PNG manifests, duplicate detection, provenance and SHA256 artifact index.

Two independent references must match reviewed versions: workflow `@COMMIT_SHA` and `with.tooling_ref: COMMIT_SHA`. Until a reviewed commit and tests exist, do not advertise production readiness. Consumers' branch protection, permitted Actions and artifact storage govern their own runs.

## Non-goals
Signing, notarization, App Store deployment, Xcode Cloud, public mirroring of private project source, private data exfiltration, self-hosted runners, billing evasion.
