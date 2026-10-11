# XB-05 — isolated public iOS Next 1.6.2 acceptance adapter

The canonical private repo is **Bambis-Lab/ios-next**. The public sanitized build mirror is **Bambis-Lab/ios-next-build**; use its `visual/ios-next-162-v01-v04` branch exclusively. The legacy repository `nicofroeba16-cell/ha-ios-next-ios` is archived and not a source for this block.

The original `.github/workflows/xcode-improvements-screenshots.yml` had a push trigger on the other branch, explaining why V01–V04 commits did not trigger that workflow. XB-05's caller resides in the public mirror and delegates to the exact reviewed `reusable-ios-next-162-visual.yml` commit. No other source mirrors, secrets, Apple signing, IPA, Factory, or private canonical access.

The adapter verifies the 12 changed product/test files against base `32d436ff6c9d71a5618b6106a4672dde4a639e1e` (plus its one new calling workflow). It prepares XcodeGen and pinned, audited WireGuardKit; boots the real iPhone 18 Pro Max iOS 27 simulator; runs Factory credential regressions; captures 28 named UI views in each appearance; exports xcresult attachments; invokes the existing app packaging script; independently checks count/unique hashes, PNG integrity, names, simulated states and an HTML gallery.

Evidence: GitHub Actions terminal success, 56 PNG files, a gallery, `xb05-acceptance.json`, `xb05-index.json` and provenance. Simulated backend states **do not prove live Factory connectivity**. The 56 captures currently cover iPhone 18 Pro Max; iPad screenshots are a separate later acceptance scope. The integration remains experimental until its first end-to-end green run.
