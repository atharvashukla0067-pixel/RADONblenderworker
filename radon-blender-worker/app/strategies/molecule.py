"""Molecule generation strategy.

Generates 3D molecular structure approximations from entity names.
Supports common molecules (water, methane, DNA, C60/buckminsterfullerene, etc.)
and falls back to a generic atomic cluster.
"""

from __future__ import annotations

import textwrap
from .base import GenerationStrategy


class MoleculeStrategy(GenerationStrategy):
    category = "molecule"

    # Common element colors (CPK-like)
    _ELEMENT_COLORS = {
        "H": (1.0, 1.0, 1.0),
        "C": (0.2, 0.2, 0.2),
        "O": (1.0, 0.0, 0.0),
        "N": (0.0, 0.0, 0.8),
        "S": (1.0, 0.8, 0.0),
        "P": (1.0, 0.5, 0.0),
        "Fe": (1.0, 0.4, 0.2),
    }

    def get_limitations(self, entity: str) -> list[str]:
        return [
            f"'{entity}' molecular geometry is an approximation, not a verified crystallographic structure.",
            "Bond lengths and angles are simplified and may not reflect actual molecular geometry.",
            "For verified molecular data, consult PubChem, PDB, or NIST databases.",
        ]

    def build_script(self, entity: str, description: str, quality: str) -> str:
        entity_lower = entity.lower().strip()

        if "dna" in entity_lower or "double helix" in entity_lower:
            return self._dna_script()
        elif "c60" in entity_lower or "buckminster" in entity_lower or "fullerene" in entity_lower:
            return self._c60_script()
        elif "water" in entity_lower or "h2o" in entity_lower:
            return self._water_script()
        elif "methane" in entity_lower or "ch4" in entity_lower:
            return self._methane_script()
        elif "benzene" in entity_lower or "c6h6" in entity_lower:
            return self._benzene_script()
        elif "caffeine" in entity_lower:
            return self._caffeine_script()
        else:
            return self._generic_molecule_script(entity)

    def _dna_script(self) -> str:
        return self._header() + textwrap.dedent("""\
            # --- DNA DOUBLE HELIX ---
            import math
            helix_radius = 1.0
            helix_height = 6.0
            turns = 3
            base_pairs = 24
            rise = helix_height / base_pairs

            backbone_a = []
            backbone_b = []

            for i in range(base_pairs):
                t = i / base_pairs * turns * 2 * math.pi
                z = i * rise - helix_height / 2
                x_a = helix_radius * math.cos(t)
                y_a = helix_radius * math.sin(t)
                x_b = helix_radius * math.cos(t + math.pi)
                y_b = helix_radius * math.sin(t + math.pi)

                # Backbone sugar-phosphate atoms
                bpy.ops.mesh.primitive_uv_sphere_add(radius=0.3, segments=12, ring_count=8, location=(x_a, y_a, z))
                atom_a = bpy.context.active_object
                atom_a.name = f"Backbone_A_{i}"
                if SHADING_SMOOTH:
                    bpy.ops.object.shade_smooth()
                add_material(atom_a, f"BB_A_{i}", (0.2, 0.4, 0.8), roughness=0.4)

                bpy.ops.mesh.primitive_uv_sphere_add(radius=0.3, segments=12, ring_count=8, location=(x_b, y_b, z))
                atom_b = bpy.context.active_object
                atom_b.name = f"Backbone_B_{i}"
                if SHADING_SMOOTH:
                    bpy.ops.object.shade_smooth()
                add_material(atom_b, f"BB_B_{i}", (0.8, 0.3, 0.2), roughness=0.4)

                backbone_a.append((x_a, y_a, z))
                backbone_b.append((x_b, y_b, z))

                # Base pair (rungs)
                mid_x = (x_a + x_b) / 2
                mid_y = (y_a + y_b) / 2
                dist = math.sqrt((x_b - x_a)**2 + (y_b - y_a)**2)
                bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=dist * 0.85, vertices=8,
                    location=(mid_x, mid_y, z))
                rung = bpy.context.active_object
                rung.name = f"Base_Pair_{i}"
                angle = math.atan2(y_b - y_a, x_b - x_a)
                rung.rotation_euler = (0, math.pi / 2, angle)
                if SHADING_SMOOTH:
                    bpy.ops.object.shade_smooth()
                base_colors = [(0.9, 0.2, 0.2), (0.2, 0.7, 0.3), (0.3, 0.5, 0.9), (0.9, 0.8, 0.2)]
                add_material(rung, f"Rung_Mat_{i}", base_colors[i % 4], roughness=0.5)

            # Create backbone curves
            for backbone, color, name in [(backbone_a, (0.2, 0.4, 0.8), "Backbone_A"), (backbone_b, (0.8, 0.3, 0.2), "Backbone_B")]:
                for i in range(len(backbone) - 1):
                    p1 = backbone[i]
                    p2 = backbone[i + 1]
                    mid = ((p1[0]+p2[0])/2, (p1[1]+p2[1])/2, (p1[2]+p2[2])/2)
                    dist = math.sqrt(sum((a-b)**2 for a, b in zip(p1, p2)))
                    bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=dist, vertices=6, location=mid)
                    bond = bpy.context.active_object
                    bond.name = f"{name}_Bond_{i}"
                    dx, dy, dz = p2[0]-p1[0], p2[1]-p1[1], p2[2]-p1[2]
                    bond.rotation_euler = (0, math.atan2(math.sqrt(dx**2+dy**2), dz), math.atan2(dy, dx))
                    if SHADING_SMOOTH:
                        bpy.ops.object.shade_smooth()
                    add_material(bond, f"{name}_Bond_Mat_{i}", color, roughness=0.5)
        """) + self._footer()

    def _c60_script(self) -> str:
        return self._header() + textwrap.dedent("""\
            # --- C60 BUCKMINSTERFULLERENE APPROXIMATION ---
            # Using vertices of a truncated icosahedron (soccer ball pattern)
            import math

            phi = (1 + math.sqrt(5)) / 2

            # Truncated icosahedron vertices
            vertices = []
            # Generate the 60 vertices using permutations of:
            # (0, ±1, ±3*phi) and cyclic permutations
            # (±1, ±(2+phi), ±2*phi) and cyclic
            # (±phi, ±2, ±(2*phi+1)) and cyclic

            perms = [(0, 1, 3*phi), (1, 2+phi, 2*phi), (phi, 2, 2*phi+1)]
            for a, b, c in perms:
                for s1 in [1, -1]:
                    for s2 in [1, -1]:
                        for s3 in [1, -1]:
                            for perm in [(a,b,c), (b,c,a), (c,a,b)]:
                                v = (s1*perm[0], s2*perm[1], s3*perm[2])
                                if v not in vertices:
                                    vertices.append(v)

            # Scale down
            scale = 0.5
            verts = [(v[0]*scale, v[1]*scale, v[2]*scale) for v in vertices]

            # Create carbon atoms at each vertex
            for i, v in enumerate(verts):
                bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12, segments=10, ring_count=8, location=v)
                atom = bpy.context.active_object
                atom.name = f"C_{i}"
                if SHADING_SMOOTH:
                    bpy.ops.object.shade_smooth()
                add_material(atom, f"C_Mat_{i}", (0.2, 0.2, 0.2), roughness=0.4)

            # Create bonds between nearby vertices
            bond_threshold = 1.15
            for i in range(len(verts)):
                for j in range(i+1, len(verts)):
                    v1, v2 = verts[i], verts[j]
                    dist = math.sqrt(sum((a-b)**2 for a, b in zip(v1, v2)))
                    if dist < bond_threshold:
                        mid = ((v1[0]+v2[0])/2, (v1[1]+v2[1])/2, (v1[2]+v2[2])/2)
                        bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=dist*0.9, vertices=6, location=mid)
                        bond = bpy.context.active_object
                        bond.name = f"Bond_{i}_{j}"
                        dx, dy, dz = v2[0]-v1[0], v2[1]-v1[1], v2[2]-v1[2]
                        bond.rotation_euler = (0, math.atan2(math.sqrt(dx**2+dy**2), dz), math.atan2(dy, dx))
                        if SHADING_SMOOTH:
                            bpy.ops.object.shade_smooth()
                        add_material(bond, f"Bond_Mat_{i}_{j}", (0.3, 0.3, 0.3), roughness=0.5)
        """) + self._footer()

    def _water_script(self) -> str:
        return self._header() + textwrap.dedent("""\
            # --- WATER MOLECULE (H2O) ---
            # Oxygen
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.5, segments=20, ring_count=16, location=(0, 0, 0))
            o = bpy.context.active_object
            o.name = "Oxygen"
            if SHADING_SMOOTH:
                bpy.ops.object.shade_smooth()
            add_material(o, "O_Mat", (1.0, 0.0, 0.0), roughness=0.3)

            # Hydrogen atoms at ~104.5 degree bond angle
            angle = math.radians(52.25)
            bond_len = 0.8
            for i, sign in enumerate([1, -1]):
                x = bond_len * math.sin(angle) * sign
                z = bond_len * math.cos(angle)
                bpy.ops.mesh.primitive_uv_sphere_add(radius=0.3, segments=16, ring_count=12, location=(x, 0, z))
                h = bpy.context.active_object
                h.name = f"Hydrogen_{i}"
                if SHADING_SMOOTH:
                    bpy.ops.object.shade_smooth()
                add_material(h, f"H_Mat_{i}", (1.0, 1.0, 1.0), roughness=0.3)

                # Bond
                bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=bond_len*0.85, vertices=8,
                    location=(x/2, 0, z/2))
                bond = bpy.context.active_object
                bond.name = f"Bond_O_H_{i}"
                bond.rotation_euler = (0, math.radians(-sign*52.25 + 90), 0)
                if SHADING_SMOOTH:
                    bpy.ops.object.shade_smooth()
                add_material(bond, f"Bond_Mat_{i}", (0.6, 0.6, 0.6), roughness=0.5)
        """) + self._footer()

    def _methane_script(self) -> str:
        return self._header() + textwrap.dedent("""\
            # --- METHANE MOLECULE (CH4) ---
            # Carbon at center
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.4, segments=20, ring_count=16, location=(0, 0, 0))
            c = bpy.context.active_object
            c.name = "Carbon"
            if SHADING_SMOOTH:
                bpy.ops.object.shade_smooth()
            add_material(c, "C_Mat", (0.2, 0.2, 0.2), roughness=0.3)

            # Tetrahedral hydrogen positions
            bond_len = 0.9
            import math
            tet_angle = math.radians(109.47)
            h_positions = [
                (bond_len, bond_len, bond_len),
                (-bond_len, -bond_len, bond_len),
                (-bond_len, bond_len, -bond_len),
                (bond_len, -bond_len, -bond_len),
            ]
            # Normalize
            h_positions = [(x*0.5773, y*0.5773, z*0.5773) for x, y, z in h_positions]

            for i, pos in enumerate(h_positions):
                bpy.ops.mesh.primitive_uv_sphere_add(radius=0.25, segments=16, ring_count=12, location=pos)
                h = bpy.context.active_object
                h.name = f"Hydrogen_{i}"
                if SHADING_SMOOTH:
                    bpy.ops.object.shade_smooth()
                add_material(h, f"H_Mat_{i}", (1.0, 1.0, 1.0), roughness=0.3)

                bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=bond_len*0.85, vertices=8,
                    location=(pos[0]/2, pos[1]/2, pos[2]/2))
                bond = bpy.context.active_object
                bond.name = f"Bond_C_H_{i}"
                dx, dy, dz = pos
                bond.rotation_euler = (0, math.atan2(math.sqrt(dx**2+dy**2), dz), math.atan2(dy, dx))
                if SHADING_SMOOTH:
                    bpy.ops.object.shade_smooth()
                add_material(bond, f"Bond_Mat_{i}", (0.5, 0.5, 0.5), roughness=0.5)
        """) + self._footer()

    def _benzene_script(self) -> str:
        return self._header() + textwrap.dedent("""\
            # --- BENZENE MOLECULE (C6H6) ---
            ring_radius = 1.0
            for i in range(6):
                angle = i * math.pi / 3
                x = ring_radius * math.cos(angle)
                y = ring_radius * math.sin(angle)
                # Carbon
                bpy.ops.mesh.primitive_uv_sphere_add(radius=0.3, segments=16, ring_count=12, location=(x, y, 0))
                c = bpy.context.active_object
                c.name = f"Carbon_{i}"
                if SHADING_SMOOTH:
                    bpy.ops.object.shade_smooth()
                add_material(c, f"C_Mat_{i}", (0.2, 0.2, 0.2), roughness=0.3)

                # Hydrogen
                hx = (ring_radius + 0.6) * math.cos(angle)
                hy = (ring_radius + 0.6) * math.sin(angle)
                bpy.ops.mesh.primitive_uv_sphere_add(radius=0.2, segments=12, ring_count=8, location=(hx, hy, 0))
                h = bpy.context.active_object
                h.name = f"Hydrogen_{i}"
                if SHADING_SMOOTH:
                    bpy.ops.object.shade_smooth()
                add_material(h, f"H_Mat_{i}", (1.0, 1.0, 1.0), roughness=0.3)

                # C-H bond
                mx, my = (x + hx) / 2, (y + hy) / 2
                bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=0.5, vertices=6, location=(mx, my, 0))
                ch_bond = bpy.context.active_object
                ch_bond.name = f"Bond_CH_{i}"
                ch_bond.rotation_euler = (math.pi/2, 0, angle)
                if SHADING_SMOOTH:
                    bpy.ops.object.shade_smooth()
                add_material(ch_bond, f"CH_Bond_Mat_{i}", (0.5, 0.5, 0.5), roughness=0.5)

                # C-C bond (to next carbon)
                next_angle = (i + 1) * math.pi / 3
                nx = ring_radius * math.cos(next_angle)
                ny = ring_radius * math.sin(next_angle)
                bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=ring_radius, vertices=6,
                    location=((x+nx)/2, (y+ny)/2, 0))
                cc_bond = bpy.context.active_object
                cc_bond.name = f"Bond_CC_{i}"
                cc_bond.rotation_euler = (math.pi/2, 0, (angle + next_angle) / 2)
                if SHADING_SMOOTH:
                    bpy.ops.object.shade_smooth()
                add_material(cc_bond, f"CC_Bond_Mat_{i}", (0.4, 0.4, 0.4), roughness=0.5)
        """) + self._footer()

    def _caffeine_script(self) -> str:
        return self._header() + textwrap.dedent("""\
            # --- CAFFEINE MOLECULE APPROXIMATION (C8H10N4O2) ---
            # Simplified fused ring system
            import math

            # Ring 1 (6-membered) and Ring 2 (5-membered) fused
            ring1_radius = 0.8
            ring1_center = (0, 0, 0)
            ring2_center = (ring1_radius * 1.5, 0, 0)

            atoms = []
            # Ring 1 carbons/nitrogens
            for i in range(6):
                angle = i * math.pi / 3
                x = ring1_center[0] + ring1_radius * math.cos(angle)
                y = ring1_center[1] + ring1_radius * math.sin(angle)
                is_n = i in [0, 3]
                atoms.append((x, y, 0, "N" if is_n else "C"))

            # Ring 2 (5-membered, fused with ring 1)
            for i in range(5):
                angle = i * 2 * math.pi / 5 + math.pi
                x = ring2_center[0] + 0.6 * math.cos(angle)
                y = ring2_center[1] + 0.6 * math.sin(angle)
                is_n = i in [1, 3]
                atoms.append((x, y, 0, "N" if is_n else "C"))

            # Oxygen atoms (carbonyl groups)
            atoms.append((ring1_center[0], ring1_radius + 0.4, 0, "O"))
            atoms.append((ring1_center[0] + ring1_radius * 0.5, -ring1_radius - 0.4, 0, "O"))

            # Methyl groups (simplified as H)
            for mx_off in [0.4, -0.4, 1.2]:
                atoms.append((ring2_center[0] + mx_off, 0.8, 0, "H"))

            colors = {"C": (0.2, 0.2, 0.2), "N": (0.0, 0.0, 0.8), "O": (1.0, 0.0, 0.0), "H": (1.0, 1.0, 1.0)}
            radii = {"C": 0.25, "N": 0.25, "O": 0.3, "H": 0.18}

            for i, (x, y, z, elem) in enumerate(atoms):
                bpy.ops.mesh.primitive_uv_sphere_add(radius=radii[elem], segments=12, ring_count=8, location=(x, y, z))
                atom = bpy.context.active_object
                atom.name = f"{elem}_{i}"
                if SHADING_SMOOTH:
                    bpy.ops.object.shade_smooth()
                add_material(atom, f"{elem}_Mat_{i}", colors[elem], roughness=0.3)

            # Simple bonds between nearby atoms
            for i in range(len(atoms)):
                for j in range(i+1, len(atoms)):
                    p1, p2 = atoms[i][:3], atoms[j][:3]
                    dist = math.sqrt(sum((a-b)**2 for a, b in zip(p1, p2)))
                    if dist < 1.0:
                        mid = ((p1[0]+p2[0])/2, (p1[1]+p2[1])/2, (p1[2]+p2[2])/2)
                        bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=dist*0.8, vertices=6, location=mid)
                        bond = bpy.context.active_object
                        bond.name = f"Bond_{i}_{j}"
                        dx, dy, dz = p2[0]-p1[0], p2[1]-p1[1], p2[2]-p1[2]
                        bond.rotation_euler = (0, math.atan2(math.sqrt(dx**2+dy**2), dz), math.atan2(dy, dx))
                        if SHADING_SMOOTH:
                            bpy.ops.object.shade_smooth()
                        add_material(bond, f"Bond_Mat_{i}_{j}", (0.4, 0.4, 0.4), roughness=0.5)
        """) + self._footer()

    def _generic_molecule_script(self, entity: str) -> str:
        safe_entity = entity.replace("'", "").replace('"', "")[:80]
        return self._header() + textwrap.dedent(f"""\
            # --- GENERIC MOLECULE: {safe_entity} ---
            import math
            import random
            random.seed(hash("{safe_entity}") & 0xFFFFFFFF)

            num_atoms = 12
            center_radius = 1.2
            atoms = []
            for i in range(num_atoms):
                theta = random.uniform(0, 2 * math.pi)
                phi = random.uniform(0, math.pi)
                r = random.uniform(0.5, center_radius)
                x = r * math.sin(phi) * math.cos(theta)
                y = r * math.sin(phi) * math.sin(theta)
                z = r * math.cos(phi)
                elements = ["C", "H", "O", "N"]
                elem = random.choice(elements)
                atoms.append((x, y, z, elem))

            colors = {{"C": (0.2, 0.2, 0.2), "H": (1.0, 1.0, 1.0), "O": (1.0, 0.0, 0.0), "N": (0.0, 0.0, 0.8)}}
            radii = {{"C": 0.25, "H": 0.18, "O": 0.28, "N": 0.25}}

            for i, (x, y, z, elem) in enumerate(atoms):
                bpy.ops.mesh.primitive_uv_sphere_add(radius=radii[elem], segments=12, ring_count=8, location=(x, y, z))
                atom = bpy.context.active_object
                atom.name = f"{{elem}}_{{i}}"
                if SHADING_SMOOTH:
                    bpy.ops.object.shade_smooth()
                add_material(atom, f"{{elem}}_Mat_{{i}}", colors[elem], roughness=0.3)

            # Bonds between nearby atoms
            for i in range(len(atoms)):
                for j in range(i+1, len(atoms)):
                    p1, p2 = atoms[i][:3], atoms[j][:3]
                    dist = math.sqrt(sum((a-b)**2 for a, b in zip(p1, p2)))
                    if dist < 1.3:
                        mid = ((p1[0]+p2[0])/2, (p1[1]+p2[1])/2, (p1[2]+p2[2])/2)
                        bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=dist*0.8, vertices=6, location=mid)
                        bond = bpy.context.active_object
                        bond.name = f"Bond_{{i}}_{{j}}"
                        dx, dy, dz = p2[0]-p1[0], p2[1]-p1[1], p2[2]-p1[2]
                        bond.rotation_euler = (0, math.atan2(math.sqrt(dx**2+dy**2), dz), math.atan2(dy, dx))
                        if SHADING_SMOOTH:
                            bpy.ops.object.shade_smooth()
                        add_material(bond, f"Bond_Mat_{{i}}_{{j}}", (0.4, 0.4, 0.4), roughness=0.5)
        """) + self._footer()
