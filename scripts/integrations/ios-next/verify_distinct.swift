// XB-05: Detect nearly identical screenshot content even when PNG hashes differ.
// Runs only on the macOS Xcode runner. No Apple app/source modifications.
import Foundation
import CoreGraphics
import ImageIO

struct Picture {
    let path: String
    let appearance: String
    let pixels: [UInt8]
}

func fail(_ reason: String) -> Never {
    fputs("XB05_PERCEPTUAL_UNIQUENESS=FAIL " + reason + "\n", stderr)
    exit(1)
}

let args = CommandLine.arguments
guard args.count == 3, args[1] == "--root" else {
    fail("usage: swift verify_distinct.swift --root build/screenshots")
}
let root = URL(fileURLWithPath: args[2], isDirectory: true).standardizedFileURL
let manifestURL = root.appendingPathComponent("manifest.json")
guard let manifestBytes = try? Data(contentsOf: manifestURL),
      let json = try? JSONSerialization.jsonObject(with: manifestBytes) as? [String: Any],
      let images = json["images"] as? [[String: String]],
      images.count == 56 else { fail("missing or invalid 56-image manifest") }

let w = 96
let h = 200
let rowBytes = w * 4
let colorSpace = CGColorSpaceCreateDeviceRGB()

func thumbnail(_ url: URL) -> [UInt8] {
    guard let source = CGImageSourceCreateWithURL(url as CFURL, nil),
          let cg = CGImageSourceCreateImageAtIndex(source, 0, nil) else {
        fail("cannot decode " + url.lastPathComponent)
    }
    var output = [UInt8](repeating: 0, count: h * rowBytes)
    let success = output.withUnsafeMutableBytes { pointer -> Bool in
        guard let ctx = CGContext(data: pointer.baseAddress,
                                  width: w, height: h, bitsPerComponent: 8,
                                  bytesPerRow: rowBytes, space: colorSpace,
                                  bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue)
        else { return false }
        ctx.interpolationQuality = .high
        ctx.draw(cg, in: CGRect(x: 0, y: 0, width: w, height: h))
        return true
    }
    if !success { fail("cannot rasterize " + url.lastPathComponent) }
    return output
}

var pictures: [Picture] = []
for item in images {
    guard let name = item["path"], let mode = item["appearance"],
          mode == "light" || mode == "dark", name.hasPrefix(mode + "/"),
          name.hasSuffix(".png"), !name.contains("..") else {
        fail("invalid screenshot manifest record")
    }
    let url = root.appendingPathComponent(name).standardizedFileURL
    if !url.path.hasPrefix(root.path + "/") { fail("path escapes screenshot directory") }
    pictures.append(Picture(path: name, appearance: mode, pixels: thumbnail(url)))
}

var comparisons = 0
var minimum = Double.infinity
for i in pictures.indices {
    for j in (i + 1)..<pictures.count {
        let a = pictures[i], b = pictures[j]
        if a.appearance != b.appearance { continue }
        var total = 0
        var count = 0
        // Exclude both top and bottom status/header areas to avoid a changing clock.
        for y in 12..<(h - 12) {
            for x in 0..<w {
                let offset = y * rowBytes + x * 4
                for c in 0..<3 {
                    total += abs(Int(a.pixels[offset + c]) - Int(b.pixels[offset + c]))
                    count += 1
                }
            }
        }
        let mean = Double(total) / Double(count)
        minimum = min(minimum, mean)
        comparisons += 1
        if mean < 1.0 {
            fail(String(format: "near-duplicate %.4f %@ %@", mean, a.path, b.path))
        }
    }
}
guard comparisons == 756 else { fail("expected 756 same-appearance comparisons, got \(comparisons)") }
print(String(format: "XB05_PERCEPTUAL_UNIQUENESS=PASS images=56 pairs=%d min_mean_difference=%.4f", comparisons, minimum))
