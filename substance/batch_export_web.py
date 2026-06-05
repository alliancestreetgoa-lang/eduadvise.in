# EduAdvise landing — Substance 3D Painter batch export for the Three.js globe
#
# Run inside Substance Painter:  Python > Console (or save to the plugins folder)
# Exports every texture set as web-optimized PBR maps into ../textures/ with the
# exact filenames globe.js looks for:
#   <set>_baseColor.png   - sRGB albedo
#   <set>_normal.png      - OpenGL tangent-space normal (glTF / Three.js standard)
#   <set>_ORM.png         - packed R=ambientOcclusion G=roughness B=metallic
#
# Name your globe texture set "globe" in Painter and the website picks the maps
# up automatically on next reload (no code change needed).

import os

import substance_painter.export
import substance_painter.project
import substance_painter.textureset

# Output: <this repo>/textures
EXPORT_PATH = os.path.normpath(
    os.path.join(os.path.dirname(substance_painter.project.file_path()), "..", "textures")
)

WEB_PRESET = {
    "exportPresets": [{
        "name": "EduAdvise_Web_PBR",
        "maps": [
            {
                "fileName": "$textureSet_baseColor",
                "channels": [
                    {"destChannel": c, "srcChannel": c,
                     "srcMapType": "documentMap", "srcMapName": "baseColor"}
                    for c in ("R", "G", "B")
                ],
                "parameters": {"fileFormat": "png", "bitDepth": "8", "dithering": True},
            },
            {
                "fileName": "$textureSet_normal",
                "channels": [
                    {"destChannel": c, "srcChannel": c,
                     "srcMapType": "virtualMap", "srcMapName": "Normal_OpenGL"}
                    for c in ("R", "G", "B")
                ],
                "parameters": {"fileFormat": "png", "bitDepth": "8", "dithering": False},
            },
            {
                # Packed ORM — one texture instead of three (Three.js shares it
                # across aoMap / roughnessMap / metalnessMap)
                "fileName": "$textureSet_ORM",
                "channels": [
                    {"destChannel": "R", "srcChannel": "R",
                     "srcMapType": "documentMap", "srcMapName": "ambientOcclusion"},
                    {"destChannel": "G", "srcChannel": "R",
                     "srcMapType": "documentMap", "srcMapName": "roughness"},
                    {"destChannel": "B", "srcChannel": "R",
                     "srcMapType": "documentMap", "srcMapName": "metallic"},
                ],
                "parameters": {"fileFormat": "png", "bitDepth": "8", "dithering": False},
            },
        ],
    }]
}

config = {
    "exportShaderParams": False,
    "exportPath": EXPORT_PATH,
    "exportPresets": WEB_PRESET["exportPresets"],
    "defaultExportPreset": "EduAdvise_Web_PBR",
    "exportList": [
        {"rootPath": ts.name(), "exportPreset": "EduAdvise_Web_PBR"}
        for ts in substance_painter.textureset.all_texture_sets()
    ],
    "exportParameters": [{
        "parameters": {
            "fileFormat": "png",
            "bitDepth": "8",
            "paddingAlgorithm": "infinite",  # no seams at UV borders
            "sizeLog2": 10,                  # 1024x1024 — web sweet spot
        }
    }],
}

result = substance_painter.export.export_project_textures(config)

if result.status == substance_painter.export.ExportStatus.Success:
    for stack, files in result.textures.items():
        print(f"[EduAdvise] exported {stack}:")
        for f in files:
            print(f"  {f}")
    print(f"[EduAdvise] done -> {EXPORT_PATH}")
else:
    print(f"[EduAdvise] export FAILED: {result.message}")
