// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "BambisXcodeSmoke",
    platforms: [.macOS(.v13), .iOS(.v16)],
    products: [.library(name: "SmokeCore", targets: ["SmokeCore"])],
    targets: [
        .target(name: "SmokeCore"),
        .testTarget(name: "SmokeCoreTests", dependencies: ["SmokeCore"])
    ]
)
