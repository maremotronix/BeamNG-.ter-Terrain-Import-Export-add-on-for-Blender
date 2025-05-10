import bpy
import struct
from bpy_extras.io_utils import ExportHelper

class BeamNGTerrainExporter(bpy.types.Operator, ExportHelper):
    """Export selected Blender Mesh objects to BeamNG Terrain (.ter)"""
    bl_idname = "export_scene.beamng_terrain_export"
    bl_label = "Export BeamNG Terrain (.ter)"
    filename_ext = ".ter"

    filter_glob: bpy.props.StringProperty(default="*.ter", options={'HIDDEN'})

    def execute(self, context):
        selected_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']
        if not selected_objects:
            self.report({'ERROR'}, "No valid mesh objects selected for export!")
            return {'CANCELLED'}

        for obj in selected_objects:
            terrain_data = self.prepare_terrain_data(obj)
            if not terrain_data:
                self.report({'ERROR'}, f"Terrain data preparation failed for {obj.name}!")
                continue

            filename = f"{self.filepath.rstrip('.ter')}_{obj.name}.ter"
            self.write_ter(filename, terrain_data)

        return {'FINISHED'}

    @staticmethod
    def prepare_terrain_data(obj):
        """Extracts terrain data from Blender mesh for .ter export"""
        verts = obj.data.vertices
        size = int(len(verts) ** 0.5)  # Ensure square terrain dimensions

        if size * size != len(verts):
            print(f"Error: Terrain mesh '{obj.name}' must be square (power-of-two dimensions).")
            return None

        # Heightmap extraction with correct scaling
        heightmap = [max(0, min(65535, int(v.co.z * 1000))) for v in sorted(verts, key=lambda v: (v.co.y, v.co.x))]

        # Layer Map extraction with material indexing
        layer_map = [0] * (size * size)
        for poly in obj.data.polygons:
            for idx in poly.vertices:
                layer_map[idx] = poly.material_index

        # Material name collection
        materials = [mat.name for mat in obj.data.materials]

        return {
            "version": 9,
            "terrain_size": size,
            "heightmap": heightmap,
            "layer_map": layer_map,
            "materials": materials,
        }

    @staticmethod
    def write_ter(filename, terrain_data):
        """Writes terrain data to .ter file"""
        try:
            with open(filename, "wb") as f:
                f.write(struct.pack("<B", terrain_data["version"]))  # Version
                f.write(struct.pack("<I", terrain_data["terrain_size"]))  # Terrain Size

                # Write heightmap data (little-endian 16-bit integers)
                f.write(struct.pack(f"<{terrain_data['terrain_size'] ** 2}H", *terrain_data["heightmap"]))

                # Write layer map (unsigned bytes)
                f.write(struct.pack(f"<{terrain_data['terrain_size'] ** 2}B", *terrain_data["layer_map"]))

                # Write material names correctly formatted
                f.write(struct.pack("<I", len(terrain_data["materials"])))  # Material count
                for name in terrain_data["materials"]:
                    f.write(struct.pack("B", len(name)))  # Name length prefix
                    f.write(name.encode("ascii"))  # Name string

            print(f"Exported terrain '{filename}' successfully!")
        except Exception as e:
            print(f"Error writing .ter file for '{filename}': {e}")

def register():
    bpy.utils.register_class(BeamNGTerrainExporter)

def unregister():
    bpy.utils.unregister_class(BeamNGTerrainExporter)
