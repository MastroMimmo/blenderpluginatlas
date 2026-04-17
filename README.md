<div align="center">

# 🧩 Blender Plugin Atlas

### *A universal plugin-discovery framework for AI agents driving Blender*

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](LICENSE)
[![Blender 4.2+](https://img.shields.io/badge/Blender-4.2+-F5792A?style=for-the-badge&logo=blender&logoColor=white)](https://www.blender.org/)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![MCP](https://img.shields.io/badge/MCP-compatible-7B2CBF?style=for-the-badge)](https://github.com/ahujasid/blender-mcp)

<br/>

**Tell your agent *"texturize this mesh"*, *"make it rain"*, *"rig this character"*, *"export to DAZ"* —  
and it picks the right Blender plugin automatically.**

<br/>

[Features](#-features) · [Install](#-install) · [Universal handlers](#-universal-handlers) · [Catalog pattern](#-catalog-pattern) · [Examples](examples/)

</div>

---

## ✨ Features

<table>
<tr>
<td width="33%" valign="top">

### 🔍 Runtime discovery
No hard-coded plugin lists. The agent `inspect_addon` at runtime, reads operators, prefs, scene props.

</td>
<td width="33%" valign="top">

### 🧬 Source-scan inspector
Handles opaque plugins (Serpens/SNA) by grepping `bl_idname` from source files. Finds every operator even when naming is cryptic.

</td>
<td width="33%" valign="top">

### 🎨 Aesthetic feedback loop
Viewport screenshot after each action → agent sees the result → adjusts parameters → iterates.

</td>
</tr>
<tr>
<td valign="top">

### 🔌 Three control channels
Real-time MCP socket · headless `--background` · bridges to ComfyUI / DAZ / asset libraries.

</td>
<td valign="top">

### 🗂️ Capability catalog
Maps user intent → category → plugin → operator. Growable, framework-neutral, plain markdown.

</td>
<td valign="top">

### 🧠 Drop-in for any agent
Works with any LLM agent that can send JSON over TCP. Skill file compatible with Claude Code, bring-your-own agent, or plain scripts.

</td>
</tr>
</table>

---

## 🎯 The problem this solves

> *Every Blender plugin invents its own operator namespace, its own preference schema, its own UI.  
> An agent that wants to orchestrate them all either (a) hard-codes support for each, or (b) hands raw Python to the user.*

**This framework picks a third path**: an introspection layer that any agent queries at runtime. Install a new add-on → agent discovers it → agent knows how to call it. No fork, no rebuild, no human middleman.

<br/>

<div align="center">

```
┌─────────────┐     socket      ┌──────────────────┐
│    Agent    │ ◄─────────────► │  blender-mcp     │
│ (any LLM)   │   TCP 9876      │  (this patch)    │
└─────────────┘                 └────────┬─────────┘
                                         │
                 ┌───────────────────────┼───────────────────────┐
                 ▼                       ▼                       ▼
         ┌───────────────┐       ┌───────────────┐       ┌───────────────┐
         │  inspect_     │       │  call_        │       │  get/set_     │
         │  addon        │       │  operator     │       │  scene_prop   │
         └───────────────┘       └───────────────┘       └───────────────┘
                 │                       │                       │
                 ▼                       ▼                       ▼
         ┌───────────────────────────────────────────────────────────────┐
         │      🧩 ANY installed Blender add-on or extension             │
         │   geometry · texturing · rigging · effects · export · …       │
         └───────────────────────────────────────────────────────────────┘
```

</div>

---

## 📦 Install

### Step 1 — Install upstream `blender-mcp`

Get the official MCP addon from [**ahujasid/blender-mcp**](https://github.com/ahujasid/blender-mcp) and enable it inside Blender (Preferences → Add-ons → Install). Follow their README for Claude / desktop-app hookup.

```bash
# In Blender: Edit → Preferences → Add-ons → Install → pick addon.py → enable
# In a 3D viewport: press N → BlenderMCP tab → click Connect to Claude
```

### Step 2 — (Optional, recommended) Apply this repo's enhancement patch

The upstream addon gives you `execute_code` as the universal escape hatch. This patch adds **first-class introspection handlers** so agents don't have to write Python strings for every action.

```bash
# Back up the original
cp "<blender-addons>/blender_mcp.py" "<blender-addons>/blender_mcp.py.bak"

# Drop in the enhanced version
cp patches/blender_mcp_enhanced.py "<blender-addons>/blender_mcp.py"

# Restart Blender, click Connect to Claude again
```

### Step 3 — Point your agent at `SKILL.md`

The skill file is framework-neutral. Paste it into Claude Code as a skill, feed it to your own prompt, or read it as a human guide.

---

## 🛠️ Universal handlers

After the patch, the MCP server exposes:

| 🔧 Command | 📥 Params | 📤 Purpose |
|---|---|---|
| `list_addons` | — | Every enabled addon key |
| `inspect_addon` | `{"name":"stablegen"}` | Prefs + namespaces (name match + source scan) |
| `list_operator_namespaces` | — | Every `bpy.ops.*` namespace |
| `inspect_ops_namespace` | `{"namespace":"sna"}` | All ops + descriptions + param schema |
| `call_operator` | `{"operator":"ns.name","params":{…}}` | Invoke anything |
| `get_addon_prefs` / `set_addon_prefs` | `{"name":"<addon>", "<key>":…}` | R/W prefs + `save_userpref` |
| `get_scene_prop` / `set_scene_prop` | `{"name":"<path>","value":…}` | Scene-level state with dotted paths |
| `find_scene_props` | `{"pattern":"<substr>"}` | Substring search over scene props |
| `get_viewport_screenshot` | — | PNG capture for visual feedback |

<br/>

<details>
<summary><b>🧪 Example: controlling any new plugin in three commands</b></summary>

```bash
# 1. Did the plugin register correctly?
python3 scripts/mcp_client.py list_addons

# 2. What does it expose?
python3 scripts/mcp_client.py inspect_addon '{"name":"my-new-plugin"}'
#   → preferences, discovered operators (even if namespace is cryptic)

# 3. Run one of its operators
python3 scripts/mcp_client.py call_operator \
  '{"operator":"myplug.do_thing","params":{"strength":0.5}}'
```

That's it. No custom integration, no fork of the MCP server.

</details>

---

## 🗂️ Catalog pattern

The agent's job is to route *"do this thing"* → *correct operator on correct plugin*. Categories that survive the test of time:

<br/>

<table>
<tr><th>Category</th><th>Typical user intent</th><th>What plugins fit here</th></tr>
<tr>
<td>🧱 <b>Geometry generation</b></td>
<td>"make a 3D model from this image", "generate a cube with holes"</td>
<td>Image-to-mesh (Trellis, Hunyuan3D, Rodin), procedural, parametric primitives</td>
</tr>
<tr>
<td>🎨 <b>AI texturing</b></td>
<td>"texturize this mesh", "make it look like marble"</td>
<td>Diffusion-based multi-view painters (e.g. StableGen)</td>
</tr>
<tr>
<td>🚚 <b>Export pipeline</b></td>
<td>"port to DAZ", "send to Unity", "bake for Marmoset"</td>
<td>Format bridges (GLB/FBX/USD) + engine-specific wizards</td>
</tr>
<tr>
<td>🌀 <b>Creative effects</b></td>
<td>"make it melt", "add rain on it", "pixel-sort this"</td>
<td>Simulation helpers, stylization post-process, mesh deformers</td>
</tr>
<tr>
<td>🦴 <b>Rigging & animation</b></td>
<td>"auto-rig this character", "retarget this mocap", "switch to IK"</td>
<td>Rigify wrappers, MHX bridges, pose libraries, mocap retargeters</td>
</tr>
<tr>
<td>🌿 <b>Environment assets</b></td>
<td>"scatter trees here", "load an HDRI", "add a sky"</td>
<td>Poly Haven, scatter tools, atmosphere shaders</td>
</tr>
<tr>
<td>🧭 <b>Harness</b></td>
<td>internal / not user-facing</td>
<td>The MCP itself, asset browsers, viewport helpers</td>
</tr>
</table>

See [`examples/CATALOG.md`](examples/CATALOG.md) for a blank template. Fork it, fill it in per-environment, commit alongside your agent config.

---

## 🎥 Aesthetic judgment loop

```
  Agent applies operator  ─────────────┐
                                        ▼
  ┌──► get_viewport_screenshot ──► see result ──► judge against intent
  │                                                       │
  │                                                       ▼
  └──── adjust scene/addon props ◄──── "too saturated" / "wrong angle" etc.
```

Diffusion-driven texturing benefits most — every run produces something slightly different, so close the loop: screenshot → evaluate → tweak prompt / seed / strength → re-run until the user's intent is satisfied.

---

## 🧵 Why source-scan for operators?

Some add-ons (anything built with **Serpens** / **SNA**) register operators under cryptic namespaces like `sna.rain_operator_41efc`. The addon folder is called *"genie"* but its ops live under `sna.*`. Name heuristics fail.

The source-scan inspector opens every `.py` in the addon folder, greps `bl_idname = "..."`, and collects the real operator ids. Works for any plugin architecture — conventional or code-generated.

---

## 📂 Repo layout

```
blender-plugin-atlas/
├── README.md                          ← you are here
├── SKILL.md                           ← agent skill file (framework-neutral)
├── LICENSE                            ← MIT
├── scripts/
│   └── mcp_client.py                  ← standalone TCP JSON client
├── patches/
│   └── blender_mcp_enhanced.py        ← enhanced upstream addon
└── examples/
    ├── CATALOG.md                     ← blank plugin-catalog template
    └── discovery_workflow.md          ← step-by-step: "I just installed X"
```

---

## 🙌 Credits

Built on top of [**ahujasid/blender-mcp**](https://github.com/ahujasid/blender-mcp) — go star their repo.  
Source-scan pattern inspired by debugging Serpens-authored plugins in the wild.

<br/>

<div align="center">

*If this saved you an afternoon of hard-coding plugin support — a ⭐ goes a long way.*

</div>
