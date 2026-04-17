<div align="center">

# 🧩 Blender Plugin Atlas

### *A Claude Code skill for driving Blender via any installed plugin*

[![Claude Code skill](https://img.shields.io/badge/Claude%20Code-skill-D97757?style=for-the-badge)](https://claude.com/product/claude-code)
[![Blender 4.2+](https://img.shields.io/badge/Blender-4.2%2B-F5792A?style=for-the-badge&logo=blender&logoColor=white)](https://www.blender.org/)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![MCP](https://img.shields.io/badge/MCP-compatible-7B2CBF?style=for-the-badge)](https://github.com/ahujasid/blender-mcp)

<br/>

**Tell Claude *"texturize this mesh"*, *"make it rain"*, *"rig this character"*, *"export to DAZ"* —  
the skill inspects your installed Blender plugins at runtime and picks the right operator.**

<br/>

[What it is](#ℹ️-what-it-is) · [Install](#📦-install) · [Universal handlers](#🛠️-universal-handlers) · [Catalog pattern](#🗂️-catalog-pattern) · [Examples](examples/)

</div>

---

## ℹ️ What it is

**This repo is a skill**, not a product. It lives inside Claude Code (or any agent that can load a `SKILL.md` and call tools over JSON) and teaches the agent how to drive Blender through the [blender mcp addon](https://github.com/ahujasid/blender-mcp).

No license, no binaries to ship. Just a guide + a patch + a small client script. Clone or copy into your own `~/.claude/skills/` folder.

## ✨ What the skill does

<table>
<tr>
<td width="33%" valign="top">

### 🔍 Runtime discovery
No hard coded plugin lists. The agent calls `inspect_addon` at runtime, reads operators, prefs, scene props.

</td>
<td width="33%" valign="top">

### 🧬 Source scan inspector
Handles opaque plugins (Serpens / SNA) by grepping `bl_idname` from source files. Finds every operator even when naming is cryptic.

</td>
<td width="33%" valign="top">

### 🎨 Aesthetic feedback loop
Viewport screenshot after each action → agent sees the result → adjusts parameters → iterates.

</td>
</tr>
<tr>
<td valign="top">

### 🔌 Three control channels
Real time MCP socket · headless `bpy` scripts · bridges to ComfyUI / DAZ / asset libraries.

</td>
<td valign="top">

### 🗂️ Capability catalog
Maps user intent → category → plugin → operator. Growable, plain markdown.

</td>
<td valign="top">

### 🧠 Drop in
Paste `SKILL.md` into Claude Code as a skill. Works with any agent that can send JSON over TCP.

</td>
</tr>
</table>

---

## 🎯 The problem this skill solves

> *Every Blender plugin invents its own operator namespace, its own preference schema, its own UI.  
> An agent that wants to orchestrate them all either (a) hard codes support for each, or (b) hands raw Python to the user.*

**This skill picks a third path**: an introspection layer the agent queries at runtime. Install a new add on → agent discovers it → agent knows how to call it. No fork, no rebuild, no human middleman.

<br/>

<div align="center">

```
┌─────────────┐     socket      ┌──────────────────┐
│ Claude Code │ ◄─────────────► │  blender mcp     │
│    agent    │   TCP 9876      │  (this patch)    │
└─────────────┘                 └────────┬─────────┘
                                         │
                 ┌───────────────────────┼───────────────────────┐
                 ▼                       ▼                       ▼
         ┌───────────────┐       ┌───────────────┐       ┌───────────────┐
         │  inspect      │       │  call         │       │  get / set    │
         │  addon        │       │  operator     │       │  scene prop   │
         └───────────────┘       └───────────────┘       └───────────────┘
                 │                       │                       │
                 ▼                       ▼                       ▼
         ┌───────────────────────────────────────────────────────────────┐
         │      🧩 ANY installed Blender add on or extension             │
         │   geometry · texturing · rigging · effects · export · …       │
         └───────────────────────────────────────────────────────────────┘
```

</div>

---

## 📦 Install

### Step 1 — Install upstream `blender mcp`

Get the official MCP addon from [**ahujasid/blender mcp**](https://github.com/ahujasid/blender-mcp) and enable it inside Blender (Preferences → Add ons → Install). Follow their README for Claude / desktop app hookup.

```
In Blender: Edit → Preferences → Add ons → Install → pick addon.py → enable
In a 3D viewport: press N → BlenderMCP tab → click Connect to Claude
```

### Step 2 — (Optional, recommended) Apply this repo's enhancement patch

The upstream addon gives you `execute_code` as the universal escape hatch. This patch adds **first class introspection handlers** so agents don't have to write Python strings for every action.

```
cp "<blender addons>/blender_mcp.py" "<blender addons>/blender_mcp.py.bak"
cp patches/blender_mcp_enhanced.py "<blender addons>/blender_mcp.py"
# restart Blender, click Connect to Claude again
```

### Step 3 — Install the skill into Claude Code

```
git clone https://github.com/MastroMimmo/blenderpluginatlas
cp -r blenderpluginatlas ~/.claude/skills/blender
```

Claude Code picks it up on next session. Trigger it by mentioning Blender in a request.

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
| `get_scene_prop` / `set_scene_prop` | `{"name":"<path>","value":…}` | Scene level state with dotted paths |
| `find_scene_props` | `{"pattern":"<substr>"}` | Substring search over scene props |
| `get_viewport_screenshot` | — | PNG capture for visual feedback |

<br/>

<details>
<summary><b>🧪 Example: controlling any new plugin in three commands</b></summary>

```
python3 scripts/mcp_client.py list_addons
python3 scripts/mcp_client.py inspect_addon '{"name":"my new plugin"}'
python3 scripts/mcp_client.py call_operator '{"operator":"myplug.do_thing","params":{"strength":0.5}}'
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
<td>Image to mesh (Trellis, Hunyuan3D, Rodin), procedural, parametric primitives</td>
</tr>
<tr>
<td>🎨 <b>AI texturing</b></td>
<td>"texturize this mesh", "make it look like marble"</td>
<td>Diffusion based multi view painters (e.g. StableGen)</td>
</tr>
<tr>
<td>🚚 <b>Export pipeline</b></td>
<td>"port to DAZ", "send to Unity", "bake for Marmoset"</td>
<td>Format bridges (GLB/FBX/USD) plus engine specific wizards</td>
</tr>
<tr>
<td>🌀 <b>Creative effects</b></td>
<td>"make it melt", "add rain on it", "pixel sort this"</td>
<td>Simulation helpers, stylization post process, mesh deformers</td>
</tr>
<tr>
<td>🦴 <b>Rigging and animation</b></td>
<td>"auto rig this character", "retarget this mocap", "switch to IK"</td>
<td>Rigify wrappers, MHX bridges, pose libraries, mocap retargeters</td>
</tr>
<tr>
<td>🌿 <b>Environment assets</b></td>
<td>"scatter trees here", "load an HDRI", "add a sky"</td>
<td>Poly Haven, scatter tools, atmosphere shaders</td>
</tr>
<tr>
<td>🧭 <b>Harness</b></td>
<td>internal, not user facing</td>
<td>The MCP itself, asset browsers, viewport helpers</td>
</tr>
</table>

See [`examples/CATALOG.md`](examples/CATALOG.md) for a blank template. Fork it, fill it in per environment, keep it alongside your agent config.

---

## 🎥 Aesthetic judgment loop

```
  Agent applies operator  ─────────────┐
                                        ▼
  ┌──► get_viewport_screenshot ──► see result ──► judge against intent
  │                                                       │
  │                                                       ▼
  └──── adjust scene / addon props ◄──── "too saturated" / "wrong angle" etc.
```

Diffusion driven texturing benefits most — every run produces something slightly different, so close the loop: screenshot → evaluate → tweak prompt / seed / strength → re run until the user's intent is satisfied.

---

## 🧵 Why source scan for operators?

Some add ons (anything built with **Serpens** / **SNA**) register operators under cryptic namespaces like `sna.rain_operator_41efc`. The addon folder is called *"genie"* but its ops live under `sna.*`. Name heuristics fail.

The source scan inspector opens every `.py` in the addon folder, greps `bl_idname = "..."`, and collects the real operator ids. Works for any plugin architecture, conventional or code generated.

---

## 📂 Repo layout

```
blenderpluginatlas/
├── README.md                          ← you are here
├── SKILL.md                           ← the Claude Code skill file
├── scripts/
│   └── mcp_client.py                  ← standalone TCP JSON client
├── patches/
│   └── blender_mcp_enhanced.py        ← enhanced upstream addon
└── examples/
    ├── CATALOG.md                     ← blank plugin catalog template
    └── discovery_workflow.md          ← step by step: "I just installed X"
```

---

## 🙌 Credits

Built on top of [**ahujasid/blender mcp**](https://github.com/ahujasid/blender-mcp) — go star their repo.  
Source scan pattern inspired by debugging Serpens authored plugins in the wild.

<br/>

<div align="center">

*A skill for Claude Code. Not a product, not a library, not a fork.  
If it saved you an afternoon of hard coding plugin support, a ⭐ goes a long way.*

</div>
