"""End-to-end tests for the RADON Blender Worker.

Tests verify:
1. Blender process launches.
2. Blender generates geometry.
3. GLB export succeeds.
4. GLB exists.
5. GLB is non-empty.
6. GLB header is valid (magic = b'glTF', version = 2).
7. The API returned success.

Run with: pytest tests/ -v
"""

import os
import sys
import time
import json
import struct
import subprocess
import shutil
import tempfile
from pathlib import Path

import pytest

# Add the project root to sys.path so imports work
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.core.blender_runner import BlenderRunner
from app.strategies.registry import strategy_registry
from app.strategies.anatomy import AnatomyStrategy
from app.strategies.general import GeneralObjectStrategy


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def find_blender() -> str | None:
    """Find the Blender executable on this system."""
    candidates = [
        os.environ.get("BLENDER_PATH", ""),
        "/usr/bin/blender",
        "/usr/local/bin/blender",
        "/opt/blender/blender",
        os.path.expanduser("~/blender/blender"),
    ]
    which = shutil.which("blender")
    if which:
        candidates.append(which)
    for c in candidates:
        if c and os.path.isfile(c) and os.access(c, os.X_OK):
            return c
    return None


BLENDER_PATH = find_blender()
BLENDER_AVAILABLE = BLENDER_PATH is not None


def clean_env(env: dict | None = None) -> dict:
    """Return env dict with LD_PRELOAD removed (breaks Blender in sandboxes)."""
    e = dict(env) if env else dict(os.environ)
    e.pop("LD_PRELOAD", None)
    return e


def validate_glb_header(path: str) -> bool:
    """Verify a file has a valid GLB binary container header."""
    with open(path, "rb") as f:
        magic = f.read(4)
        version = struct.unpack("<I", f.read(4))[0]
        length = struct.unpack("<I", f.read(4))[0]
    if magic != b"glTF":
        return False
    if version != 2:
        return False
    if length != os.path.getsize(path):
        return False
    return True


def run_blender_script(script_content: str, output_path: str, timeout: int = 120) -> subprocess.CompletedProcess:
    """Run a Blender script headlessly and return the result."""
    with tempfile.TemporaryDirectory(prefix="radon_test_") as tmpdir:
        script_file = Path(tmpdir) / "test_script.py"
        script_file.write_text(script_content, encoding="utf-8")

        env = clean_env()
        env["OUTPUT_PATH"] = str(output_path)
        env["QUALITY"] = "standard"

        result = subprocess.run(
            [BLENDER_PATH, "--background", "--factory-startup", "--python", str(script_file)],
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
        )
        return result


# ---------------------------------------------------------------------------
# Blender executable tests
# ---------------------------------------------------------------------------

class TestBlenderExecutable:
    """Verify the real Blender executable is available and can run."""

    def test_blender_executable_exists(self):
        """Blender executable must exist and be executable."""
        if not BLENDER_AVAILABLE:
            pytest.skip("Blender not installed in this environment")
        assert BLENDER_PATH is not None
        assert os.path.isfile(BLENDER_PATH)
        assert os.access(BLENDER_PATH, os.X_OK)

    def test_blender_version_runs(self):
        """Blender --background --version must execute successfully."""
        if not BLENDER_AVAILABLE:
            pytest.skip("Blender not installed in this environment")
        env = clean_env()
        result = subprocess.run(
            [BLENDER_PATH, "--background", "--version"],
            capture_output=True, text=True, timeout=30, env=env,
        )
        assert result.returncode == 0
        combined = result.stdout + result.stderr
        assert "Blender" in combined

    def test_blender_can_import_bpy(self):
        """Blender must be able to import bpy (the Python API)."""
        if not BLENDER_AVAILABLE:
            pytest.skip("Blender not installed in this environment")
        script = "import bpy; print(f'BPY_VERSION: {bpy.app.version_string}'); print('BPY_OK')"
        with tempfile.TemporaryDirectory() as tmpdir:
            script_file = Path(tmpdir) / "test_bpy.py"
            script_file.write_text(script)
            env = clean_env()
            result = subprocess.run(
                [BLENDER_PATH, "--background", "--factory-startup", "--python", str(script_file)],
                capture_output=True, text=True, timeout=30, env=env,
            )
        combined = result.stdout + result.stderr
        assert "BPY_OK" in combined
        assert result.returncode == 0

    def test_blender_version_string(self):
        """Extract and verify the Blender version string."""
        if not BLENDER_AVAILABLE:
            pytest.skip("Blender not installed in this environment")
        env = clean_env()
        result = subprocess.run(
            [BLENDER_PATH, "--background", "--version"],
            capture_output=True, text=True, timeout=30, env=env,
        )
        combined = result.stdout + result.stderr
        import re
        match = re.search(r"Blender\s+([\d.]+)", combined)
        assert match is not None
        version = match.group(1)
        parts = version.split(".")
        assert len(parts) >= 2
        int(parts[0])  # major version is numeric
        int(parts[1])  # minor version is numeric


