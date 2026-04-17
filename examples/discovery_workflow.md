# Discovery workflow — "I just installed a new plugin"

Five minutes from "I clicked Install" to "the agent can use it".

## 0. Prereqs

- Blender 4.2+ open with **blender-mcp** running (panel says `Running on port 9876`).
- `patches/blender_mcp_enhanced.py` copied over the upstream addon, server restarted.
- `scripts/mcp_client.py` in your path.

## 1. Confirm registration

```bash
python3 scripts/mcp_client.py list_addons
```

Look for the new entry. Extension-installed plugins appear as `bl_ext.user_default.<name>`; classic add-ons as plain `<name>`.

## 2. First look at preferences + operators

```bash
python3 scripts/mcp_client.py inspect_addon '{"name":"<short-name>"}'
```

You get:

- `preferences` — the full addon-preferences struct, minus private fields.
- `operator_namespaces` — what the inspector thinks is this plugin's slice of `bpy.ops`. If empty, the name didn't match any `bpy.ops.*` and the source scan didn't find `bl_idname` strings either.
- `operators` — actual operator ids pulled from the source files. This is the reliable list.
- `source_path` — where the scanner looked.

## 3. If the plugin uses a cryptic namespace

Some plugins (anything built with Serpens / SNA) register under a generic namespace like `sna.*` with random-hex-suffixed names (`sna.rain_operator_41efc`). That's normal — `inspect_addon` still finds them via source scan.

If you need more detail on the namespace:

```bash
python3 scripts/mcp_client.py inspect_ops_namespace '{"namespace":"sna"}'
```

## 4. Find its scene properties

Most add-ons expose their runtime state as scene properties. The UI labels you see in the plugin's side panel are usually good grep hints:

```bash
python3 scripts/mcp_client.py find_scene_props '{"pattern":"<hint>"}'
```

e.g. `{"pattern":"generation"}` → every scene prop with "generation" in its name. Map those against what the plugin panel labels, and you have the control surface.

## 5. Try it out

Start with a cheap op (no scene state mutation):

```bash
python3 scripts/mcp_client.py call_operator \
  '{"operator":"<ns>.<op>","params":{}}'
```

If you need parameters, `inspect_ops_namespace` already reported them in the `properties` dict. Pass them under `params`.

## 6. Slot it into the catalog

Open `examples/CATALOG.md` (or wherever your project tracks plugins) and add a row under the matching category:

```markdown
| <Plugin name> (<loader>, namespace `<ns>`) | <one-line scope> | "when user says X", "when user says Y" |
```

Append a key-operator block at the bottom:

```
<plugin>:
  <ns>.<op_name>   # brief description
  <ns>.<op_name>   # ...
```

Commit. Done — your agent now routes requests like *"do X"* to this plugin without a fork.

## Common pitfalls

**`operator_namespaces: []`** — the plugin registers nothing under `bpy.ops` at import time. Try opening its side panel once, then re-run inspection; some plugins lazy-register on first UI draw.

**Operator returns `{'CANCELLED'}`** — inspect its poll method by calling `get_rna_type().description`; most often the plugin wants a specific object selected or a specific mode active (edit vs object).

**Preferences show `<unreadable>`** — a pref is a `bpy_prop_collection` or a PointerProperty. Use `execute_code` to iterate over it instead of treating it as a scalar.

**Plugin relies on an external server (e.g. ComfyUI, DAZ CLI)** — handle the connection from the plugin's own prefs (`set_addon_prefs`) and make sure the external service is reachable before invoking its operators.
