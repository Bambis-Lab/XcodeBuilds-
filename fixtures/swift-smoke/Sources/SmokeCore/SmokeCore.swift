public enum SmokeCore {
    public static func checksum(_ numbers: [Int]) -> Int {
        numbers.reduce(0, +)
    }
}
