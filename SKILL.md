---
name: blender
description: Drive Blender through three control channels — (1) the blender-mcp addon via socket TCP on port 9876 for real-time commands on an open scene, (2) Blender headless (`--background --python`) for batch jobs and configuration, (3) bridges to sibling services (ComfyUI REST, DAZ Studio script runner, etc.) via installed add-ons. Discovers any installed add-on at runtime, reads its operators and preferences (via name match plus source-scan for opaque plugins), and routes the user's intent to the right plugin. Categorizes plugins under capability headings — geometry generation, AI texturing, export pipeline, creative effects, rigging & animation, environment assets, harness — so "texturize this mesh", "make it rain", "rig this character", "export to X" each end up calling the right operator. Use whenever the user wants something done in Blender.
---

# Blender Agent Skill

A framework-neutral guide for an agent driving Blender through [ahujasid/blender-mcp](https://github.com/ahujasid/blender-mcp). Keeps plugin usage **discovery-based** — every new add-on is introspected and slotted into a capability catalog, so the agent does not need hard-coded support for each new plugin.

## Control channels

### 1. MCP socket (real-time, Blender GUI running)

The blender-mcp addon listens on `localhost:9876`. Send JSON commands:

```bash
python3 scripts/mcp_client.py execute_code '{"code":"import bpy; print(len(bpy.data.objects))"}'
python3 scripts/mcp_client.py get_scene_info
python3 scripts/mcp_client.py get_viewport_screenshot
```

If the MCP harness layer reports the server as "Failed to connect":
- The Blender GUI is not running, or
- The user has not clicked **Connect to Claude** / equivalent in the MCP side panel, or
- The server-side Python dependency resolver used the wrong interpreter (on systems where `uvx` defaults to Python 3.14, pin `--python 3.12` when launching the client side).

Reload cycle for the addon after editing its source:

```python
# Via execute_code
import bpy, importlib, sys
bpy.ops.blendermcp.stop_server()
bpy.ops.preferences.addon_disable(module="blender_mcp")
importlib.reload(sys.modules["blender_mcp"])
bpy.ops.preferences.addon_enable(module="blender_mcp")
bpy.ops.blendermcp.start_server()
```

### 2. Headless batch (`--background --python`)

For reproducible batch jobs (bulk import/export, setting preferences, baking, rendering) and anything the user does not need to watch happen live:

```bash
blender --background --python <script>.py -- [script args]
```

- On Windows-from-WSL, pass **Windows-style paths** (`C:\...`). Blender is a native binary and parses its arguments as Windows.
- Use this channel to pre-configure add-on preferences before launching a GUI session.
- Great for CI or scheduled jobs.

### 3. Bridges through installed add-ons

Some add-ons talk to external services: ComfyUI (for AI texture and mesh generation), DAZ Studio (for character pipeline), asset libraries (for HDRIs, materials). Treat them as sub-skills — the MCP layer calls their operators, the add-on does the network work internally.

## Universal handlers (from `patches/blender_mcp_enhanced.py`)

Once the enhancement patch is applied, the server exposes these endpoints in addition to the upstream set. They are the core of the discovery workflow.

| Command | Params | What it does |
|---|---|---|
| `list_addons` | — | Every enabled addon key, full path (e.g. `bl_ext.user_default.stablegen`) |
| `inspect_addon` | `{"name":"<addon>"}` | Preferences + namespaces owned by the addon (name match + source scan for cryptic plugins) + file-discovered operators |
| `list_operator_namespaces` | — | All `bpy.ops.*` namespaces |
| `inspect_ops_namespace` | `{"namespace":"<ns>"}` | Every operator in that namespace with description and parameter schema |
| `call_operator` | `{"operator":"ns.name", "params":{…}}` | Invokes any operator, returns Blender's result enum |
| `get_addon_prefs` / `set_addon_prefs` | `{"name":"<addon>", …}` | Read/write addon preferences; writes call `save_userpref` |
| `get_scene_prop` / `set_scene_prop` | `{"name":"<path>", "value":…}` | Scene-level properties with dotted paths (`stablegen_props.prompt`) |
| `find_scene_props` | `{"pattern":"<substr>"}` | Filter scene props by case-insensitive substring |
| `get_viewport_screenshot` | — | PNG viewport capture — use for visual feedback/aesthetic judgment |

## Plugin catalog pattern

The agent maintains a **catalog** that maps capabilities → plugins → operators. Starter layout in `examples/CATALOG.md`. Recommended categories:

- **Geometry generation** (image→mesh, procedural, parametric)
- **AI texturing** (diffusion-driven UV painting, multi-view projection)
- **Export pipelines** (FBX/GLB/USD bridges to DAZ, Unity, Unreal, Marmoset, web)
- **Creative effects** (simulation, stylization, post-process on mesh)
- **Rigging & animation** (auto-rig, IK/FK, pose library, mocap retarget)
- **Environment assets** (HDRI, sky, vegetation, scatter)
- **Harness** (the MCP itself, asset browsers, viewport helpers)

When a new plugin is installed:

```bash
python3 scripts/mcp_client.py list_addons
python3 scripts/mcp_client.py inspect_addon '{"name":"<new-addon>"}'
# For cryptic namespaces:
python3 scripts/mcp_client.py inspect_ops_namespace '{"namespace":"<ns>"}'
```

Then add a row to the catalog under the matching category with:
- Plugin name / description
- User-intent triggers ("when user says X")
- Key operator ids
- Preferences or scene props that matter

## Aesthetic judgment loop

When generating or transforming visuals, close the loop with `get_viewport_screenshot`:

1. Apply an operator (e.g. `call_operator stablegen.queue_process`).
2. Take a screenshot.
3. Evaluate against the user's intent (composition, color, style, coverage).
4. Adjust scene props or addon preferences (`set_scene_prop`, `set_addon_prefs`).
5. Re-run, re-screenshot, compare.

Same flow for render previews via `bpy.ops.render.render` then reading the output image path.

## Troubleshooting

**Socket refuses connections** — the server was shut down by a hot-reload. Re-run the reload script block above (stop_server → addon disable → module reload → addon enable → start_server), or ask the user to click **Connect to Claude** again in the side panel.

**Cryptic operator names (e.g. `sna.xxx_yyyy_5e99e`)** — addons generated by tools like Serpens use GUID suffixes. The source-scan inspector handles this; if your inspector skipped them, verify the addon's source folder exists at one of the standard Blender extension/addon paths.

**`bpy.ops.<plugin>` missing after enabling** — some add-ons register classes only on first panel draw. Call the operator at least once via `execute_code` or open the panel in the UI before introspecting; or reload the addon.

**Operator returns `{'CANCELLED'}`** — check the poll method by inspecting the operator's RNA `poll_message`; most commonly an object of the wrong type is selected or the user is in the wrong mode (edit/object).

**Scene prop path missing** — properties defined by add-ons live under auto-generated names. Use `find_scene_props` with a substring hint from the addon's UI labels; props are usually attached to `bpy.context.scene` directly for Serpens-style plugins, or under a PropertyGroup named after the addon for conventional ones.

## Minimal workflow example

```bash
# Discover what is installed
python3 scripts/mcp_client.py list_addons

# Explore a specific addon (prefs + operators)
python3 scripts/mcp_client.py inspect_addon '{"name":"<short-name>"}'

# Configure it
python3 scripts/mcp_client.py set_addon_prefs '{"name":"<short-name>", "server_address":"127.0.0.1:8188"}'

# Run one of its operators
python3 scripts/mcp_client.py call_operator '{"operator":"<ns>.<op>","params":{}}'

# Inspect the result visually
python3 scripts/mcp_client.py get_viewport_screenshot
```
