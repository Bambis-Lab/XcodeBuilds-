#!/usr/bin/env bash
set -euo pipefail

# Only this sanitized public mirror is permitted; never try to fetch private source.
test "${GITHUB_REPOSITORY:-}" = "Bambis-Lab/ios-next-build" || {
  echo "::error::XB05_SOURCE_REPOSITORY_MISMATCH"; exit 1;
}
# An isolated same-repo PR into the visual branch is a testable, read-only
# alternative when Actions cannot be manually dispatched from a non-default branch.
if [[ "${GITHUB_EVENT_NAME:-}" == "pull_request" ]]; then
  [[ "${GITHUB_BASE_REF:-}" == "visual/ios-next-162-v01-v04" &&
     "${GITHUB_HEAD_REF:-}" == xb05/acceptance-* ]] || {
    echo "::error::XB05_UNEXPECTED_PULL_REQUEST_SCOPE"; exit 1;
  }
else
  [[ "${GITHUB_EVENT_NAME:-}" == "push" &&
     "${GITHUB_REF_NAME:-}" == "visual/ios-next-162-v01-v04" ]] || {
    echo "::error::XB05_SOURCE_BRANCH_MISMATCH"; exit 1;
  }
fi
BASE="32d436ff6c9d71a5618b6106a4672dde4a639e1e"
git fetch --no-tags --depth=1 origin "$BASE"
BASE="$BASE" python3 - <<'PY'
import os
import subprocess
changed = set(subprocess.check_output(
    ["git", "diff", "--name-only", os.environ["BASE"]+"..HEAD"],
    text=True).splitlines())
original = {
    ".github/workflows/xcode-improvements-screenshots.yml",
    "UITests/ImprovementsGalleryUITests.swift",
    "Scripts/package_improvement_screenshots.py",
    "Tests/FactoryMCPIntegrationTests.swift",
    "Sources/Features/AdminAreaView.swift",
    "Sources/Features/RunnerDashboardView.swift",
    "Sources/Features/Owner/Factory/FactoryCommandDeck.swift",
    "Sources/Features/Owner/Factory/FactoryStandaloneView.swift",
    "Sources/Features/Owner/Factory/FactoryConnectionModel.swift",
    "Sources/Features/Owner/Factory/FactoryConnectionView.swift",
    "Sources/Core/WireGuardTunnelController.swift",
    "Sources/Features/WireGuardView.swift",
}
allowed = original | {".github/workflows/xb05-ios-next-xcodebuilds.yml"}
assert original.issubset(changed), "XB05_V01_V04_PATCH_SET_INCOMPLETE: " + repr(original-changed)
assert changed.issubset(allowed), "XB05_UNAUTHORIZED_SOURCE_FILES: " + repr(changed-allowed)
print(f"XB05_SOURCE_SCOPE=PASS touched={len(changed)}")
PY

xcodebuild -version
test "$(xcrun --sdk iphonesimulator --show-sdk-version)" = "27.0"
if ! command -v xcodegen >/dev/null 2>&1; then
  HOMEBREW_NO_AUTO_UPDATE=1 brew install xcodegen
fi
bash Scripts/prepare_wireguard_dependency.sh
export CM_COMMIT="$(git rev-parse HEAD)"
export EXPECTED_VERSION="1.6.2"
export EXPECTED_BUILD="25"
bash Scripts/prepare_free_sideload_project.sh

mkdir -p build/screenshots build/xb05-logs
SIM_ID="$(xcrun simctl list devices available -j | python3 -c '
import json,sys
data=json.load(sys.stdin)
devices=[d["udid"] for name,series in data["devices"].items()
         if "iOS-27-0" in name for d in series
         if d["name"] == "iPhone 18 Pro Max" and d.get("isAvailable", True)]
assert devices, "No iOS 27 iPhone 18 Pro Max Simulator"
print(devices[0])
')"
echo "XB05_DEVICE=iPhone 18 Pro Max iOS27"
if ! xcrun simctl list devices booted | grep -q "$SIM_ID"; then
  xcrun simctl boot "$SIM_ID"
fi
xcrun simctl bootstatus "$SIM_ID" -b

xcodebuild \
  -project IOSNext.xcodeproj -scheme IOSNext -configuration Debug \
  -sdk iphonesimulator -destination "platform=iOS Simulator,id=$SIM_ID" \
  -parallel-testing-enabled NO -only-testing:IOSNextTests/FactoryMCPIntegrationTests \
  -derivedDataPath build/VisualDerivedData \
  -resultBundlePath build/Improvements-Factory-Regression.xcresult \
  CODE_SIGNING_ALLOWED=NO CODE_SIGNING_REQUIRED=NO CODE_SIGN_IDENTITY="" \
  test 2>&1 | tee build/xb05-logs/factory-regression.log
echo "XB05_FACTORY_CREDENTIAL_REGRESSION=PASS"

for APPEARANCE in light dark; do
  xcrun simctl ui "$SIM_ID" appearance "$APPEARANCE"
  if [ "$APPEARANCE" = light ]; then
    SELECT_A=testLightIndependentServices
    SELECT_B=testLightProductBackgrounds
    SELECT_C=testLightAdditionalStates
  else
    SELECT_A=testDarkIndependentServices
    SELECT_B=testDarkProductBackgrounds
    SELECT_C=testDarkAdditionalStates
  fi
  xcodebuild \
    -project IOSNext.xcodeproj -scheme IOSNext -configuration Debug \
    -sdk iphonesimulator -destination "platform=iOS Simulator,id=$SIM_ID" \
    -parallel-testing-enabled NO \
    "-only-testing:IOSNextUITests/ImprovementsGalleryUITests/$SELECT_A" \
    "-only-testing:IOSNextUITests/ImprovementsGalleryUITests/$SELECT_B" \
    "-only-testing:IOSNextUITests/ImprovementsGalleryUITests/$SELECT_C" \
    -derivedDataPath build/VisualDerivedData \
    -resultBundlePath "build/Improvements-$APPEARANCE.xcresult" \
    CODE_SIGNING_ALLOWED=NO CODE_SIGNING_REQUIRED=NO CODE_SIGN_IDENTITY="" \
    test 2>&1 | tee "build/xb05-logs/ui-$APPEARANCE.log"
  xcrun xcresulttool export attachments \
    --path "build/Improvements-$APPEARANCE.xcresult" \
    --output-path "build/screenshots/$APPEARANCE"
  echo "XB05_UI_$APPEARANCE=PASS"
done

python3 Scripts/package_improvement_screenshots.py
python3 .xcodebuilds-tools/scripts/integrations/ios-next/verify_gallery.py \
  --root build/screenshots --report build/xb05-acceptance.json
python3 .xcodebuilds-tools/scripts/artifacts/index.py \
  --root build/screenshots --output build/xb05-index.json
python3 .xcodebuilds-tools/scripts/artifacts/write_metadata.py \
  --output build/xb05-environment.json --project ios-next-1.6.2 --runner xcode-27
echo "XB05_VISUAL_56=PASS"