# ---------------------------------------------------------------------------
# BlenderRunner class tests
# ---------------------------------------------------------------------------

class TestBlenderRunner:
    """Test the BlenderRunner wrapper class."""

    def test_is_available(self):
        if not BLENDER_AVAILABLE:
            pytest.skip("Blender not installed in this environment")
        runner = BlenderRunner()
        assert runner.is_available() is True

    def test_get_version(self):
        if not BLENDER_AVAILABLE:
            pytest.skip("Blender not installed in this environment")
        runner = BlenderRunner()
        version = runner.get_version()
        assert version is not None
        assert len(version) > 0

    def test_executable_path(self):
        if not BLENDER_AVAILABLE:
            pytest.skip("Blender not installed in this environment")
        runner = BlenderRunner()
        path = runner.executable_path
        assert path is not None
        assert os.path.isfile(path)


# ---------------------------------------------------------------------------
# Strategy tests (no Blender required — just script generation)
# ---------------------------------------------------------------------------

class TestStrategies:
    """Test that strategies generate valid Python scripts."""

    def test_anatomy_strategy_generates_heart(self):
        strategy = AnatomyStrategy()
        script = strategy.build_script("heart", "", "standard")
        assert "import bpy" in script
        assert "Heart_Body" in script
        assert "export_glb" in script
        assert "OUTPUT_PATH" in script

    def test_anatomy_strategy_generates_brain(self):
        strategy = AnatomyStrategy()
        script = strategy.build_script("brain", "", "standard")
        assert "Brain_Mass" in script

    def test_molecule_strategy_generates_dna(self):
        from app.strategies.molecule import MoleculeStrategy
        strategy = MoleculeStrategy()
        script = strategy.build_script("DNA double helix", "", "standard")
        assert "DNA" in script or "helix" in script
        assert "import bpy" in script

    def test_molecule_strategy_generates_water(self):
        from app.strategies.molecule import MoleculeStrategy
        strategy = MoleculeStrategy()
        script = strategy.build_script("water", "", "standard")
        assert "Oxygen" in script

    def test_astronomy_strategy_generates_saturn(self):
        from app.strategies.astronomy import AstronomyStrategy
        strategy = AstronomyStrategy()
        script = strategy.build_script("Saturn", "", "standard")
        assert "Saturn" in script
        assert "Ring" in script

    def test_vehicle_strategy_generates_airplane(self):
        from app.strategies.vehicle import VehicleStrategy
        strategy = VehicleStrategy()
        script = strategy.build_script("Boeing 747", "", "standard")
        assert "Fuselage" in script

    def test_general_strategy_generates_sphere(self):
        strategy = GeneralObjectStrategy()
        script = strategy.build_script("sphere", "", "standard")
        assert "Sphere" in script

    def test_strategy_has_limitations(self):
        strategy = AnatomyStrategy()
        limitations = strategy.get_limitations("heart")
        assert len(limitations) > 0
        assert any("approximation" in l.lower() for l in limitations)

    def test_strategy_registry_returns_strategies(self):
        from app.strategies.anatomy import AnatomyStrategy
        strategy = strategy_registry.get("anatomy")
        assert isinstance(strategy, AnatomyStrategy)

    def test_strategy_registry_falls_back_to_general(self):
        from app.strategies.general import GeneralObjectStrategy
        strategy = strategy_registry.get_or_default("nonexistent_category")
        assert isinstance(strategy, GeneralObjectStrategy)

    def test_all_categories_have_strategies(self):
        categories = strategy_registry.list_categories()
        assert len(categories) >= 7
        for cat in categories:
            s = strategy_registry.get(cat)
            assert s is not None


# ---------------------------------------------------------------------------
# GLB generation tests (require real Blender)
# ---------------------------------------------------------------------------

