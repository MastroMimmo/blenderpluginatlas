# Plugin Catalog — template

Fill in one row per installed add-on under the matching category. Keep the "When user says" column focused on intent triggers, not tool names — the agent will match user requests against these strings.

> Run `python3 scripts/mcp_client.py inspect_addon '{"name":"<short-name>"}'` after installing a plugin to auto-discover its operators and prefs. Then slot the findings here.

---

## 🧱 Geometry generation

| Plugin | Scope | When user says |
|---|---|---|
| *(example)* ComfyUI-Trellis2 (ComfyUI node, external) | Image → high-res mesh with multi-view texturing | "generate 3D from photo", "image to mesh" |
| *(example)* ComfyUI-Hunyuan3DWrapper (ComfyUI node) | Fast image → mesh, no gated dependency | "quick 3D gen", "fallback mesh" |

## 🎨 AI texturing

| Plugin | Scope | When user says |
|---|---|---|
| *(example)* StableGen (Blender extension) | Multi-view SDXL/FLUX projection + bake on existing mesh | "texturize this", "restyle the material" |

## 🚚 Export pipeline

| Plugin | Scope | When user says |
|---|---|---|
| *(example)* Your DAZ bridge (addon + native plugin) | Bake PBR → flat + hand off to DAZ Studio | "port to DAZ", "save as .duf" |

## 🌀 Creative effects

| Plugin | Scope | When user says |
|---|---|---|
| *(example)* A CGMatter/Serpens pack under `sna.*` | Procedural effects (rain, melt, cloud, pixel-sort…) | "make it rain", "melt this" |

## 🦴 Rigging & animation

| Plugin | Scope | When user says |
|---|---|---|
| *(example)* A DAZ importer with auto-Rigify conversion | `.duf` → Blender + Rigify/MHX + IK/FK + pose library | "rig this character", "IK/FK switch" |

## 🌿 Environment assets

| Plugin | Scope | When user says |
|---|---|---|
| *(example)* Poly Haven addon | HDRIs, textures, models via API | "add an HDRI", "load a sky" |

## 🧭 Harness (meta)

| Plugin | Scope |
|---|---|
| blender-mcp + this repo's enhancement patch | Socket control, universal introspection, screenshot feedback |

---

## Key operators quick-reference

For each plugin row above, keep a short list of the operators the agent will actually call:

```
<plugin-name>:
  <ns>.<op_name>          # description / what it does
  <ns>.<op_name>          # ...
```

Store scene props that matter:

```
<plugin-name> scene props:
  bpy.context.scene.<prop_name>    # controls X
  bpy.context.scene.<group>.<prop> # controls Y
```

The agent uses `find_scene_props` + `set_scene_prop` against these paths.
