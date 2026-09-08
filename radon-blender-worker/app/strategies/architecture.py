"""Architecture generation strategy.

Generates simplified building and structure approximations.
"""

from __future__ import annotations

import textwrap
from .base import GenerationStrategy


class ArchitectureStrategy(GenerationStrategy):
    category = "architecture"

    def get_limitations(self, entity: str) -> list[str]:
        return [
            f"'{entity}' is a simplified geometric approximation, not an architecturally accurate model.",
            "Interior spaces, structural details, and materials are not represented.",
        ]

    def build_script(self, entity: str, description: str, quality: str) -> str:
        entity_lower = entity.lower().strip()

        if "house" in entity_lower or "home" in entity_lower or "cottage" in entity_lower:
            return self._house_script()
        elif "tower" in entity_lower or "skyscraper" in entity_lower:
            return self._tower_script()
        elif "temple" in entity_lower or "parthenon" in entity_lower:
            return self._temple_script()
        elif "bridge" in entity_lower:
            return self._bridge_script()
        elif "pyramid" in entity_lower:
            return self._pyramid_script()
        elif "castle" in entity_lower or "fortress" in entity_lower:
            return self._castle_script()
        else:
            return self._generic_building_script(entity)

    def _house_script(self) -> str:
        return self._header() + textwrap.dedent("""\
            # --- HOUSE ---
            # Base
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.5))
            base = bpy.context.active_object
            base.name = "House_Base"
            base.scale = (2.0, 2.5, 1.0)
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            add_material(base, "Wall_Mat", (0.85, 0.8, 0.7), roughness=0.8)

            # Roof (pyramid/cone)
            bpy.ops.mesh.primitive_cone_add(radius1=1.5, radius2=0, depth=1.2, vertices=4, location=(0, 0, 1.6))
            roof = bpy.context.active_object
            roof.name = "Roof"
            roof.rotation_euler = (0, 0, math.radians(45))
            roof.scale = (1.5, 1.8, 1.0)
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
            add_material(roof, "Roof_Mat", (0.5, 0.2, 0.1), roughness=0.7)

            # Door
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 1.25, 0.4))
            door = bpy.context.active_object
            door.name = "Door"
            door.scale = (0.3, 0.02, 0.6)
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            add_material(door, "Door_Mat", (0.3, 0.15, 0.05), roughness=0.6)

            # Windows
            for x_off in [-0.6, 0.6]:
                bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x_off, 1.25, 0.7))
                win = bpy.context.active_object
                win.name = f"Window_{'L' if x_off < 0 else 'R'}"
                win.scale = (0.25, 0.02, 0.25)
                bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
                add_material(win, f"Win_Mat_{x_off}", (0.3, 0.5, 0.7), metallic=0.1, roughness=0.1)

            # Chimney
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.5, 0, 2.0))
            chim = bpy.context.active_object
            chim.name = "Chimney"
            chim.scale = (0.2, 0.2, 0.5)
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            add_material(chim, "Chim_Mat", (0.4, 0.35, 0.3), roughness=0.8)
        """) + self._footer()

    def _tower_script(self) -> str:
        return self._header() + textwrap.dedent("""\
            # --- TOWER / SKYSCRAPER ---
            # Main shaft
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 3.0))
            shaft = bpy.context.active_object
            shaft.name = "Tower_Shaft"
            shaft.scale = (1.0, 1.0, 6.0)
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            if BEVEL_SEGMENTS > 0:
                bpy.ops.object.modifier_add(type='BEVEL')
                shaft.modifiers["Bevel"].segments = BEVEL_SEGMENTS
                bpy.ops.object.modifier_apply(modifier="Bevel")
            add_material(shaft, "Tower_Mat", (0.6, 0.65, 0.7), metallic=0.5, roughness=0.2)

            # Tapered top
            bpy.ops.mesh.primitive_cone_add(radius1=0.7, radius2=0.3, depth=1.5, vertices=4, location=(0, 0, 6.75))
            top = bpy.context.active_object
            top.name = "Tower_Top"
            top.rotation_euler = (0, 0, math.radians(45))
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
            add_material(top, "Top_Mat", (0.5, 0.55, 0.6), metallic=0.5, roughness=0.2)

            # Antenna
            bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=1.5, vertices=8, location=(0, 0, 8.25))
            ant = bpy.context.active_object
            ant.name = "Antenna"
            add_material(ant, "Ant_Mat", (0.2, 0.2, 0.2), metallic=0.7, roughness=0.3)

            # Window strips (horizontal bands)
            for z in range(1, 6):
                bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, z * 1.0))
                band = bpy.context.active_object
                band.name = f"Window_Band_{z}"
                band.scale = (1.02, 1.02, 0.05)
                bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
                add_material(band, f"Band_Mat_{z}", (0.2, 0.3, 0.4), metallic=0.3, roughness=0.1)
        """) + self._footer()

    def _temple_script(self) -> str:
        return self._header() + textwrap.dedent("""\
            # --- TEMPLE (GRECO-ROMAN STYLE) ---
            # Base / stylobate
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.15))
            base = bpy.context.active_object
            base.name = "Stylobate"
            base.scale = (3.0, 4.0, 0.3)
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            add_material(base, "Base_Mat", (0.8, 0.78, 0.72), roughness=0.7)

            # Columns
            col_positions = []
            for x in [-1.2, 0, 1.2]:
                for y in [-1.6, -0.5, 0.5, 1.6]:
                    bpy.ops.mesh.primitive_cylinder_add(radius=0.18, depth=2.0, vertices=20, location=(x, y, 1.3))
                    col = bpy.context.active_object
                    col.name = f"Col_{x}_{y}"
                    if SHADING_SMOOTH:
                        bpy.ops.object.shade_smooth()
                    add_material(col, f"Col_Mat_{x}_{y}", (0.85, 0.83, 0.78), roughness=0.6)
                    col_positions.append((x, y))

            # Architrave (beam across columns)
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 2.5))
            arch = bpy.context.active_object
            arch.name = "Architrave"
            arch.scale = (3.0, 4.0, 0.3)
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            add_material(arch, "Arch_Mat", (0.82, 0.8, 0.75), roughness=0.7)

            # Pediment (triangular gable)
            bpy.ops.mesh.primitive_cone_add(radius1=2.0, radius2=0, depth=1.0, vertices=3, location=(0, 0, 3.2))
            ped = bpy.context.active_object
            ped.name = "Pediment"
            ped.rotation_euler = (math.radians(90), 0, math.radians(90))
            ped.scale = (1.0, 1.0, 1.5)
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
            add_material(ped, "Ped_Mat", (0.8, 0.78, 0.72), roughness=0.7)
        """) + self._footer()

    def _bridge_script(self) -> str:
        return self._header() + textwrap.dedent("""\
            # --- BRIDGE ---
            # Deck
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.5))
            deck = bpy.context.active_object
            deck.name = "Bridge_Deck"
            deck.scale = (0.8, 5.0, 0.2)
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            add_material(deck, "Deck_Mat", (0.4, 0.4, 0.42), roughness=0.6)

            # Towers
            for y_off in [-2.0, 2.0]:
                bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, y_off, 1.5))
                tower = bpy.context.active_object
                tower.name = f"Tower_{'B' if y_off < 0 else 'F'}"
                tower.scale = (0.3, 0.3, 2.0)
                bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
                add_material(tower, f"Tow_Mat_{y_off}", (0.5, 0.5, 0.52), roughness=0.5)

            # Suspension cables (simplified curves)
            for x_off in [-0.3, 0.3]:
                bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x_off, 0, 2.8))
                main_cable = bpy.context.active_object
                main_cable.name = f"Main_Cable_{x_off}"
                main_cable.scale = (0.02, 5.0, 0.02)
                bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
                add_material(main_cable, f"MC_Mat_{x_off}", (0.2, 0.2, 0.2), roughness=0.5)

                # Vertical suspenders
                for i in range(5):
                    y = -2.0 + i * 1.0
                    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x_off, y, 1.8))
                    susp = bpy.context.active_object
                    susp.name = f"Susp_{x_off}_{i}"
                    susp.scale = (0.015, 0.015, 1.8)
                    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
                    add_material(susp, f"S_Mat_{x_off}_{i}", (0.25, 0.25, 0.25), roughness=0.5)

            # Pylons / supports
            for y_off in [-2.0, 2.0]:
                bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, y_off, -0.5))
                pylon = bpy.context.active_object
                pylon.name = f"Pylon_{'B' if y_off < 0 else 'F'}"
                pylon.scale = (0.5, 0.3, 0.5)
                bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
                add_material(pylon, f"Pyl_Mat_{y_off}", (0.35, 0.35, 0.37), roughness=0.7)
        """) + self._footer()

    def _pyramid_script(self) -> str:
        return self._header() + textwrap.dedent("""\
            # --- PYRAMID ---
            bpy.ops.mesh.primitive_cone_add(radius1=2.0, radius2=0, depth=2.5, vertices=4, location=(0, 0, 1.25))
            pyramid = bpy.context.active_object
            pyramid.name = "Pyramid"
            pyramid.rotation_euler = (0, 0, math.radians(45))
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
            if SHADING_SMOOTH:
                bpy.ops.object.shade_smooth()
            add_material(pyramid, "Pyr_Mat", (0.8, 0.7, 0.45), roughness=0.8)

            # Base platform
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.05))
            platform = bpy.context.active_object
            platform.name = "Base_Platform"
            platform.scale = (2.5, 2.5, 0.1)
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            add_material(platform, "Plat_Mat", (0.75, 0.65, 0.4), roughness=0.85)

            # Entrance
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 1.4, 0.4))
            entrance = bpy.context.active_object
            entrance.name = "Entrance"
            entrance.scale = (0.3, 0.05, 0.4)
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            add_material(entrance, "Ent_Mat", (0.1, 0.08, 0.05), roughness=0.9)
        """) + self._footer()

    def _castle_script(self) -> str:
        return self._header() + textwrap.dedent("""\
            # --- CASTLE ---
            # Main keep
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 1.5))
            keep = bpy.context.active_object
            keep.name = "Keep"
            keep.scale = (1.5, 1.5, 3.0)
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            add_material(keep, "Keep_Mat", (0.5, 0.48, 0.45), roughness=0.8)

            # Corner towers
            for x_off in [-1.2, 1.2]:
                for y_off in [-1.2, 1.2]:
                    bpy.ops.mesh.primitive_cylinder_add(radius=0.4, depth=4.0, vertices=16, location=(x_off, y_off, 2.0))
                    tower = bpy.context.active_object
                    tower.name = f"Tower_{x_off}_{y_off}"
                    if SHADING_SMOOTH:
                        bpy.ops.object.shade_smooth()
                    add_material(tower, f"Tow_Mat_{x_off}_{y_off}", (0.5, 0.48, 0.45), roughness=0.8)

                    # Tower roof (cone)
                    bpy.ops.mesh.primitive_cone_add(radius1=0.45, radius2=0, depth=0.8, vertices=16, location=(x_off, y_off, 4.4))
                    roof = bpy.context.active_object
                    roof.name = f"Tower_Roof_{x_off}_{y_off}"
                    if SHADING_SMOOTH:
                        bpy.ops.object.shade_smooth()
                    add_material(roof, f"Roof_Mat_{x_off}_{y_off}", (0.4, 0.1, 0.05), roughness=0.7)

            # Walls connecting towers
            for angle in [0, 90, 180, 270]:
                rad = math.radians(angle)
                x = math.cos(rad) * 1.2
                y = math.sin(rad) * 1.2
                bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, y, 1.5))
                wall = bpy.context.active_object
                wall.name = f"Wall_{angle}"
                if abs(math.cos(rad)) > 0.5:
                    wall.scale = (0.1, 2.5, 3.0)
                else:
                    wall.scale = (2.5, 0.1, 3.0)
                bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
                add_material(wall, f"Wall_Mat_{angle}", (0.48, 0.46, 0.43), roughness=0.85)

            # Gate
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -1.3, 0.5))
            gate = bpy.context.active_object
            gate.name = "Gate"
            gate.scale = (0.3, 0.05, 0.8)
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            add_material(gate, "Gate_Mat", (0.2, 0.1, 0.05), roughness=0.8)
        """) + self._footer()

    def _generic_building_script(self, entity: str) -> str:
        safe_entity = entity.replace("'", "").replace('"', "")[:80]
        return self._header() + textwrap.dedent(f"""\
            # --- GENERIC BUILDING: {safe_entity} ---
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 1.5))
            building = bpy.context.active_object
            building.name = "Building"
            building.scale = (1.5, 2.0, 3.0)
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            if BEVEL_SEGMENTS > 0:
                bpy.ops.object.modifier_add(type='BEVEL')
                building.modifiers["Bevel"].segments = BEVEL_SEGMENTS
                bpy.ops.object.modifier_apply(modifier="Bevel")
            add_material(building, "Bldg_Mat", (0.7, 0.7, 0.75), metallic=0.3, roughness=0.3)

            # Roof
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 3.1))
            roof = bpy.context.active_object
            roof.name = "Roof"
            roof.scale = (1.6, 2.1, 0.1)
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            add_material(roof, "Roof_Mat", (0.3, 0.3, 0.35), roughness=0.5)

            # Door
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 1.0, 0.4))
            door = bpy.context.active_object
            door.name = "Door"
            door.scale = (0.25, 0.02, 0.6)
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            add_material(door, "Door_Mat", (0.2, 0.1, 0.05), roughness=0.6)

            # Windows
            for z in [1.0, 2.0]:
                for x_off in [-0.5, 0.5]:
                    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x_off, 1.0, z))
                    win = bpy.context.active_object
                    win.name = f"Win_{x_off}_{z}"
                    win.scale = (0.2, 0.02, 0.2)
                    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
                    add_material(win, f"WM_{x_off}_{z}", (0.2, 0.4, 0.6), metallic=0.2, roughness=0.1)
        """) + self._footer()
