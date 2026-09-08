"""Engineering generation strategy.

Generates simplified mechanical/engineering structures: gears, engines, turbines, etc.
"""

from __future__ import annotations

import textwrap
from .base import GenerationStrategy


class EngineeringStrategy(GenerationStrategy):
    category = "engineering"

    def get_limitations(self, entity: str) -> list[str]:
        return [
            f"'{entity}' is a simplified geometric approximation, not an engineering-accurate model.",
            "Moving parts, tolerances, and material properties are not represented.",
        ]

    def build_script(self, entity: str, description: str, quality: str) -> str:
        entity_lower = entity.lower().strip()

        if "gear" in entity_lower:
            return self._gear_script()
        elif "engine" in entity_lower or "motor" in entity_lower:
            return self._engine_script()
        elif "turbine" in entity_lower:
            return self._turbine_script()
        elif "bolt" in entity_lower or "screw" in entity_lower:
            return self._bolt_script()
        elif "pipe" in entity_lower or "tube" in entity_lower:
            return self._pipe_script()
        elif "beam" in entity_lower or "ibeam" in entity_lower or "i-beam" in entity_lower:
            return self._beam_script()
        else:
            return self._generic_engineering_script(entity)

    def _gear_script(self) -> str:
        return self._header() + textwrap.dedent("""\
            # --- GEAR ---
            # Main disc
            bpy.ops.mesh.primitive_cylinder_add(radius=1.0, depth=0.3, vertices=32, location=(0, 0, 0))
            gear = bpy.context.active_object
            gear.name = "Gear_Body"
            if SHADING_SMOOTH:
                bpy.ops.object.shade_smooth()
            add_material(gear, "Gear_Mat", (0.6, 0.6, 0.62), metallic=0.8, roughness=0.3)

            # Teeth
            num_teeth = 16
            for i in range(num_teeth):
                angle = i * 2 * math.pi / num_teeth
                x = 1.1 * math.cos(angle)
                y = 1.1 * math.sin(angle)
                bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, y, 0))
                tooth = bpy.context.active_object
                tooth.name = f"Tooth_{i}"
                tooth.scale = (0.15, 0.15, 0.3)
                bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
                tooth.rotation_euler = (0, 0, angle)
                add_material(tooth, f"Tooth_Mat_{i}", (0.55, 0.55, 0.57), metallic=0.8, roughness=0.3)

            # Center hole (using a small cylinder as visual indicator)
            bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=0.35, vertices=16, location=(0, 0, 0))
            hole = bpy.context.active_object
            hole.name = "Center_Hole"
            if SHADING_SMOOTH:
                bpy.ops.object.shade_smooth()
            add_material(hole, "Hole_Mat", (0.1, 0.1, 0.1), metallic=0.5, roughness=0.5)
        """) + self._footer()

    def _engine_script(self) -> str:
        return self._header() + textwrap.dedent("""\
            # --- ENGINE BLOCK ---
            # Main block
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.5))
            block = bpy.context.active_object
            block.name = "Engine_Block"
            block.scale = (1.5, 2.5, 0.8)
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            if BEVEL_SEGMENTS > 0:
                bpy.ops.object.modifier_add(type='BEVEL')
                block.modifiers["Bevel"].segments = BEVEL_SEGMENTS
                bpy.ops.object.modifier_apply(modifier="Bevel")
            add_material(block, "Block_Mat", (0.3, 0.3, 0.32), metallic=0.7, roughness=0.4)

            # Cylinders
            for i in range(4):
                x = -0.45 + i * 0.3
                bpy.ops.mesh.primitive_cylinder_add(radius=0.12, depth=0.8, vertices=20, location=(x, 0, 1.2))
                cyl = bpy.context.active_object
                cyl.name = f"Cylinder_{i}"
                if SHADING_SMOOTH:
                    bpy.ops.object.shade_smooth()
                add_material(cyl, f"Cyl_Mat_{i}", (0.4, 0.4, 0.42), metallic=0.6, roughness=0.3)

            # Cylinder head
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 1.7))
            head = bpy.context.active_object
            head.name = "Cylinder_Head"
            head.scale = (1.6, 2.6, 0.2)
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            add_material(head, "Head_Mat", (0.35, 0.35, 0.37), metallic=0.6, roughness=0.4)

            # Exhaust pipes
            for i in range(4):
                x = -0.45 + i * 0.3
                bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=1.5, vertices=12, location=(x, 1.5, 1.2))
                pipe = bpy.context.active_object
                pipe.name = f"Exhaust_{i}"
                pipe.rotation_euler = (math.pi / 2, 0, 0)
                bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
                if SHADING_SMOOTH:
                    bpy.ops.object.shade_smooth()
                add_material(pipe, f"Exh_Mat_{i}", (0.5, 0.5, 0.52), metallic=0.8, roughness=0.2)

            # Crankshaft pulley
            bpy.ops.mesh.primitive_cylinder_add(radius=0.25, depth=0.15, vertices=20, location=(0, -1.4, 0.5))
            pulley = bpy.context.active_object
            pulley.name = "Crankshaft_Pulley"
            pulley.rotation_euler = (math.pi / 2, 0, 0)
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
            if SHADING_SMOOTH:
                bpy.ops.object.shade_smooth()
            add_material(pulley, "Pul_Mat", (0.2, 0.2, 0.2), metallic=0.7, roughness=0.3)
        """) + self._footer()

    def _turbine_script(self) -> str:
        return self._header() + textwrap.dedent("""\
            # --- TURBINE ---
            # Central hub
            bpy.ops.mesh.primitive_cylinder_add(radius=0.3, depth=0.4, vertices=20, location=(0, 0, 0))
            hub = bpy.context.active_object
            hub.name = "Turbine_Hub"
            hub.rotation_euler = (math.pi / 2, 0, 0)
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
            if SHADING_SMOOTH:
                bpy.ops.object.shade_smooth()
            add_material(hub, "Hub_Mat", (0.4, 0.4, 0.42), metallic=0.8, roughness=0.3)

            # Blades
            num_blades = 12
            for i in range(num_blades):
                angle = i * 2 * math.pi / num_blades
                bpy.ops.mesh.primitive_cube_add(size=1.0, location=(math.cos(angle) * 0.7, math.sin(angle) * 0.7, 0))
                blade = bpy.context.active_object
                blade.name = f"Blade_{i}"
                blade.scale = (0.04, 0.7, 0.15)
                bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
                blade.rotation_euler = (math.radians(15), 0, angle)
                if BEVEL_SEGMENTS > 0:
                    bpy.ops.object.modifier_add(type='BEVEL')
                    blade.modifiers["Bevel"].segments = BEVEL_SEGMENTS
                    bpy.ops.object.modifier_apply(modifier="Bevel")
                add_material(blade, f"Blade_Mat_{i}", (0.6, 0.6, 0.62), metallic=0.7, roughness=0.3)

            # Casing ring
            bpy.ops.mesh.primitive_torus_add(major_radius=1.1, minor_radius=0.1, major_segments=48, minor_segments=12, location=(0, 0, 0))
            casing = bpy.context.active_object
            casing.name = "Casing"
            casing.rotation_euler = (math.pi / 2, 0, 0)
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
            if SHADING_SMOOTH:
                bpy.ops.object.shade_smooth()
            add_material(casing, "Casing_Mat", (0.3, 0.3, 0.32), metallic=0.6, roughness=0.4)
        """) + self._footer()

    def _bolt_script(self) -> str:
        return self._header() + textwrap.dedent("""\
            # --- BOLT / SCREW ---
            # Head (hexagonal)
            bpy.ops.mesh.primitive_cylinder_add(radius=0.4, depth=0.25, vertices=6, location=(0, 0, 0.1))
            head = bpy.context.active_object
            head.name = "Bolt_Head"
            if SHADING_SMOOTH:
                bpy.ops.object.shade_smooth()
            add_material(head, "Head_Mat", (0.5, 0.5, 0.52), metallic=0.9, roughness=0.2)

            # Shaft
            bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=2.0, vertices=20, location=(0, 0, -0.9))
            shaft = bpy.context.active_object
            shaft.name = "Bolt_Shaft"
            if SHADING_SMOOTH:
                bpy.ops.object.shade_smooth()
            add_material(shaft, "Shaft_Mat", (0.5, 0.5, 0.52), metallic=0.9, roughness=0.2)

            # Thread approximation (rings)
            for i in range(10):
                z = -0.1 - i * 0.18
                bpy.ops.mesh.primitive_torus_add(major_radius=0.16, minor_radius=0.02, major_segments=16, minor_segments=6, location=(0, 0, z))
                thread = bpy.context.active_object
                thread.name = f"Thread_{i}"
                if SHADING_SMOOTH:
                    bpy.ops.object.shade_smooth()
                add_material(thread, f"Thread_Mat_{i}", (0.48, 0.48, 0.5), metallic=0.9, roughness=0.2)
        """) + self._footer()

    def _pipe_script(self) -> str:
        return self._header() + textwrap.dedent("""\
            # --- PIPE / TUBE ---
            # Main pipe
            bpy.ops.mesh.primitive_cylinder_add(radius=0.3, depth=4.0, vertices=24, location=(0, 0, 0))
            pipe = bpy.context.active_object
            pipe.name = "Pipe"
            pipe.rotation_euler = (math.pi / 2, 0, 0)
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
            if SHADING_SMOOTH:
                bpy.ops.object.shade_smooth()
            add_material(pipe, "Pipe_Mat", (0.5, 0.5, 0.52), metallic=0.7, roughness=0.3)

            # Flange 1
            bpy.ops.mesh.primitive_cylinder_add(radius=0.5, depth=0.15, vertices=24, location=(0, 2.0, 0))
            flange1 = bpy.context.active_object
            flange1.name = "Flange_1"
            flange1.rotation_euler = (math.pi / 2, 0, 0)
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
            if SHADING_SMOOTH:
                bpy.ops.object.shade_smooth()
            add_material(flange1, "F1_Mat", (0.4, 0.4, 0.42), metallic=0.6, roughness=0.4)

            # Flange 2
            bpy.ops.mesh.primitive_cylinder_add(radius=0.5, depth=0.15, vertices=24, location=(0, -2.0, 0))
            flange2 = bpy.context.active_object
            flange2.name = "Flange_2"
            flange2.rotation_euler = (math.pi / 2, 0, 0)
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
            if SHADING_SMOOTH:
                bpy.ops.object.shade_smooth()
            add_material(flange2, "F2_Mat", (0.4, 0.4, 0.42), metallic=0.6, roughness=0.4)

            # Valve
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.4))
            valve = bpy.context.active_object
            valve.name = "Valve"
            valve.scale = (0.6, 0.6, 0.4)
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            add_material(valve, "Valve_Mat", (0.3, 0.3, 0.32), metallic=0.5, roughness=0.5)

            # Bolt holes on flanges
            for y_off in [2.0, -2.0]:
                for i in range(6):
                    angle = i * math.pi / 3
                    x = 0.4 * math.cos(angle)
                    z = 0.4 * math.sin(angle)
                    bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=0.2, vertices=8, location=(x, y_off, z))
                    bolt = bpy.context.active_object
                    bolt.name = f"BoltHole_{y_off}_{i}"
                    bolt.rotation_euler = (math.pi / 2, 0, 0)
                    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
                    add_material(bolt, f"BH_Mat_{y_off}_{i}", (0.2, 0.2, 0.2), metallic=0.8, roughness=0.3)
        """) + self._footer()

    def _beam_script(self) -> str:
        return self._header() + textwrap.dedent("""\
            # --- I-BEAM ---
            # Top flange
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.45))
            top = bpy.context.active_object
            top.name = "Top_Flange"
            top.scale = (0.5, 4.0, 0.08)
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            add_material(top, "Top_Mat", (0.5, 0.5, 0.52), metallic=0.6, roughness=0.4)

            # Bottom flange
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, -0.45))
            bottom = bpy.context.active_object
            bottom.name = "Bottom_Flange"
            bottom.scale = (0.5, 4.0, 0.08)
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            add_material(bottom, "Bot_Mat", (0.5, 0.5, 0.52), metallic=0.6, roughness=0.4)

            # Web
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0))
            web = bpy.context.active_object
            web.name = "Web"
            web.scale = (0.08, 4.0, 0.8)
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            add_material(web, "Web_Mat", (0.5, 0.5, 0.52), metallic=0.6, roughness=0.4)
        """) + self._footer()

    def _generic_engineering_script(self, entity: str) -> str:
        safe_entity = entity.replace("'", "").replace('"', "")[:80]
        return self._header() + textwrap.dedent(f"""\
            # --- GENERIC ENGINEERING OBJECT: {safe_entity} ---
            # Base plate
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.1))
            base = bpy.context.active_object
            base.name = "Base_Plate"
            base.scale = (2.0, 2.0, 0.2)
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            add_material(base, "Base_Mat", (0.4, 0.4, 0.42), metallic=0.6, roughness=0.4)

            # Main cylinder
            bpy.ops.mesh.primitive_cylinder_add(radius=0.6, depth=1.5, vertices=24, location=(0, 0, 1.0))
            cyl = bpy.context.active_object
            cyl.name = "Main_Cylinder"
            if SHADING_SMOOTH:
                bpy.ops.object.shade_smooth()
            add_material(cyl, "Cyl_Mat", (0.5, 0.5, 0.52), metallic=0.7, roughness=0.3)

            # Side supports
            for x_off in [-0.8, 0.8]:
                bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x_off, 0, 0.5))
                support = bpy.context.active_object
                support.name = f"Support_{'L' if x_off < 0 else 'R'}"
                support.scale = (0.15, 0.8, 0.8)
                bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
                add_material(support, f"Sup_Mat_{x_off}", (0.45, 0.45, 0.47), metallic=0.6, roughness=0.4)

            # Top cap
            bpy.ops.mesh.primitive_cylinder_add(radius=0.65, depth=0.2, vertices=24, location=(0, 0, 1.85))
            cap = bpy.context.active_object
            cap.name = "Top_Cap"
            if SHADING_SMOOTH:
                bpy.ops.object.shade_smooth()
            add_material(cap, "Cap_Mat", (0.4, 0.4, 0.42), metallic=0.6, roughness=0.4)
        """) + self._footer()
