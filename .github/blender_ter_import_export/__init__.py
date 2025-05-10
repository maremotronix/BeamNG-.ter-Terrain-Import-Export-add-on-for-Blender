bl_info = {
    "name": "BeamNG Terrain Importer & Exporter",
    "author": "MaremoTronix",
    "version": (1, 0, 0),
    "blender": (3, 0, 0),
    "location": "File > Import/Export",
    "description": "Import and export BeamNG terrain (.ter) files.",
    "category": "Import-Export"
}

import bpy
from . import import_ter, export_ter

def menu_func_import(self, context):
    self.layout.operator(import_ter.BeamNGTerrainImporter.bl_idname, text="BeamNG Terrain (.ter)")

def menu_func_export(self, context):
    self.layout.operator(export_ter.BeamNGTerrainExporter.bl_idname, text="BeamNG Terrain (.ter)")

def register():
    import_ter.register()
    export_ter.register()
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)

def unregister():
    import_ter.unregister()
    export_ter.unregister()
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)

if __name__ == "__main__":
    register()
