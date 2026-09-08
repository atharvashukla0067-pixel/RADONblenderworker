"""General object generation strategy.

Fallback strategy for entities that don't match any specific category.
Creates a reasonable 3D representation based on keywords in the entity name.
"""

from __future__ import annotations

import textwrap
from .base import GenerationStrategy


class GeneralObjectStrategy(GenerationStrategy):
    category = "general"

    def get_limitations(self, entity: str) -> list[str]:
        return [
            f"'{entity}' is a simplified geometric approximation generated procedurally.",
            "The model may not resemble the actual object in detail or proportion.",
        ]

    def build_script(self, entity: str, description: str, quality: str) -> str:
        entity_lower = entity.lower().strip()

        if "cube" in entity_lower or "box" in entity_lower:
            return self._cube_script()
        elif "sphere" in entity_lower or "ball" in entity_lower:
            return self._sphere_script()
        elif "cylinder" in entity_lower or "column" in entity_lower or "pillar" in entity_lower:
            return self._cylinder_script()
        elif "cone" in entity_lower:
            return self._cone_script()
        elif "torus" in entity_lower or "donut" in entity_lower or "ring" in entity_lower:
            return self._torus_script()
        elif "tree" in entity_lower:
            return self._tree_script()
        elif "chair" in entity_lower:
            return self._chair_script()
        elif "table" in entity_lower:
            return self._table_script()
        else:
            return self._composite_object_script(entity)

    def _cube_script(self) -> str:
        return self._header() + textwrap.dedent("""\
            # --- CUBE ---
            bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0, 0, 0))
            cube = bpy.context.active_object
            cube.name = "Cube"
            if BEVEL_SEGMENTS > 0:
                bpy.ops.object.modifier_add(type='BEVEL')
                cube.modifiers["Bevel"].segments = BEVEL_SEGMENTS
                bpy.ops.object.modifier_apply(modifier="Bevel")
            if SHADING_SMOOTH:
                bpy.ops.object.shade_smooth()
            add_material(cube, "Cube_Mat", (0.6, 0.6, 0.65), metallic=0.3, roughness=0.4)
        """) + self._footer()

    def _sphere_script(self) -> str:
        return self._header() + textwrap.dedent("""\
            # --- SPHERE ---
            bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, segments=32, ring_count=16, location=(0, 0, 0))
            sphere = bpy.context.active_object
            sphere.name = "Sphere"
            if SHADING_SMOOTH:
                bpy.ops.object.shade_smooth()
            add_material(sphere, "Sphere_Mat", (0.5, 0.5, 0.55), metallic=0.3, roughness=0.3)
            if SUBDIV_LEVEL > 0:
                mod = sphere.modifiers.new(name="Subsurf", type='SUBSURF')
                mod.levels = SUBDIV_LEVEL
                bpy.ops.object.modifier_apply(modifier=mod.name)
        """) + self._footer()

    def _cylinder_script(self) -> str:
        return self._header() + textwrap.dedent("""\
            # --- CYLINDER ---
            bpy.ops.mesh.primitive_cylinder_add(radius=1.0, depth=2.0, vertices=32, location=(0, 0, 0))
            cyl = bpy.context.active_object
            cyl.name = "Cylinder"
            if SHADING_SMOOTH:
                bpy.ops.object.shade_smooth()
            add_material(cyl, "Cyl_Mat", (0.5, 0.5, 0.55), metallic=0.3, roughness=0.3)
            if SUBDIV_LEVEL > 0:
                mod = cyl.modifiers.new(name="Subsurf", type='SUBSURF')
                mod.levels = SUBDIV_LEVEL
                bpy.ops.object.modifier_apply(modifier=mod.name)
        """) + self._footer()

    def _cone_script(self) -> str:
        return self._header() + textwrap.dedent("""\
            # --- CONE ---
            bpy.ops.mesh.primitive_cone_add(radius1=1.0, radius2=0, depth=2.0, vertices=32, location=(0, 0, 0))
            cone = bpy.context.active_object
            cone.name = "Cone"
            if SHADING_SMOOTH:
                bpy.ops.object.shade_smooth()
            add_material(cone, "Cone_Mat", (0.5, 0.5, 0.55), metallic=0.3, roughness=0.3)
        """) + self._footer()

    def _torus_script(self) -> str:
        return self._header() + textwrap.dedent("""\
            # --- TORUS ---
            bpy.ops.mesh.primitive_torus_add(major_radius=1.0, minor_radius=0.3, major_segments=48, minor_segments=16, location=(0, 0, 0))
            torus = bpy.context.active_object
            torus.name = "Torus"
            if SHADING_SMOOTH:
                bpy.ops.object.shade_smooth()
            add_material(torus, "Torus_Mat", (0.6, 0.4, 0.3), metallic=0.2, roughness=0.5)
            if SUBDIV_LEVEL > 0:
                mod = torus.modifiers.new(name="Subsurf", type='SUBSURF')
                mod.levels = SUBDIV_LEVEL
                bpy.ops.object.modifier_apply(modifier=mod.name)
        """) + self._footer()

    def _tree_script(self) -> str:
        return self._header() + textwrap.dedent("""\
            # --- TREE ---
            # Trunk
            bpy.ops.mesh.primitive_cylinder_add(radius=0.25, depth=2.0, vertices=16, location=(0, 0, 0))
            trunk = bpy.context.active_object
            trunk.name = "Trunk"
            if SHADING_SMOOTH:
                bpy.ops.object.shade_smooth()
            add_material(trunk, "Trunk_Mat", (0.4, 0.2, 0.05), roughness=0.9)

            # Foliage (3 spheres)
            for i, (z, s) in enumerate([(1.2, 0.8), (1.6, 0.7), (2.0, 0.5)]):
                bpy.ops.mesh.primitive_uv_sphere_add(radius=s, segments=16, ring_count=12, location=(0, 0, z))
                foliage = bpy.context.active_object
                foliage.name = f"Foliage_{i}"
                if SHADING_SMOOTH:
                    bpy.ops.object.shade_smooth()
                add_material(foliage, f"Fol_Mat_{i}", (0.15, 0.4, 0.1), roughness=0.8)
        """) + self._footer()

    def _chair_script(self) -> str:
        return self._header() + textwrap.dedent("""\
            # --- CHAIR ---
            # Seat
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.5))
            seat = bpy.context.active_object
            seat.name = "Seat"
            seat.scale = (0.6, 0.6, 0.05)
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            add_material(seat, "Seat_Mat", (0.5, 0.3, 0.15), roughness=0.6)

            # Backrest
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.28, 0.9))
            back = bpy.context.active_object
            back.name = "Backrest"
            back.scale = (0.6, 0.05, 0.5)
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            add_material(back, "Back_Mat", (0.5, 0.3, 0.15), roughness=0.6)

            # Legs
            for x_off in [-0.25, 0.25]:
                for y_off in [-0.25, 0.25]:
                    bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=0.5, vertices=8, location=(x_off, y_off, 0.25))
                    leg = bpy.context.active_object
                    leg.name = f"Leg_{x_off}_{y_off}"
                    add_material(leg, f"Leg_Mat_{x_off}_{y_off}", (0.3, 0.2, 0.1), roughness=0.7)
        """) + self._footer()

    def _table_script(self) -> str:
        return self._header() + textwrap.dedent("""\
            # --- TABLE ---
            # Top
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 1.0))
            top = bpy.context.active_object
            top.name = "Table_Top"
            top.scale = (1.5, 1.0, 0.08)
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            add_material(top, "Top_Mat", (0.5, 0.3, 0.15), roughness=0.6)

            # Legs
            for x_off in [-0.65, 0.65]:
                for y_off in [-0.4, 0.4]:
                    bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=1.0, vertices=12, location=(x_off, y_off, 0.5))
                    leg = bpy.context.active_object
                    leg.name = f"Leg_{x_off}_{y_off}"
                    add_material(leg, f"Leg_Mat_{x_off}_{y_off}", (0.3, 0.2, 0.1), roughness=0.7)
        """) + self._footer()

    def _composite_object_script(self, entity: str) -> str:
        safe_entity = entity.replace("'", "").replace('"', "")[:80]
        return self._header() + textwrap.dedent(f"""\
            # --- GENERAL OBJECT: {safe_entity} ---
            import random
            random.seed(hash("{safe_entity}") & 0xFFFFFFFF)

            # Create a composite object from primitives
            shapes = ['cube', 'sphere', 'cylinder', 'cone']
            num_parts = random.randint(2, 5)

            for i in range(num_parts):
                shape = random.choice(shapes)
                x = random.uniform(-0.8, 0.8)
                y = random.uniform(-0.8, 0.8)
                z = random.uniform(0, 1.0)
                size = random.uniform(0.3, 0.7)

                color = (random.uniform(0.2, 0.8), random.uniform(0.2, 0.8), random.uniform(0.2, 0.8))

                if shape == 'cube':
                    bpy.ops.mesh.primitive_cube_add(size=size, location=(x, y, z))
                elif shape == 'sphere':
                    bpy.ops.mesh.primitive_uv_sphere_add(radius=size * 0.5, segments=16, ring_count=12, location=(x, y, z))
                elif shape == 'cylinder':
                    bpy.ops.mesh.primitive_cylinder_add(radius=size * 0.5, depth=size, vertices=16, location=(x, y, z))
                else:  # cone
                    bpy.ops.mesh.primitive_cone_add(radius1=size * 0.5, radius2=0, depth=size, vertices=16, location=(x, y, z))

                obj = bpy.context.active_object
                obj.name = f"Part_{{i}}"
                if SHADING_SMOOTH:
                    bpy.ops.object.shade_smooth()
                add_material(obj, f"Mat_{{i}}", color, metallic=random.uniform(0, 0.5), roughness=random.uniform(0.2, 0.8))
        """) + self._footer()
