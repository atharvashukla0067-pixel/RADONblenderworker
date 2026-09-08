"""Blender executable manager — detects and runs the real Blender runtime."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import logging
from pathlib import Path
from typing import Optional

from .config import settings

logger = logging.getLogger("radon-blender-worker")


class BlenderNotFoundError(Exception):
    pass


class BlenderRunner:
    """Wraps the Blender executable, providing version detection and headless script execution."""

    def __init__(self, blender_path: Optional[str] = None) -> None:
        self._blender_path: Optional[str] = blender_path or settings.blender_path

    def _resolve_executable(self) -> Optional[str]:
        """Find the Blender executable. Checks configured path, PATH, and common install locations."""
        candidates: list[str] = []
        if self._blender_path:
            candidates.append(self._blender_path)
        # Common Docker / system install locations
        candidates.extend([
            "/usr/bin/blender",
            "/usr/local/bin/blender",
            "/opt/blender/blender",
            "/snap/blender/current/blender",
        ])
        path_lookup = shutil.which("blender")
        if path_lookup:
            candidates.append(path_lookup)

        for candidate in candidates:
            if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
                return candidate
        return None

    def _clean_env(self, env: dict[str, str]) -> dict[str, str]:
        """Remove LD_PRELOAD from the environment before launching Blender.

        Some sandboxed environments inject a virtual-filesystem library via
        LD_PRELOAD that causes Blender to hang on startup. Blender does its
        own file I/O and is incompatible with these interceptors.
        """
        env.pop("LD_PRELOAD", None)
        return env

    def is_available(self) -> bool:
        """Return True only if the Blender executable exists and can actually run."""
        exe = self._resolve_executable()
        if exe is None:
            return False
        try:
            env = self._clean_env(os.environ.copy())
            result = subprocess.run(
                [exe, "--background", "--version"],
                capture_output=True,
                text=True,
                timeout=20,
                env=env,
            )
            return result.returncode == 0 and "Blender" in (result.stdout + result.stderr)
        except (subprocess.TimeoutExpired, OSError):
            return False

    def get_version(self) -> Optional[str]:
        """Extract the Blender version string from the executable."""
        exe = self._resolve_executable()
        if exe is None:
            return None
        try:
            env = self._clean_env(os.environ.copy())
            result = subprocess.run(
                [exe, "--background", "--version"],
                capture_output=True,
                text=True,
                timeout=20,
                env=env,
            )
            output = result.stdout + result.stderr
            match = re.search(r"Blender\s+([\d.]+)", output)
            return match.group(1) if match else None
        except (subprocess.TimeoutExpired, OSError):
            return None

    @property
    def executable_path(self) -> Optional[str]:
        return self._resolve_executable()

    def run_script(
        self,
        script_path: str,
        output_path: str,
        timeout: Optional[int] = None,
    ) -> subprocess.CompletedProcess:
        """Run Blender headlessly with a Python generation script.

        The script receives the output path via the `OUTPUT_PATH` environment variable
        and quality via `QUALITY` so that no user input is ever passed as a command-line
        argument (preventing injection).
        """
        exe = self._resolve_executable()
        if exe is None:
            raise BlenderNotFoundError("Blender executable not found on this system")

        env = os.environ.copy()
        env = self._clean_env(env)
        env["OUTPUT_PATH"] = str(output_path)
        env["QUALITY"] = os.environ.get("QUALITY", "standard")
        env["ENTITY"] = os.environ.get("ENTITY", "")
        env["CATEGORY"] = os.environ.get("CATEGORY", "")

        effective_timeout = timeout or settings.job_timeout

        logger.info("Launching Blender: %s --background --python %s", exe, script_path)
        result = subprocess.run(
            [exe, "--background", "--factory-startup", "--python", script_path],
            capture_output=True,
            text=True,
            timeout=effective_timeout,
            env=env,
        )
        return result


blender_runner = BlenderRunner()
