# Bambis-Lab XcodeBuilds

Reusable, **unsigned** Apple-platform build, test and visual-acceptance infrastructure. This public repository contains tooling and a synthetic fixture; it is **not** a mirror of app sources, Factory, Home Assistant, or signing materials.

## Status
Foundation XB-01–XB-04 implementation branch. **A checked-in workflow is not proof of a successful macOS run.** Consult Actions and [docs/ACCEPTANCE.md](docs/ACCEPTANCE.md) for evidence.

## Scope
- XB-01: registry, profiles, permissions, architecture and governance.
- XB-02: GitHub-hosted `xcode-27` macOS/Swift smoke test.
- XB-03: reusable unsigned build and test workflows (Swift Package or Xcode project/workspace).
- XB-04: screenshot validation, xcresult export (best effort), artifact manifests.

## Getting started
1. Open [Actions](https://github.com/Bambis-Lab/XcodeBuilds-/actions), inspect **Foundation Checks**, **Xcode 27 Runner Smoke** and **Reusable Integration Smoke**.
2. Run the smoke and wait for terminal **success** before declaring the runner ready. `xcode-27` is a GitHub-hosted preview image, not a self-hosted Mac.
3. Review [docs/ONBOARDING.md](docs/ONBOARDING.md) for integration from another repository. Consumers should pin both workflow and `tooling_ref` to the same reviewed full commit SHA.
4. No IPA signing, App Store upload, publishing, deployment or live-environment access is provided.

## Supported project types
`swift-package`, `xcode-project`, `xcode-workspace`. Profiles cover iOS, iPadOS, macOS, watchOS, tvOS, visionOS and Swift Packages subject to actually installed SDKs/runtimes.

## Security
All workflows use read-only repository tokens. No user-controlled shell is executed; input paths are constrained to the checked-out caller workspace. No inherited secrets. Check [docs/SECURITY.md](docs/SECURITY.md).

## License
No license is granted until the organization explicitly chooses one.