"""Vehicle generation strategy.

Generates simplified vehicle approximations: planes, cars, rockets, ships, etc.
"""

from __future__ import annotations

import textwrap
from .base import GenerationStrategy


class VehicleStrategy(GenerationStrategy):
    category = "vehicle"

    def get_limitations(self, entity: str) -> list[str]:
        return [
            f"'{entity}' is a simplified geometric approximation, not a detailed engineering model.",
            "Internal components, detailed surface features, and accurate proportions are not represented.",
        ]

    def build_script(self, entity: str, description: str, quality: str) -> str:
        entity_lower = entity.lower().strip()

        if "747" in entity_lower or "boeing" in entity_lower or "airplane" in entity_lower or "jet" in entity_lower:
            return self._airplane_script()
        elif "car" in entity_lower or "automobile" in entity_lower or "vehicle" in entity_lower:
            return self._car_script()
        elif "rocket" in entity_lower or "spaceship" in entity_lower or "spacecraft" in entity_lower:
            return self._rocket_script()
        elif "ship" in entity_lower or "boat" in entity_lower or "vessel" in entity_lower:
            return self._ship_script()
        elif "helicopter" in entity_lower or "chopper" in entity_lower:
            return self._helicopter_script()
        elif "tank" in entity_lower:
            return self._tank_script()
        else:
            return self._generic_vehicle_script(entity)

    def _airplane_script(self) -> str:
        return self._header() + textwrap.dedent("""\
            # --- AIRPLANE (BOEING 747 STYLE) ---
            # Fuselage
            bpy.ops.mesh.primitive_cylinder_add(radius=0.5, depth=6.0, vertices=24, location=(0, 0, 0))
            fuselage = bpy.context.active_object
            fuselage.name = "Fuselage"
            fuselage.rotation_euler = (math.pi / 2, 0, 0)
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
            if SHADING_SMOOTH:
                bpy.ops.object.shade_smooth()
            add_material(fuselage, "Fus_Mat", (0.9, 0.9, 0.95), metallic=0.3, roughness=0.3)

            # Nose cone
            bpy.ops.mesh.primitive_cone_add(radius1=0.5, radius2=0, depth=1.0, vertices=24, location=(0, 3.5, 0))
            nose = bpy.context.active_object
            nose.name = "Nose"
            nose.rotation_euler = (math.pi, 0, 0)
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
            if SHADING_SMOOTH:
                bpy.ops.object.shade_smooth()
            add_material(nose, "Nose_Mat", (0.85, 0.85, 0.9), metallic=0.3, roughness=0.3)

            # Tail cone
            bpy.ops.mesh.primitive_cone_add(radius1=0.5, radius2=0.1, depth=1.5, vertices=24, location=(0, -3.75, 0))
            tail = bpy.context.active_object
            tail.name = "Tail_Cone"
            tail.rotation_euler = (0, 0, 0)
            if SHADING_SMOOTH:
                bpy.ops.object.shade_smooth()
            add_material(tail, "Tail_Mat", (0.9, 0.9, 0.95), metallic=0.3, roughness=0.3)

            # Main wings
            for sign in [1, -1]:
                bpy.ops.mesh.primitive_cube_add(size=1.0, location=(sign * 2.0, 0, -0.1))
                wing = bpy.context.active_object
                wing.name = f"Main_Wing_{'R' if sign > 0 else 'L'}"
                wing.scale = (2.5, 1.2, 0.08)
                bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
                wing.rotation_euler = (0, 0, math.radians(sign * 3))
                if BEVEL_SEGMENTS > 0:
                    bpy.ops.object.modifier_add(type='BEVEL')
                    wing.modifiers["Bevel"].segments = BEVEL_SEGMENTS
                    bpy.ops.object.modifier_apply(modifier="Bevel")
                add_material(wing, f"Wing_Mat_{sign}", (0.8, 0.8, 0.85), metallic=0.2, roughness=0.4)

            # Tail wings (horizontal stabilizer)
            for sign in [1, -1]:
                bpy.ops.mesh.primitive_cube_add(size=1.0, location=(sign * 1.0, -3.5, 0))
                tail_wing = bpy.context.active_object
                tail_wing.name = f"Tail_Wing_{'R' if sign > 0 else 'L'}"
                tail_wing.scale = (1.2, 0.5, 0.06)
                bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
                add_material(tail_wing, f"TW_Mat_{sign}", (0.85, 0.85, 0.9), metallic=0.2, roughness=0.4)

            # Vertical stabilizer
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -3.5, 0.5))
            vstab = bpy.context.active_object
            vstab.name = "Vertical_Stabilizer"
            vstab.scale = (0.06, 0.8, 0.7)
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            add_material(vstab, "VStab_Mat", (0.85, 0.85, 0.9), metallic=0.2, roughness=0.4)

            # Engines (4)
            for x_sign in [1, -1]:
                for y_off in [0.5, -0.5]:
                    bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=0.8, vertices=16, location=(x_sign * 1.8, y_off, -0.3))
                    engine = bpy.context.active_object
                    engine.name = f"Engine_{x_sign}_{y_off}"
                    engine.rotation_euler = (math.pi / 2, 0, 0)
                    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
                    if SHADING_SMOOTH:
                        bpy.ops.object.shade_smooth()
                    add_material(engine, f"Eng_Mat_{x_sign}_{y_off}", (0.3, 0.3, 0.35), metallic=0.7, roughness=0.3)
        """) + self._footer()

    def _car_script(self) -> str:
        return self._header() + textwrap.dedent("""\
            # --- CAR ---
            # Body
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.5))
            body = bpy.context.active_object
            body.name = "Car_Body"
            body.scale = (1.0, 2.5, 0.5)
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            if BEVEL_SEGMENTS > 0:
                bpy.ops.object.modifier_add(type='BEVEL')
                body.modifiers["Bevel"].segments = BEVEL_SEGMENTS
                bpy.ops.object.modifier_apply(modifier="Bevel")
            add_material(body, "Body_Mat", (0.8, 0.1, 0.1), metallic=0.5, roughness=0.3)

            # Cabin
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.2, 1.1))
            cabin = bpy.context.active_object
            cabin.name = "Cabin"
            cabin.scale = (0.8, 1.5, 0.4)
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            if BEVEL_SEGMENTS > 0:
                bpy.ops.object.modifier_add(type='BEVEL')
                cabin.modifiers["Bevel"].segments = BEVEL_SEGMENTS
                bpy.ops.object.modifier_apply(modifier="Bevel")
            add_material(cabin, "Cabin_Mat", (0.1, 0.1, 0.15), metallic=0.2, roughness=0.1)

            # Wheels
            wheel_positions = [(-0.9, 1.5, 0.1), (0.9, 1.5, 0.1), (-0.9, -1.5, 0.1), (0.9, -1.5, 0.1)]
            for i, pos in enumerate(wheel_positions):
                bpy.ops.mesh.primitive_cylinder_add(radius=0.5, depth=0.3, vertices=20, location=pos)
                wheel = bpy.context.active_object
                wheel.name = f"Wheel_{i}"
                wheel.rotation_euler = (0, math.pi / 2, 0)
                bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
                if SHADING_SMOOTH:
                    bpy.ops.object.shade_smooth()
                add_material(wheel, f"Wheel_Mat_{i}", (0.1, 0.1, 0.1), roughness=0.8)

            # Headlights
            for x_off in [-0.6, 0.6]:
                bpy.ops.mesh.primitive_uv_sphere_add(radius=0.15, segments=12, ring_count=8, location=(x_off, 2.4, 0.5))
                light = bpy.context.active_object
                light.name = f"Headlight_{'L' if x_off < 0 else 'R'}"
                if SHADING_SMOOTH:
                    bpy.ops.object.shade_smooth()
                add_material(light, f"Light_Mat_{x_off}", (1.0, 0.95, 0.7), metallic=0.1, roughness=0.1)
        """) + self._footer()

    def _rocket_script(self) -> str:
        return self._header() + textwrap.dedent("""\
            # --- ROCKET ---
            # Main body
            bpy.ops.mesh.primitive_cylinder_add(radius=0.6, depth=4.0, vertices=24, location=(0, 0, 0))
            body = bpy.context.active_object
            body.name = "Rocket_Body"
            if SHADING_SMOOTH:
                bpy.ops.object.shade_smooth()
            add_material(body, "Body_Mat", (0.9, 0.9, 0.92), metallic=0.3, roughness=0.3)

            # Nose cone
            bpy.ops.mesh.primitive_cone_add(radius1=0.6, radius2=0, depth=1.5, vertices=24, location=(0, 0, 2.75))
            nose = bpy.context.active_object
            nose.name = "Nose_Cone"
            if SHADING_SMOOTH:
                bpy.ops.object.shade_smooth()
            add_material(nose, "Nose_Mat", (0.85, 0.15, 0.15), metallic=0.2, roughness=0.4)

            # Fins
            for angle in [0, 120, 240]:
                bpy.ops.mesh.primitive_cube_add(size=1.0, location=(math.cos(math.radians(angle)) * 0.7, math.sin(math.radians(angle)) * 0.7, -1.5))
                fin = bpy.context.active_object
                fin.name = f"Fin_{angle}"
                fin.scale = (0.05, 0.5, 0.6)
                bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
                fin.rotation_euler = (0, 0, math.radians(angle))
                add_material(fin, f"Fin_Mat_{angle}", (0.7, 0.1, 0.1), roughness=0.5)

            # Engine nozzles
            for angle in [0, 120, 240]:
                x = math.cos(math.radians(angle)) * 0.25
                y = math.sin(math.radians(angle)) * 0.25
                bpy.ops.mesh.primitive_cone_add(radius1=0.2, radius2=0.1, depth=0.5, vertices=16, location=(x, y, -2.25))
                nozzle = bpy.context.active_object
                nozzle.name = f"Nozzle_{angle}"
                nozzle.rotation_euler = (math.pi, 0, 0)
                if SHADING_SMOOTH:
                    bpy.ops.object.shade_smooth()
                add_material(nozzle, f"Noz_Mat_{angle}", (0.3, 0.3, 0.3), metallic=0.8, roughness=0.4)
        """) + self._footer()

    def _ship_script(self) -> str:
        return self._header() + textwrap.dedent("""\
            # --- SHIP ---
            # Hull
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0))
            hull = bpy.context.active_object
            hull.name = "Hull"
            hull.scale = (1.0, 4.0, 0.6)
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            if BEVEL_SEGMENTS > 0:
                bpy.ops.object.modifier_add(type='BEVEL')
                hull.modifiers["Bevel"].segments = BEVEL_SEGMENTS
                bpy.ops.object.modifier_apply(modifier="Bevel")
            add_material(hull, "Hull_Mat", (0.2, 0.3, 0.5), roughness=0.6)

            # Bow (tapered front)
            bpy.ops.mesh.primitive_cone_add(radius1=0.5, radius2=0, depth=1.5, vertices=16, location=(0, 2.75, 0))
            bow = bpy.context.active_object
            bow.name = "Bow"
            bow.rotation_euler = (math.radians(90), 0, 0)
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
            if SHADING_SMOOTH:
                bpy.ops.object.shade_smooth()
            add_material(bow, "Bow_Mat", (0.2, 0.3, 0.5), roughness=0.6)

            # Bridge / superstructure
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.5, 0.8))
            bridge = bpy.context.active_object
            bridge.name = "Bridge"
            bridge.scale = (0.7, 1.5, 0.4)
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            add_material(bridge, "Bridge_Mat", (0.9, 0.9, 0.9), roughness=0.4)

            # Smokestack
            bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=1.0, vertices=16, location=(0, -1.0, 1.4))
            stack = bpy.context.active_object
            stack.name = "Smokestack"
            if SHADING_SMOOTH:
                bpy.ops.object.shade_smooth()
            add_material(stack, "Stack_Mat", (0.15, 0.15, 0.15), roughness=0.7)
        """) + self._footer()

    def _helicopter_script(self) -> str:
        return self._header() + textwrap.dedent("""\
            # --- HELICOPTER ---
            # Main body
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.8, segments=24, ring_count=16, location=(0, 0, 0))
            body = bpy.context.active_object
            body.name = "Heli_Body"
            body.scale = (0.8, 2.0, 0.7)
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            if SHADING_SMOOTH:
                bpy.ops.object.shade_smooth()
            add_material(body, "Body_Mat", (0.1, 0.3, 0.5), metallic=0.3, roughness=0.4)

            # Tail boom
            bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=3.0, vertices=16, location=(0, -2.0, 0.1))
            tail = bpy.context.active_object
            tail.name = "Tail_Boom"
            tail.rotation_euler = (math.pi / 2, 0, 0)
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
            if SHADING_SMOOTH:
                bpy.ops.object.shade_smooth()
            add_material(tail, "Tail_Mat", (0.1, 0.3, 0.5), roughness=0.4)

            # Main rotor
            bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=3.5, vertices=8, location=(0, 0, 1.0))
            rotor = bpy.context.active_object
            rotor.name = "Main_Rotor"
            rotor.rotation_euler = (0, math.pi / 2, 0)
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
            add_material(rotor, "Rotor_Mat", (0.2, 0.2, 0.2), roughness=0.6)

            # Rotor hub
            bpy.ops.mesh.primitive_cylinder_add(radius=0.1, depth=0.3, vertices=12, location=(0, 0, 0.9))
            hub = bpy.context.active_object
            hub.name = "Rotor_Hub"
            if SHADING_SMOOTH:
                bpy.ops.object.shade_smooth()
            add_material(hub, "Hub_Mat", (0.3, 0.3, 0.3), metallic=0.5, roughness=0.4)

            # Tail rotor
            bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=0.8, vertices=8, location=(0.15, -3.4, 0.1))
            trot = bpy.context.active_object
            trot.name = "Tail_Rotor"
            add_material(trot, "TR_Mat", (0.2, 0.2, 0.2), roughness=0.6)

            # Skids
            for x_off in [-0.5, 0.5]:
                bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=2.0, vertices=8, location=(x_off, 0, -0.8))
                skid = bpy.context.active_object
                skid.name = f"Skid_{'L' if x_off < 0 else 'R'}"
                skid.rotation_euler = (math.pi / 2, 0, 0)
                bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
                add_material(skid, f"Skid_Mat_{x_off}", (0.3, 0.3, 0.3), metallic=0.6, roughness=0.4)
        """) + self._footer()

    def _tank_script(self) -> str:
        return self._header() + textwrap.dedent("""\
            # --- TANK ---
            # Hull
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.5))
            hull = bpy.context.active_object
            hull.name = "Tank_Hull"
            hull.scale = (1.2, 3.0, 0.4)
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            if BEVEL_SEGMENTS > 0:
                bpy.ops.object.modifier_add(type='BEVEL')
                hull.modifiers["Bevel"].segments = BEVEL_SEGMENTS
                bpy.ops.object.modifier_apply(modifier="Bevel")
            add_material(hull, "Hull_Mat", (0.3, 0.35, 0.2), roughness=0.7)

            # Turret
            bpy.ops.mesh.primitive_cylinder_add(radius=0.8, depth=0.5, vertices=20, location=(0, 0.2, 1.0))
            turret = bpy.context.active_object
            turret.name = "Turret"
            if SHADING_SMOOTH:
                bpy.ops.object.shade_smooth()
            add_material(turret, "Turret_Mat", (0.3, 0.35, 0.2), roughness=0.7)

            # Gun barrel
            bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=2.5, vertices=16, location=(0, 2.0, 1.0))
            barrel = bpy.context.active_object
            barrel.name = "Gun_Barrel"
            barrel.rotation_euler = (math.pi / 2, 0, 0)
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
            if SHADING_SMOOTH:
                bpy.ops.object.shade_smooth()
            add_material(barrel, "Barrel_Mat", (0.2, 0.2, 0.15), metallic=0.5, roughness=0.5)

            # Wheels / road wheels
            for i in range(5):
                y = -1.2 + i * 0.6
                for x_off in [-0.9, 0.9]:
                    bpy.ops.mesh.primitive_cylinder_add(radius=0.35, depth=0.2, vertices=16, location=(x_off, y, 0.1))
                    wheel = bpy.context.active_object
                    wheel.name = f"Wheel_{i}_{x_off}"
                    wheel.rotation_euler = (0, math.pi / 2, 0)
                    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
                    if SHADING_SMOOTH:
                        bpy.ops.object.shade_smooth()
                    add_material(wheel, f"W_Mat_{i}_{x_off}", (0.15, 0.15, 0.1), roughness=0.8)
        """) + self._footer()

    def _generic_vehicle_script(self, entity: str) -> str:
        safe_entity = entity.replace("'", "").replace('"', "")[:80]
        return self._header() + textwrap.dedent(f"""\
            # --- GENERIC VEHICLE: {safe_entity} ---
            # Body
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.5))
            body = bpy.context.active_object
            body.name = "Vehicle_Body"
            body.scale = (0.8, 2.0, 0.5)
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            if BEVEL_SEGMENTS > 0:
                bpy.ops.object.modifier_add(type='BEVEL')
                body.modifiers["Bevel"].segments = BEVEL_SEGMENTS
                bpy.ops.object.modifier_apply(modifier="Bevel")
            add_material(body, "Body_Mat", (0.4, 0.4, 0.5), metallic=0.4, roughness=0.4)

            # Wheels
            for i, pos in enumerate([(-0.7, 0.7, 0.1), (0.7, 0.7, 0.1), (-0.7, -0.7, 0.1), (0.7, -0.7, 0.1)]):
                bpy.ops.mesh.primitive_cylinder_add(radius=0.35, depth=0.2, vertices=16, location=pos)
                wheel = bpy.context.active_object
                wheel.name = f"Wheel_{i}"
                wheel.rotation_euler = (0, math.pi / 2, 0)
                bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
                if SHADING_SMOOTH:
                    bpy.ops.object.shade_smooth()
                add_material(wheel, f"W_Mat_{i}", (0.1, 0.1, 0.1), roughness=0.8)
        """) + self._footer()
