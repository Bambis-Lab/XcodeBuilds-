# Onboarding a source repository

1. Keep source and Xcode schemes/workspaces in the original repository.
2. Select `swift-package`, `xcode-project` or `xcode-workspace`, set path to Package.swift directory or .xcodeproj/.xcworkspace relative to repository root.
3. From a reviewed, merged foundation release note, get the SAME full 40-character SHA for workflow reference and `tooling_ref`. Do not assume a branch was deployed.
4. In the source repository, create a small caller workflow with `permissions: contents: read` and a job:
   ```yaml
   jobs:
     build:
       uses: Bambis-Lab/XcodeBuilds-/.github/workflows/reusable-apple-build.yml@<REVIEWED_40_CHARACTER_SHA>
       with:
         tooling_ref: <REVIEWED_40_CHARACTER_SHA>
         project_kind: swift-package
         source_path: .
   ```
5. Test under repository Actions. A private caller is charged/limited under private Actions quota; public tools do not waive this.
6. Optional `reusable-apple-tests.yml` for unit/UI tests and `reusable-visual-acceptance.yml` for named PNG acceptance; screenshot manifest lives in caller source and is required.
7. Signing and publishing intentionally out of scope.

The sample placeholder must be substituted before use. The named-screen adapter for iOS Next is XB-05, **not** part of this foundation.