class TestGLBGeneration:
    """Test that Blender actually generates non-empty GLB files."""

    def test_generate_simple_sphere(self):
        """Generate a simple sphere and verify GLB output."""
        if not BLENDER_AVAILABLE:
            pytest.skip("Blender not installed in this environment")

        strategy = GeneralObjectStrategy()
        script = strategy.build_script("sphere", "", "standard")

        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "test_sphere.glb"
            result = run_blender_script(script, str(output), timeout=60)

            # 1. Blender process launched (returncode is set)
            assert result.returncode is not None

            # 2. Blender generated geometry (check output for SUCCESS)
            combined = result.stdout + result.stderr
            assert "SUCCESS" in combined, f"Blender did not report success: {combined[-500:]}"

            # 3. GLB export succeeded
            assert output.exists(), "GLB file was not created"

            # 4. GLB exists (checked above)

            # 5. GLB is non-empty
            size = output.stat().st_size
            assert size > 0, "GLB file is empty"
            assert size > 100, f"GLB file suspiciously small: {size} bytes"

            # 6. GLB header is valid
            assert validate_glb_header(str(output)), "GLB header is invalid (magic/version mismatch)"

    def test_generate_heart(self):
        """Generate a simplified human heart and verify GLB output."""
        if not BLENDER_AVAILABLE:
            pytest.skip("Blender not installed in this environment")

        strategy = AnatomyStrategy()
        script = strategy.build_script("heart", "", "standard")

        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "test_heart.glb"
            result = run_blender_script(script, str(output), timeout=90)

            combined = result.stdout + result.stderr
            assert result.returncode == 0, f"Blender exited with error: {combined[-500:]}"
            assert "SUCCESS" in combined, f"Blender did not report success: {combined[-500:]}"

            assert output.exists(), "GLB file was not created"
            size = output.stat().st_size
            assert size > 0, "GLB file is empty"
            assert size > 100, f"GLB file suspiciously small: {size} bytes"

            # Verify genuine GLB
            assert validate_glb_header(str(output)), "GLB header is invalid"

    def test_generate_multiple_objects(self):
        """Generate multiple different objects to verify generic engine works."""
        if not BLENDER_AVAILABLE:
            pytest.skip("Blender not installed in this environment")

        test_cases = [
            ("cube", "general"),
            ("water", "molecule"),
            ("Saturn", "astronomy"),
        ]

        for entity, category in test_cases:
            strategy = strategy_registry.get_or_default(category)
            script = strategy.build_script(entity, "", "preview")

            with tempfile.TemporaryDirectory() as tmpdir:
                output = Path(tmpdir) / f"test_{entity}.glb"
                result = run_blender_script(script, str(output), timeout=60)

                assert result.returncode == 0, f"Failed for {entity}: {result.stderr[-300:]}"
                assert output.exists(), f"GLB not created for {entity}"
                assert output.stat().st_size > 0, f"GLB empty for {entity}"
                assert validate_glb_header(str(output)), f"Invalid GLB header for {entity}"

    def test_glb_header_magic_bytes(self):
        """Explicitly check GLB magic bytes are b'glTF'."""
        if not BLENDER_AVAILABLE:
            pytest.skip("Blender not installed in this environment")

        strategy = GeneralObjectStrategy()
        script = strategy.build_script("cube", "", "preview")

        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "test_cube.glb"
            run_blender_script(script, str(output), timeout=60)

            with open(str(output), "rb") as f:
                magic = f.read(4)
            assert magic == b"glTF", f"GLB magic bytes are {magic}, expected b'glTF'"


# ---------------------------------------------------------------------------
# API tests (require both Blender and the FastAPI server)
# ---------------------------------------------------------------------------

