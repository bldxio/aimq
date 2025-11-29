"""Test module-level import."""

import sys

# This happens during collection
print("\n=== MODULE LEVEL: sys.path ===")
for i, p in enumerate(sys.path[:10]):
    print(f"{i}: {p}")

print("\n=== MODULE LEVEL: Importing aimq.agents ===")
try:
    import aimq.agents  # noqa: F401

    print("SUCCESS")
except Exception as e:
    print(f"FAILED: {e}")
    import traceback

    traceback.print_exc()


def test_dummy():
    assert True
