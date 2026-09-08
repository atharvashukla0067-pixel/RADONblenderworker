"""Base class for all generation strategies.

Each strategy produces a Blender Python script that, when run headlessly,
constructs a scene and exports it as GLB. Strategies are selected by category.
"""

from __future__ import annotations

import textwrap
from abc import ABC, abstractmethod
from typing import Any


class GenerationStrategy(ABC):
    """Abstract base for a Blender generation strategy.

    Subclasses implement `build_script()` which returns the full Python
    script text that Blender will execute in headless mode.

    The script MUST:
    - Read OUTPUT_PATH from os.environ for the export path
    - Read QUALITY from os.environ for quality level
    - Construct geometry using bpy
    - Export using bpy.ops.export_scene.gltf or equivalent
    - Exit cleanly
    """

    # Category name this strategy handles (set by subclass)
    category: str = "general"

    @abstractmethod
    def build_script(self, entity: str, description: str, quality: str) -> str:
        """Return the Blender Python script as a string.

        Args:
            entity: The entity name (sanitized, max 200 chars)
            description: Free-text description (sanitized, max 2000 chars)
            quality: One of 'preview', 'standard', 'high'

        Returns:
            Python script source code as a string
        """
        ...

    def get_limitations(self, entity: str) -> list[str]:
        """Return human-readable limitations for this strategy's output."""
        return [
            "Generated geometry is an approximation, not a verified scientific/anatomical model.",
            "Proportions and details are simplified and may not be accurate to real-world references.",
        ]

    def get_strategy_name(self) -> str:
        return self.__class__.__name__

    # -- Helpers for subclasses --

    def _header(self) -> str:
        """Common Blender script header: imports, quality config, output path."""
        return textwrap.dedent("""\
            import bpy
            import os
            import math
            import sys

            OUTPUT_PATH = os.environ.get("OUTPUT_PATH", "/tmp/output.glb")
            QUALITY = os.environ.get("QUALITY", "standard")

            # Quality presets
            if QUALITY == "preview":
                SUBDIV_LEVEL = 0
                BEVEL_SEGMENTS = 1
                SHADING_SMOOTH = True
            elif QUALITY == "high":
                SUBDIV_LEVEL = 3
                BEVEL_SEGMENTS = 4
                SHADING_SMOOTH = True
            else:  # standard
                SUBDIV_LEVEL = 1
                BEVEL_SEGMENTS = 2
                SHADING_SMOOTH = True

            # Clean default scene
            bpy.ops.wm.read_factory_settings(use_empty=True)

            def add_material(obj, name, color, metallic=0.0, roughness=0.5):
                mat = bpy.data.materials.new(name=name)
                mat.use_nodes = True
                bsdf = mat.node_tree.nodes.get("Principled BSDF")
                if bsdf:
                    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
                    bsdf.inputs["Metallic"].default_value = metallic
                    bsdf.inputs["Roughness"].default_value = roughness
                obj.data.materials.append(mat)
                return mat

            def export_glb():
                # Select all mesh objects for export
                for obj in bpy.context.scene.objects:
                    obj.select_set(False)
                meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
                for m in meshes:
                    m.select_set(True)
                bpy.ops.export_scene.gltf(
                    filepath=OUTPUT_PATH,
                    export_format='GLB',
                    use_selection=True,
                    export_apply=True,
                )

            def count_meshes():
                return len([o for o in bpy.context.scene.objects if o.type == 'MESH'])
        """)

    def _footer(self) -> str:
        """Common Blender script footer: export and verify."""
        return textwrap.dedent("""\

            # Export
            export_glb()

            # Verify output
            if not os.path.exists(OUTPUT_PATH):
                print("ERROR: GLB output file was not created")
                sys.exit(1)
            if os.path.getsize(OUTPUT_PATH) == 0:
                print("ERROR: GLB output file is empty")
                sys.exit(1)
            print(f"SUCCESS: Exported {os.path.getsize(OUTPUT_PATH)} bytes to {OUTPUT_PATH}")
            print(f"MESH_COUNT: {count_meshes()}")
        """)
