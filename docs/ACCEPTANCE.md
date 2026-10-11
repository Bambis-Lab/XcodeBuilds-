# Foundation acceptance gates (do not mark PASS without evidence)

| Gate | Status as coded | Terminal evidence required |
| --- | --- | --- |
| XB-01 | Implemented in feature branch | Registry/schema tests and source review |
| XB-02 | Implemented in feature branch | Real GitHub Actions Xcode 27 runner + Swift fixture `swift test` success |
| XB-03 | Implemented in feature branch | Reusable workflow calls `swift build` and `swift test` succeed |
| XB-04 | Implemented in feature branch | Positive screenshot fixture + negative tests + artifact export run |
| XB-05 iOS Next | Adapter/caller implemented; synthetic 56-shot validator 5/5 tests PASS; real V01–V04 Xcode status not yet independently confirmed | Real iPhone 18 Pro Max simulator run must finish PASS with exactly 56 valid PNGs and evidence bundle |

Tests reported by source code are not runner evidence. Check Actions URLs and exact commit SHA; failing or missing runs must be reported as outstanding. No merge or deployment permitted by this document.
