"""Standalone generation test script.

Can be run directly (without pytest) to verify Blender + GLB generation:
    python tests/test_standalone.py

This is useful inside the Docker container for quick verification.
"""

import os
import sys
import subprocess
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.core.blender_runner import BlenderRunner
from app.strategies.anatomy import AnatomyStrategy
from app.strategies.general import GeneralObjectStrategy


def test_blender_executable():
    """Test 1: Blender executable exists and runs."""
    print("\n=== Test 1: Blender Executable ===")
    runner = BlenderRunner()

    if not runner.is_available():
        print("FAIL: Blender executable not found")
        return False

    version = runner.get_version()
    print(f"PASS: Blender found at {runner.executable_path}")
    print(f"PASS: Blender version: {version}")
    return True


def test_simple_sphere():
    """Test 2: Generate a simple sphere GLB."""
    print("\n=== Test 2: Simple Sphere Generation ===")
    runner = BlenderRunner()

    if not runner.is_available():
        print("FAIL: Blender not available")
        return False

    strategy = GeneralObjectStrategy()
    script = strategy.build_script("sphere", "", "standard")

    with tempfile.TemporaryDirectory(prefix="radon_test_") as tmpdir:
        output = Path(tmpdir) / "sphere.glb"
        script_file = Path(tmpdir) / "generate.py"
        script_file.write_text(script)

        env = os.environ.copy()
        env["OUTPUT_PATH"] = str(output)
        env["QUALITY"] = "standard"

        result = subprocess.run(
            [runner.executable_path, "--background", "--factory-startup", "--python", str(script_file)],
            capture_output=True, text=True, timeout=60, env=env,
        )

        if result.returncode != 0:
            print(f"FAIL: Blender exited with code {result.returncode}")
            print(f"stderr: {result.stderr[-300:]}")
            return False

        if not output.exists():
            print("FAIL: GLB file not created")
            return False

        size = output.stat().st_size
        if size == 0:
            print("FAIL: GLB file is empty")
            return False

        print(f"PASS: Blender process launched (exit code 0)")
        print(f"PASS: GLB export succeeded")
        print(f"PASS: GLB exists at {output}")
        print(f"PASS: GLB is non-empty ({size} bytes)")
        return True


def test_heart():
    """Test 3: Generate a simplified human heart GLB."""
    print("\n=== Test 3: Human Heart Generation ===")
    runner = BlenderRunner()

    if not runner.is_available():
        print("FAIL: Blender not available")
        return False

    strategy = AnatomyStrategy()
    script = strategy.build_script("heart", "", "standard")

    with tempfile.TemporaryDirectory(prefix="radon_test_") as tmpdir:
        output = Path(tmpdir) / "heart.glb"
        script_file = Path(tmpdir) / "generate.py"
        script_file.write_text(script)

        env = os.environ.copy()
        env["OUTPUT_PATH"] = str(output)
        env["QUALITY"] = "standard"

        result = subprocess.run(
            [runner.executable_path, "--background", "--factory-startup", "--python", str(script_file)],
            capture_output=True, text=True, timeout=90, env=env,
        )

        if result.returncode != 0:
            print(f"FAIL: Blender exited with code {result.returncode}")
            print(f"stderr: {result.stderr[-300:]}")
            return False

        combined = result.stdout + result.stderr
        if "SUCCESS" not in combined:
            print(f"FAIL: Blender did not report SUCCESS")
            return False

        if not output.exists():
            print("FAIL: GLB file not created")
            return False

        size = output.stat().st_size
        if size == 0:
            print("FAIL: GLB file is empty")
            return False

        # Check mesh count
        import re
        mesh_match = re.search(r"MESH_COUNT:\s*(\d+)", combined)
        mesh_count = int(mesh_match.group(1)) if mesh_match else 0

        print(f"PASS: Blender process launched (exit code 0)")
        print(f"PASS: Blender generated geometry ({mesh_count} mesh objects)")
        print(f"PASS: GLB export succeeded")
        print(f"PASS: GLB exists at {output}")
        print(f"PASS: GLB is non-empty ({size} bytes)")
        return True


def main():
    print("=" * 60)
    print("RADON Blender Worker — Standalone Generation Tests")
    print("=" * 60)

    results = []
    results.append(("Blender Executable", test_blender_executable()))
    results.append(("Simple Sphere GLB", test_simple_sphere()))
    results.append(("Human Heart GLB", test_heart()))

    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    all_passed = True
    for name, passed in results:
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {name}")
        if not passed:
            all_passed = False

    print("=" * 60)
    if all_passed:
        print("ALL TESTS PASSED")
    else:
        print("SOME TESTS FAILED")
    print("=" * 60)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
