def test_aimq_import():
    import sys

    print("\n=== Before importing aimq ===")
    print("langgraph" in sys.modules)

    print("\n=== Importing aimq.agents ===")
    try:
        import aimq.agents  # noqa: F401

        print("SUCCESS")
    except Exception as e:
        print(f"FAILED: {e}")
        import traceback

        traceback.print_exc()

        print("\n=== Checking sys.modules for langgraph ===")
        for key in sorted(sys.modules.keys()):
            if "langgraph" in key.lower():
                mod = sys.modules[key]
                print(f"  {key}: {mod}")
                if hasattr(mod, "__path__"):
                    print(f"    __path__: {mod.__path__}")
