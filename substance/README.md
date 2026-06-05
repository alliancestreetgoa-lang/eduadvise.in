# Substance 3D Painter → EduAdvise globe pipeline

The landing page's 3D globe (`globe.js`) renders with a Three.js
`MeshStandardMaterial` (metallic/roughness PBR). Right now it uses a CDN earth
texture tinted brand-purple. The moment Substance-exported maps exist in
`../textures/`, the globe **automatically upgrades** to them — no code changes.

## Expected files (in `eduadvise-landing/textures/`)

| File | Content | Color space |
|---|---|---|
| `globe_baseColor.png` | Albedo (continents in brand purple `#660066` on paper `#F7F2EE`?) | sRGB |
| `globe_normal.png` | Tangent-space normal, **OpenGL (Y+)** — glTF/Three.js standard | Linear |
| `globe_ORM.png` | Packed: **R**=ambient occlusion, **G**=roughness, **B**=metallic | Linear |

## Workflow

1. Install Adobe Substance 3D Painter (Creative Cloud / free trial).
2. Get a UV-unwrapped sphere: in Blender, add a UV Sphere (it comes with
   equirectangular UVs), export as `globe.fbx`.
3. New Painter project → select `globe.fbx`, template *PBR Metallic Roughness*,
   document resolution 1024.
4. **Name the texture set `globe`** (rename in the Texture Set list) — the
   export filenames derive from it.
5. Texture it. Brand direction: matte paper ocean (roughness ~0.85), purple
   landmasses with a subtle height/normal relief, maybe gold metallic flecks
   on the destination cities (metallic 1.0, roughness 0.3).
6. Export: open **Python > Console** and run `batch_export_web.py`
   (or `exec(open('<path>/batch_export_web.py').read())`).
7. Reload the landing page — the globe now wears your textures.

## Why these settings

- **1024×1024 PNG-8** — the web sweet spot: ~4 MB for all three maps.
- **Padding "infinite"** — prevents seam lines at UV borders.
- **Packed ORM** — one texture serves `aoMap` + `roughnessMap` + `metalnessMap`
  in Three.js (they share a sampler), saving two HTTP requests and GPU memory.
- **OpenGL normals** — Three.js/glTF expect Y+; DirectX (Y−) normals would
  show inverted lighting.

## Tuning in globe.js

When the ORM map loads, `globe.js` sets `roughness`/`metalness` to `1.0` so the
texture has full authority. Adjust the maps in Painter rather than the code.
