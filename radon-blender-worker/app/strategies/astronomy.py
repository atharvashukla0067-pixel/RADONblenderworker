"""Astronomy generation strategy.

Generates celestial body approximations: planets, stars, moons, rings, etc.
"""

from __future__ import annotations

import textwrap
from .base import GenerationStrategy


class AstronomyStrategy(GenerationStrategy):
    category = "astronomy"

    def get_limitations(self, entity: str) -> list[str]:
        return [
            f"'{entity}' is a simplified geometric approximation, not a scientifically accurate model.",
            "Surface features, atmospheric effects, and scale are not represented accurately.",
            "For verified astronomical models, consult NASA or ESA visualization resources.",
        ]

    def build_script(self, entity: str, description: str, quality: str) -> str:
        entity_lower = entity.lower().strip()

        if "saturn" in entity_lower:
            return self._saturn_script()
        elif "earth" in entity_lower or "planet earth" in entity_lower:
            return self._earth_script()
        elif "mars" in entity_lower:
            return self._mars_script()
        elif "jupiter" in entity_lower:
            return self._jupiter_script()
        elif "sun" in entity_lower or "star" in entity_lower:
            return self._sun_script()
        elif "moon" in entity_lower or "luna" in entity_lower:
            return self._moon_script()
        else:
            return self._generic_planet_script(entity)

    def _saturn_script(self) -> str:
        return self._header() + textwrap.dedent("""\
            # --- SATURN WITH RINGS ---
            bpy.ops.mesh.primitive_uv_sphere_add(radius=1.5, segments=48, ring_count=24, location=(0, 0, 0))
            saturn = bpy.context.active_object
            saturn.name = "Saturn"
            if SHADING_SMOOTH:
                bpy.ops.object.shade_smooth()
            add_material(saturn, "Saturn_Mat", (0.8, 0.7, 0.5), metallic=0.1, roughness=0.6)

            if SUBDIV_LEVEL > 0:
                mod = saturn.modifiers.new(name="Subsurf", type='SUBSURF')
                mod.levels = SUBDIV_LEVEL
                bpy.ops.object.modifier_apply(modifier=mod.name)

            # Rings (torus)
            bpy.ops.mesh.primitive_torus_add(major_radius=2.5, minor_radius=0.15, major_segments=64, minor_segments=12, location=(0, 0, 0))
            ring1 = bpy.context.active_object
            ring1.name = "Ring_Inner"
            ring1.scale = (1, 1, 0.05)
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            if SHADING_SMOOTH:
                bpy.ops.object.shade_smooth()
            add_material(ring1, "Ring1_Mat", (0.7, 0.65, 0.55), roughness=0.7)

            bpy.ops.mesh.primitive_torus_add(major_radius=3.0, minor_radius=0.12, major_segments=64, minor_segments=12, location=(0, 0, 0))
            ring2 = bpy.context.active_object
            ring2.name = "Ring_Outer"
            ring2.scale = (1, 1, 0.05)
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            if SHADING_SMOOTH:
                bpy.ops.object.shade_smooth()
            add_material(ring2, "Ring2_Mat", (0.6, 0.55, 0.45), roughness=0.7)

            # Tilt the rings
            for ring in [ring1, ring2]:
                ring.rotation_euler = (math.radians(20), 0, 0)
        """) + self._footer()

    def _earth_script(self) -> str:
        return self._header() + textwrap.dedent("""\
            # --- EARTH ---
            bpy.ops.mesh.primitive_uv_sphere_add(radius=1.5, segments=48, ring_count=24, location=(0, 0, 0))
            earth = bpy.context.active_object
            earth.name = "Earth"
            if SHADING_SMOOTH:
                bpy.ops.object.shade_smooth()
            add_material(earth, "Earth_Mat", (0.15, 0.3, 0.6), metallic=0.0, roughness=0.5)

            if SUBDIV_LEVEL > 0:
                mod = earth.modifiers.new(name="Subsurf", type='SUBSURF')
                mod.levels = SUBDIV_LEVEL
                bpy.ops.object.modifier_apply(modifier=mod.name)

            # Add simple "continent" patches
            import random
            random.seed(7)
            for i in range(8):
                angle = random.uniform(0, 6.28)
                elev = random.uniform(-0.8, 0.8)
                r = 1.5
                x = r * math.cos(angle) * math.cos(elev)
                y = r * math.sin(angle) * math.cos(elev)
                z = r * math.sin(elev)
                bpy.ops.mesh.primitive_uv_sphere_add(radius=random.uniform(0.3, 0.6), segments=12, ring_count=8, location=(x, y, z))
                continent = bpy.context.active_object
                continent.name = f"Continent_{i}"
                if SHADING_SMOOTH:
                    bpy.ops.object.shade_smooth()
                add_material(continent, f"Cont_Mat_{i}", (0.2, 0.5, 0.15), roughness=0.8)

            # Moon
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.3, segments=16, ring_count=12, location=(3, 0, 0))
            moon = bpy.context.active_object
            moon.name = "Moon"
            if SHADING_SMOOTH:
                bpy.ops.object.shade_smooth()
            add_material(moon, "Moon_Mat", (0.6, 0.6, 0.6), roughness=0.9)
        """) + self._footer()

    def _mars_script(self) -> str:
        return self._header() + textwrap.dedent("""\
            # --- MARS ---
            bpy.ops.mesh.primitive_uv_sphere_add(radius=1.2, segments=40, ring_count=20, location=(0, 0, 0))
            mars = bpy.context.active_object
            mars.name = "Mars"
            if SHADING_SMOOTH:
                bpy.ops.object.shade_smooth()
            add_material(mars, "Mars_Mat", (0.7, 0.3, 0.15), roughness=0.85)

            if SUBDIV_LEVEL > 0:
                mod = mars.modifiers.new(name="Subsurf", type='SUBSURF')
                mod.levels = SUBDIV_LEVEL
                bpy.ops.object.modifier_apply(modifier=mod.name)

            # Polar ice caps
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.3, segments=16, ring_count=8, location=(0, 0, 1.1))
            cap_n = bpy.context.active_object
            cap_n.name = "North_Polar_Cap"
            if SHADING_SMOOTH:
                bpy.ops.object.shade_smooth()
            add_material(cap_n, "CapN_Mat", (0.9, 0.9, 0.9), roughness=0.5)

            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.25, segments=16, ring_count=8, location=(0, 0, -1.1))
            cap_s = bpy.context.active_object
            cap_s.name = "South_Polar_Cap"
            if SHADING_SMOOTH:
                bpy.ops.object.shade_smooth()
            add_material(cap_s, "CapS_Mat", (0.85, 0.85, 0.85), roughness=0.5)
        """) + self._footer()

    def _jupiter_script(self) -> str:
        return self._header() + textwrap.dedent("""\
            # --- JUPITER ---
            bpy.ops.mesh.primitive_uv_sphere_add(radius=2.0, segments=48, ring_count=24, location=(0, 0, 0))
            jupiter = bpy.context.active_object
            jupiter.name = "Jupiter"
            if SHADING_SMOOTH:
                bpy.ops.object.shade_smooth()
            add_material(jupiter, "Jupiter_Mat", (0.8, 0.6, 0.4), roughness=0.7)

            if SUBDIV_LEVEL > 0:
                mod = jupiter.modifiers.new(name="Subsurf", type='SUBSURF')
                mod.levels = SUBDIV_LEVEL
                bpy.ops.object.modifier_apply(modifier=mod.name)

            # Bands (flattened toruses)
            band_colors = [(0.7, 0.5, 0.3), (0.85, 0.7, 0.5), (0.6, 0.4, 0.25)]
            for i, z_off in enumerate([-1.2, -0.5, 0.2, 0.9]):
                bpy.ops.mesh.primitive_torus_add(major_radius=1.8, minor_radius=0.3, major_segments=48, minor_segments=8, location=(0, 0, z_off))
                band = bpy.context.active_object
                band.name = f"Band_{i}"
                band.scale = (1, 1, 0.1)
                bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
                if SHADING_SMOOTH:
                    bpy.ops.object.shade_smooth()
                add_material(band, f"Band_Mat_{i}", band_colors[i % len(band_colors)], roughness=0.7)

            # Great Red Spot
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.4, segments=16, ring_count=12, location=(1.5, 0.3, -0.3))
            grs = bpy.context.active_object
            grs.name = "Great_Red_Spot"
            if SHADING_SMOOTH:
                bpy.ops.object.shade_smooth()
            add_material(grs, "GRS_Mat", (0.7, 0.2, 0.1), roughness=0.8)
        """) + self._footer()

    def _sun_script(self) -> str:
        return self._header() + textwrap.dedent("""\
            # --- SUN / STAR ---
            bpy.ops.mesh.primitive_uv_sphere_add(radius=2.0, segments=48, ring_count=24, location=(0, 0, 0))
            sun = bpy.context.active_object
            sun.name = "Sun"
            if SHADING_SMOOTH:
                bpy.ops.object.shade_smooth()
            add_material(sun, "Sun_Mat", (1.0, 0.85, 0.2), metallic=0.0, roughness=0.2)

            # Emission for glow effect
            mat = sun.data.materials[0]
            bsdf = mat.node_tree.nodes.get("Principled BSDF")
            if bsdf and "Emission" in bsdf.inputs:
                bsdf.inputs["Emission"].default_value = (1.0, 0.7, 0.1, 1.0)
                if "Emission Strength" in bsdf.inputs:
                    bsdf.inputs["Emission Strength"].default_value = 2.0

            if SUBDIV_LEVEL > 0:
                mod = sun.modifiers.new(name="Subsurf", type='SUBSURF')
                mod.levels = SUBDIV_LEVEL
                bpy.ops.object.modifier_apply(modifier=mod.name)

            # Solar flares (cones)
            import random
            random.seed(99)
            for i in range(8):
                angle = random.uniform(0, 6.28)
                elev = random.uniform(-0.5, 0.5)
                x = 2.2 * math.cos(angle) * math.cos(elev)
                y = 2.2 * math.sin(angle) * math.cos(elev)
                z = 2.2 * math.sin(elev)
                bpy.ops.mesh.primitive_cone_add(radius1=0.2, radius2=0, depth=0.5, vertices=8, location=(x, y, z))
                flare = bpy.context.active_object
                flare.name = f"Solar_Flare_{i}"
                flare.rotation_euler = (0, math.atan2(math.sqrt(x**2+y**2), z), math.atan2(y, x))
                if SHADING_SMOOTH:
                    bpy.ops.object.shade_smooth()
                add_material(flare, f"Flare_Mat_{i}", (1.0, 0.5, 0.1), roughness=0.3)
        """) + self._footer()

    def _moon_script(self) -> str:
        return self._header() + textwrap.dedent("""\
            # --- MOON ---
            bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, segments=40, ring_count=20, location=(0, 0, 0))
            moon = bpy.context.active_object
            moon.name = "Moon"
            if SHADING_SMOOTH:
                bpy.ops.object.shade_smooth()
            add_material(moon, "Moon_Mat", (0.5, 0.5, 0.5), roughness=0.95)

            # Craters
            import random
            random.seed(13)
            for i in range(15):
                angle = random.uniform(0, 6.28)
                elev = random.uniform(-0.8, 0.8)
                r = 0.98
                x = r * math.cos(angle) * math.cos(elev)
                y = r * math.sin(angle) * math.cos(elev)
                z = r * math.sin(elev)
                cr = random.uniform(0.08, 0.25)
                bpy.ops.mesh.primitive_uv_sphere_add(radius=cr, segments=10, ring_count=6, location=(x, y, z))
                crater = bpy.context.active_object
                crater.name = f"Crater_{i}"
                if SHADING_SMOOTH:
                    bpy.ops.object.shade_smooth()
                add_material(crater, f"Crater_Mat_{i}", (0.35, 0.35, 0.35), roughness=0.95)

            if SUBDIV_LEVEL > 0:
                mod = moon.modifiers.new(name="Subsurf", type='SUBSURF')
                mod.levels = SUBDIV_LEVEL
                bpy.ops.object.modifier_apply(modifier=mod.name)
        """) + self._footer()

    def _generic_planet_script(self, entity: str) -> str:
        safe_entity = entity.replace("'", "").replace('"', "")[:80]
        return self._header() + textwrap.dedent(f"""\
            # --- GENERIC CELESTIAL BODY: {safe_entity} ---
            bpy.ops.mesh.primitive_uv_sphere_add(radius=1.5, segments=32, ring_count=16, location=(0, 0, 0))
            body = bpy.context.active_object
            body.name = "Celestial_Body"
            if SHADING_SMOOTH:
                bpy.ops.object.shade_smooth()
            add_material(body, "Body_Mat", (0.5, 0.4, 0.3), roughness=0.7)

            if SUBDIV_LEVEL > 0:
                mod = body.modifiers.new(name="Subsurf", type='SUBSURF')
                mod.levels = SUBDIV_LEVEL
                bpy.ops.object.modifier_apply(modifier=mod.name)

            # Optional ring
            bpy.ops.mesh.primitive_torus_add(major_radius=2.2, minor_radius=0.1, major_segments=48, minor_segments=8, location=(0, 0, 0))
            ring = bpy.context.active_object
            ring.name = "Ring"
            ring.scale = (1, 1, 0.05)
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            ring.rotation_euler = (math.radians(15), 0, 0)
            if SHADING_SMOOTH:
                bpy.ops.object.shade_smooth()
            add_material(ring, "Ring_Mat", (0.6, 0.55, 0.45), roughness=0.7)
        """) + self._footer()
