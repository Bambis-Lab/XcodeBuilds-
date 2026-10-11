import XCTest
@testable import SmokeCore

final class SmokeCoreTests: XCTestCase {
    func testChecksum() {
        XCTAssertEqual(SmokeCore.checksum([1, 2, 3]), 6)
        XCTAssertEqual(SmokeCore.checksum([]), 0)
    }
}