class TestAPI:
    """Test the HTTP API endpoints."""

    def test_health_endpoint(self):
        """Test the /health endpoint returns correct structure."""
        if not BLENDER_AVAILABLE:
            pytest.skip("Blender not installed in this environment")

        from fastapi.testclient import TestClient
        from app.main import app

        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert "status" in data
        assert "blender" in data
        assert "version" in data
        assert "worker" in data
        assert data["worker"] == "radon-blender-worker"

        if BLENDER_AVAILABLE:
            assert data["status"] == "healthy"
            assert data["blender"] == "available"
            assert data["version"] is not None

    def test_generate_endpoint_sphere(self):
        """Test the /generate endpoint creates a real GLB."""
        if not BLENDER_AVAILABLE:
            pytest.skip("Blender not installed in this environment")

        from fastapi.testclient import TestClient
        from app.main import app

        client = TestClient(app)
        response = client.post("/generate", json={
            "requestId": "test-sphere-001",
            "entity": "sphere",
            "category": "general",
            "description": "A simple sphere",
            "quality": "standard",
            "outputFormat": "glb",
        })

        assert response.status_code == 200
        data = response.json()

        # 6. The API returned success
        assert data["success"] is True
        assert data["requestId"] == "test-sphere-001"
        assert data["origin"] == "BLENDER_GENERATED"
        assert data["outputFormat"] == "glb"
        assert data["fileSizeBytes"] > 0
        assert data["assetUrl"].startswith("/assets/")
        assert len(data["limitations"]) > 0

        # Verify the actual GLB file exists and has valid header
        import app.main as main_mod
        from app.core.config import settings
        asset_path = Path(settings.output_dir) / data["assetUrl"].split("/assets/")[1]
        assert asset_path.exists(), f"GLB file not found at {asset_path}"
        assert validate_glb_header(str(asset_path)), "Generated GLB has invalid header"

    def test_generate_endpoint_heart(self):
        """Test the /generate endpoint creates a heart GLB."""
        if not BLENDER_AVAILABLE:
            pytest.skip("Blender not installed in this environment")

        from fastapi.testclient import TestClient
        from app.main import app

        client = TestClient(app)
        response = client.post("/generate", json={
            "requestId": "test-heart-001",
            "entity": "heart",
            "category": "anatomy",
            "description": "A simplified human heart",
            "quality": "standard",
            "outputFormat": "glb",
        })

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert data["origin"] == "BLENDER_GENERATED"
        assert data["fileSizeBytes"] > 0
        assert "metadata" in data
        assert data["metadata"]["generation_strategy"] == "AnatomyStrategy"
        assert data["metadata"]["blender_scene_objects"] > 0

        # Verify the actual GLB file
        from app.core.config import settings
        asset_path = Path(settings.output_dir) / data["assetUrl"].split("/assets/")[1]
        assert asset_path.exists()
        assert validate_glb_header(str(asset_path)), "Heart GLB has invalid header"

    def test_generate_validates_request(self):
        """Test that invalid requests are rejected."""
        from fastapi.testclient import TestClient
        from app.main import app

        client = TestClient(app)

        # Missing required fields
        response = client.post("/generate", json={"requestId": "test-001"})
        assert response.status_code == 422

    def test_generate_rejects_invalid_format(self):
        """Test that invalid output formats are rejected."""
        from fastapi.testclient import TestClient
        from app.main import app

        client = TestClient(app)
        response = client.post("/generate", json={
            "requestId": "test-002",
            "entity": "cube",
            "category": "general",
            "outputFormat": "obj",  # Invalid
        })
        assert response.status_code == 422

    def test_generate_rejects_invalid_quality(self):
        """Test that invalid quality levels are rejected."""
        from fastapi.testclient import TestClient
        from app.main import app

        client = TestClient(app)
        response = client.post("/generate", json={
            "requestId": "test-003",
            "entity": "cube",
            "category": "general",
            "quality": "ultra",  # Invalid
        })
        assert response.status_code == 422

    def test_generate_rejects_null_byte_injection(self):
        """Test that null bytes in input are stripped (path traversal prevention)."""
        from fastapi.testclient import TestClient
        from app.main import app

        client = TestClient(app)
        response = client.post("/generate", json={
            "requestId": "test-004",
            "entity": "cube\x00../../etc/passwd",
            "category": "general",
        })
        # Should not crash — null bytes stripped by validator
        if BLENDER_AVAILABLE:
            assert response.status_code in (200, 422)
        else:
            assert response.status_code == 503

    def test_categories_endpoint(self):
        """Test the /categories endpoint."""
        from fastapi.testclient import TestClient
        from app.main import app

        client = TestClient(app)
        response = client.get("/categories")
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        assert len(data["categories"]) >= 7

    def test_health_when_blender_unavailable(self):
        """Test that /health reports unavailable when Blender is not found."""
        from fastapi.testclient import TestClient
        from app.core.blender_runner import BlenderRunner
        from app.main import app

        # Create a runner that points to a nonexistent Blender
        bad_runner = BlenderRunner(blender_path="/nonexistent/blender")

        # Monkey-patch the app's runner
        import app.main as main_mod
        original = main_mod.blender_runner
        main_mod.blender_runner = bad_runner
        try:
            client = TestClient(app)
            response = client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "unavailable"
            assert data["blender"] == "unavailable"
        finally:
            main_mod.blender_runner = original
