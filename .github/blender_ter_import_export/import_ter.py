import bpy
import struct
from bpy_extras.io_utils import ImportHelper

class BeamNGTerrainImporter(bpy.types.Operator, ImportHelper):
    """Import BeamNG Terrain (.ter)"""
    bl_idname = "import_scene.beamng_ter"
    bl_label = "Import BeamNG Terrain (.ter)"
    filename_ext = ".ter"

    filter_glob: bpy.props.StringProperty(default="*.ter", options={'HIDDEN'})

    def execute(self, context):
        terrain_data = self.read_ter(self.filepath)
        if terrain_data:
            self.create_mesh(context, terrain_data)
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "Failed to import .ter file")
            return {'CANCELLED'}

    @staticmethod
    def read_ter(filename):
        """Reads .ter file & extracts terrain data (without materials)"""
        try:
            with open(filename, "rb") as f:
                version = struct.unpack("B", f.read(1))[0]
                terrain_size = struct.unpack("<I", f.read(4))[0]

                # Read heightmap safely
                heightmap_size = terrain_size * terrain_size * 2
                heightmap_bytes = f.read(heightmap_size)
                if len(heightmap_bytes) != heightmap_size:
                    print(f"Error: Expected {heightmap_size} bytes for heightmap, got {len(heightmap_bytes)}")
                    return None
                heightmap = list(struct.unpack(f"<{terrain_size * terrain_size}H", heightmap_bytes))

                # Read layer map (material indices, but NOT applied)
                layer_map_size = terrain_size * terrain_size
                layer_map_bytes = f.read(layer_map_size)
                if len(layer_map_bytes) != layer_map_size:
                    print(f"Error: Expected {layer_map_size} bytes for layer map, got {len(layer_map_bytes)}")
                    return None
                layer_map = list(struct.unpack(f"<{terrain_size * terrain_size}B", layer_map_bytes))

            return {
                "version": version,
                "terrain_size": terrain_size,
                "heightmap": heightmap,
                "layer_map": layer_map,
            }
        except Exception as e:
            print(f"Error reading .ter file: {e}")
            return None

    def create_mesh(self, context, terrain_data):
        """Creates a Blender terrain mesh from .ter heightmap (without materials)"""
        try:
            size = terrain_data["terrain_size"]
            verts = [(x, y, terrain_data["heightmap"][y * size + x] / 1000.0) for y in range(size) for x in range(size)]
            faces = [(y * size + x, y * size + x + 1, (y + 1) * size + x + 1, (y + 1) * size + x) for y in range(size - 1) for x in range(size - 1)]

            mesh = bpy.data.meshes.new(name="BeamNG_Terrain")
            mesh.from_pydata(verts, [], faces)
            obj = bpy.data.objects.new("BeamNG_Terrain", mesh)
            context.scene.collection.objects.link(obj)
        except Exception as e:
            print(f"Error during mesh creation: {e}")

def register():
    bpy.utils.register_class(BeamNGTerrainImporter)

def unregister():
    bpy.utils.unregister_class(BeamNGTerrainImporter)
