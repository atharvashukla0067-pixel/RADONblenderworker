"""Anatomy generation strategy.

Generates approximate anatomical structures (heart, brain, kidney, etc.)
using procedural geometry. NOT medically accurate — these are simplified
visual approximations.
"""

from __future__ import annotations

import textwrap
from .base import GenerationStrategy


class AnatomyStrategy(GenerationStrategy):
    category = "anatomy"

    def get_limitations(self, entity: str) -> list[str]:
        return [
            f"'{entity}' is a simplified geometric approximation, NOT a medically accurate model.",
            "Internal structures, vasculature, and tissue layers are not represented.",
            "Proportions are approximate and should not be used for medical/educational reference.",
            "For verified anatomical models, consult a medical 3D model database.",
        ]

    def build_script(self, entity: str, description: str, quality: str) -> str:
        entity_lower = entity.lower().strip()
        # Route to specific anatomical generator based on entity
        if "heart" in entity_lower:
            return self._heart_script()
        elif "brain" in entity_lower:
            return self._brain_script()
        elif "kidney" in entity_lower:
            return self._kidney_script()
        elif "lung" in entity_lower:
            return self._lung_script()
        elif "liver" in entity_lower:
            return self._liver_script()
        elif "skull" in entity_lower or "bone" in entity_lower:
            return self._skull_script()
        else:
            return self._generic_organ_script(entity)

    def _heart_script(self) -> str:
        return self._header() + textwrap.dedent("""\
            # --- HEART APPROXIMATION ---
            # Body: scaled UV sphere
            bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, segments=32, ring_count=16, location=(0, 0, 0))
            heart = bpy.context.active_object
            heart.name = "Heart_Body"
            heart.scale = (1.0, 0.8, 1.1)
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            if SHADING_SMOOTH:
                bpy.ops.object.shade_smooth()

            # Taper the top (atria region) by editing the top vertices
            for v in heart.data.vertices:
                if v.co.z > 0.5:
                    factor = (v.co.z - 0.5) / 0.6
                    v.co.x *= (1.0 - 0.3 * min(factor, 1.0))
                    v.co.y *= (1.0 - 0.2 * min(factor, 1.0))

            # Point the bottom (apex)
            for v in heart.data.vertices:
                if v.co.z < -0.3:
                    factor = (-v.co.z - 0.3) / 0.8
                    v.co.x *= (1.0 - 0.4 * min(factor, 1.0))
                    v.co.y *= (1.0 - 0.4 * min(factor, 1.0))

            add_material(heart, "Heart_Tissue", (0.6, 0.08, 0.08), metallic=0.0, roughness=0.7)

            if SUBDIV_LEVEL > 0:
                mod = heart.modifiers.new(name="Subsurf", type='SUBSURF')
                mod.levels = SUBDIV_LEVEL
                mod.render_levels = SUBDIV_LEVEL
                bpy.ops.object.modifier_apply(modifier=mod.name)

            # Aorta (cylinder exiting top)
            bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=0.8, vertices=16, location=(0.2, 0, 0.9))
            aorta = bpy.context.active_object
            aorta.name = "Aorta"
            aorta.rotation_euler = (0.3, 0, 0.2)
            if SHADING_SMOOTH:
                bpy.ops.object.shade_smooth()
            add_material(aorta, "Aorta_Mat", (0.5, 0.05, 0.05), roughness=0.6)

            # Pulmonary trunk
            bpy.ops.mesh.primitive_cylinder_add(radius=0.1, depth=0.6, vertices=16, location=(-0.15, 0.1, 0.8))
            pulm = bpy.context.active_object
            pulm.name = "Pulmonary_Trunk"
            pulm.rotation_euler = (0.2, 0, -0.1)
            if SHADING_SMOOTH:
                bpy.ops.object.shade_smooth()
            add_material(pulm, "Pulm_Mat", (0.4, 0.1, 0.1), roughness=0.6)

            # Superior vena cava
            bpy.ops.mesh.primitive_cylinder_add(radius=0.1, depth=0.5, vertices=16, location=(-0.3, 0, 0.75))
            svc = bpy.context.active_object
            svc.name = "Superior_Vena_Cava"
            svc.rotation_euler = (0.1, 0, -0.15)
            if SHADING_SMOOTH:
                bpy.ops.object.shade_smooth()
            add_material(svc, "SVC_Mat", (0.3, 0.08, 0.15), roughness=0.6)

            # Left ventricle bulge
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.35, segments=16, ring_count=12, location=(0.5, 0.1, -0.3))
            lv = bpy.context.active_object
            lv.name = "Left_Ventricle_Bulge"
            if SHADING_SMOOTH:
                bpy.ops.object.shade_smooth()
            add_material(lv, "LV_Mat", (0.55, 0.06, 0.06), roughness=0.7)
        """) + self._footer()

    def _brain_script(self) -> str:
        return self._header() + textwrap.dedent("""\
            # --- BRAIN APPROXIMATION ---
            # Main brain mass
            bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, segments=32, ring_count=20, location=(0, 0, 0))
            brain = bpy.context.active_object
            brain.name = "Brain_Mass"
            brain.scale = (1.1, 0.9, 0.85)
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            if SHADING_SMOOTH:
                bpy.ops.object.shade_smooth()

            # Indent the bottom (brain stem area)
            for v in brain.data.vertices:
                if v.co.z < -0.5:
                    v.co.z *= 0.6

            add_material(brain, "Brain_Tissue", (0.85, 0.75, 0.7), roughness=0.9)

            # Add surface bumps for gyrus approximation
            import random
            random.seed(42)
            for i in range(20):
                angle = random.uniform(0, 6.28)
                elev = random.uniform(-0.5, 0.7)
                r = 1.0
                x = r * math.cos(angle) * math.cos(elev)
                y = r * math.sin(angle) * math.cos(elev)
                z = r * math.sin(elev)
                bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12, segments=8, ring_count=6,
                    location=(x * 1.05, y * 0.85, z * 0.85))
                bump = bpy.context.active_object
                bump.name = f"Gyrus_{i}"
                if SHADING_SMOOTH:
                    bpy.ops.object.shade_smooth()
                add_material(bump, f"Gyrus_Mat_{i}", (0.82, 0.72, 0.68), roughness=0.9)

            # Brain stem
            bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=0.6, vertices=12, location=(0, 0, -0.7))
            stem = bpy.context.active_object
            stem.name = "Brain_Stem"
            if SHADING_SMOOTH:
                bpy.ops.object.shade_smooth()
            add_material(stem, "Stem_Mat", (0.78, 0.68, 0.63), roughness=0.85)

            if SUBDIV_LEVEL > 0:
                mod = brain.modifiers.new(name="Subsurf", type='SUBSURF')
                mod.levels = SUBDIV_LEVEL
                bpy.ops.object.modifier_apply(modifier=mod.name)
        """) + self._footer()

    def _kidney_script(self) -> str:
        return self._header() + textwrap.dedent("""\
            # --- KIDNEY APPROXIMATION ---
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.8, segments=24, ring_count=16, location=(0, 0, 0))
            kidney = bpy.context.active_object
            kidney.name = "Kidney"
            kidney.scale = (0.6, 1.2, 0.8)
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            if SHADING_SMOOTH:
                bpy.ops.object.shade_smooth()

            # Create concave indentation (hilum)
            for v in kidney.data.vertices:
                if v.co.x < -0.2 and abs(v.co.y) < 0.3:
                    v.co.x *= 0.7

            add_material(kidney, "Kidney_Tissue", (0.5, 0.15, 0.12), roughness=0.8)

            # Ureter
            bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=1.0, vertices=8, location=(-0.3, -0.6, -0.2))
            ureter = bpy.context.active_object
            ureter.name = "Ureter"
            if SHADING_SMOOTH:
                bpy.ops.object.shade_smooth()
            add_material(ureter, "Ureter_Mat", (0.4, 0.1, 0.08), roughness=0.7)

            if SUBDIV_LEVEL > 0:
                mod = kidney.modifiers.new(name="Subsurf", type='SUBSURF')
                mod.levels = SUBDIV_LEVEL
                bpy.ops.object.modifier_apply(modifier=mod.name)
        """) + self._footer()

    def _lung_script(self) -> str:
        return self._header() + textwrap.dedent("""\
            # --- LUNG APPROXIMATION ---
            # Right lung
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.7, segments=24, ring_count=16, location=(0.5, 0, 0))
            rlung = bpy.context.active_object
            rlung.name = "Right_Lung"
            rlung.scale = (0.6, 0.9, 1.3)
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            if SHADING_SMOOTH:
                bpy.ops.object.shade_smooth()
            add_material(rlung, "RLung_Mat", (0.7, 0.65, 0.6), roughness=0.85)

            # Left lung
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.65, segments=24, ring_count=16, location=(-0.5, 0, 0))
            llung = bpy.context.active_object
            llung.name = "Left_Lung"
            llung.scale = (0.55, 0.85, 1.2)
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            if SHADING_SMOOTH:
                bpy.ops.object.shade_smooth()
            add_material(llung, "LLung_Mat", (0.68, 0.63, 0.58), roughness=0.85)

            # Trachea
            bpy.ops.mesh.primitive_cylinder_add(radius=0.12, depth=0.6, vertices=12, location=(0, 0, 0.8))
            trachea = bpy.context.active_object
            trachea.name = "Trachea"
            if SHADING_SMOOTH:
                bpy.ops.object.shade_smooth()
            add_material(trachea, "Trachea_Mat", (0.6, 0.55, 0.5), roughness=0.8)

            # Bronchi
            bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=0.5, vertices=8, location=(0.25, 0, 0.4))
            rbronch = bpy.context.active_object
            rbronch.name = "Right_Bronchus"
            rbronch.rotation_euler = (0.4, 0, 0.3)
            if SHADING_SMOOTH:
                bpy.ops.object.shade_smooth()
            add_material(rbronch, "RBr_Mat", (0.58, 0.53, 0.48), roughness=0.8)

            bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=0.5, vertices=8, location=(-0.25, 0, 0.4))
            lbronch = bpy.context.active_object
            lbronch.name = "Left_Bronchus"
            lbronch.rotation_euler = (0.4, 0, -0.3)
            if SHADING_SMOOTH:
                bpy.ops.object.shade_smooth()
            add_material(lbronch, "LBr_Mat", (0.58, 0.53, 0.48), roughness=0.8)

            if SUBDIV_LEVEL > 0:
                for obj in [rlung, llung]:
                    mod = obj.modifiers.new(name="Subsurf", type='SUBSURF')
                    mod.levels = SUBDIV_LEVEL
                    bpy.context.view_layer.objects.active = obj
                    bpy.ops.object.modifier_apply(modifier=mod.name)
        """) + self._footer()

    def _liver_script(self) -> str:
        return self._header() + textwrap.dedent("""\
            # --- LIVER APPROXIMATION ---
            bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, segments=24, ring_count=16, location=(0, 0, 0))
            liver = bpy.context.active_object
            liver.name = "Liver"
            liver.scale = (1.3, 0.8, 0.5)
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            if SHADING_SMOOTH:
                bpy.ops.object.shade_smooth()

            # Flatten bottom
            for v in liver.data.vertices:
                if v.co.z < -0.1:
                    v.co.z *= 0.5

            add_material(liver, "Liver_Tissue", (0.35, 0.12, 0.08), roughness=0.8)

            # Gallbladder
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.15, segments=12, ring_count=8, location=(0.5, -0.3, -0.2))
            gb = bpy.context.active_object
            gb.name = "Gallbladder"
            gb.scale = (0.8, 1.2, 1.5)
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            if SHADING_SMOOTH:
                bpy.ops.object.shade_smooth()
            add_material(gb, "GB_Mat", (0.4, 0.35, 0.1), roughness=0.7)

            if SUBDIV_LEVEL > 0:
                mod = liver.modifiers.new(name="Subsurf", type='SUBSURF')
                mod.levels = SUBDIV_LEVEL
                bpy.ops.object.modifier_apply(modifier=mod.name)
        """) + self._footer()

    def _skull_script(self) -> str:
        return self._header() + textwrap.dedent("""\
            # --- SKULL APPROXIMATION ---
            bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, segments=32, ring_count=20, location=(0, 0, 0))
            skull = bpy.context.active_object
            skull.name = "Skull_Cranium"
            skull.scale = (1.0, 1.1, 1.0)
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            if SHADING_SMOOTH:
                bpy.ops.object.shade_smooth()
            add_material(skull, "Skull_Mat", (0.9, 0.88, 0.82), roughness=0.6)

            # Jaw
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.5, -0.6))
            jaw = bpy.context.active_object
            jaw.name = "Mandible"
            jaw.scale = (0.8, 0.5, 0.25)
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            if BEVEL_SEGMENTS > 0:
                bpy.ops.object.modifier_add(type='BEVEL')
                jaw.modifiers["Bevel"].segments = BEVEL_SEGMENTS
                bpy.ops.object.modifier_apply(modifier="Bevel")
            add_material(jaw, "Jaw_Mat", (0.88, 0.86, 0.8), roughness=0.6)

            # Eye sockets
            for x_off in [-0.35, 0.35]:
                bpy.ops.mesh.primitive_uv_sphere_add(radius=0.18, segments=16, ring_count=12, location=(x_off, -0.7, 0.1))
                socket = bpy.context.active_object
                socket.name = f"Eye_Socket_{'L' if x_off < 0 else 'R'}"
                add_material(socket, f"Socket_Mat_{x_off}", (0.05, 0.05, 0.05), roughness=0.9)

            if SUBDIV_LEVEL > 0:
                mod = skull.modifiers.new(name="Subsurf", type='SUBSURF')
                mod.levels = SUBDIV_LEVEL
                bpy.ops.object.modifier_apply(modifier=mod.name)
        """) + self._footer()

    def _generic_organ_script(self, entity: str) -> str:
        # Sanitize entity for use in Blender script (it's already validated, but double-check)
        safe_entity = entity.replace("'", "").replace('"', "")[:100]
        return self._header() + textwrap.dedent(f"""\
            # --- GENERIC ANATOMICAL ORGAN: {safe_entity} ---
            # Create a generic organ-like shape
            bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, segments=24, ring_count=16, location=(0, 0, 0))
            organ = bpy.context.active_object
            organ.name = "Organ_{safe_entity}"
            organ.scale = (1.0, 0.8, 0.7)
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            if SHADING_SMOOTH:
                bpy.ops.object.shade_smooth()
            add_material(organ, "Organ_Tissue", (0.5, 0.1, 0.1), roughness=0.75)

            # Connecting vessel
            bpy.ops.mesh.primitive_cylinder_add(radius=0.1, depth=0.6, vertices=12, location=(0, 0, 0.8))
            vessel = bpy.context.active_object
            vessel.name = "Vessel"
            if SHADING_SMOOTH:
                bpy.ops.object.shade_smooth()
            add_material(vessel, "Vessel_Mat", (0.4, 0.05, 0.05), roughness=0.6)

            if SUBDIV_LEVEL > 0:
                mod = organ.modifiers.new(name="Subsurf", type='SUBSURF')
                mod.levels = SUBDIV_LEVEL
                bpy.ops.object.modifier_apply(modifier=mod.name)
        """) + self._footer()
