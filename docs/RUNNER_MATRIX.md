# Runner/SDK matrix

| Domain | Label | Evidence requirement |
| --- | --- | --- |
| Xcode 27 preview | `xcode-27` (ARM64/macOS 27) | `xcodebuild -version`, Swift fixture `swift test` PASS |
| iOS/iPadOS | `xcode-27` | List real sim runtimes via `xcrun simctl`; run real app scheme |
| macOS | `xcode-27` | Run project scheme |
| watchOS/tvOS/visionOS | `xcode-27` | Verify SDK and simulator runtime present, or fail explicitly |
| Swift Package | `xcode-27` | `swift build` / `swift test` |

Availability is not acceptance. The `xcode-27` runner is a GitHub preview and may queue or change. No large/paid runner fallback.
