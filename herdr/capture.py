#!/usr/bin/env python3
"""Capture a live herdr session's layout + agent roster into a portable manifest.

Run this ON THE MACHINE YOU WANT TO COPY FROM (normally the desktop).

It talks to the herdr server over its unix socket, using the documented
`layout.export` / `workspace.list` / `tab.list` / `pane.list` / `agent.list`
API methods (see `herdr api schema --json`).

For every tab it exports the real pane/split tree, and for every pane holding a
pi agent it recovers `provider` + `modelId` from that session's JSONL, so the
launch command can be reconstructed as:

    pi --provider <provider> --model <modelId>

Output: herdr/layout/<hostname>.json   (portable: $HOME is rewritten to `~`)

Nothing is written to the live session; this is read-only.
"""

import argparse
import json
import os
import socket
import sys
from datetime import datetime, timezone

HOME = os.path.expanduser("~")


def socket_path() -> str:
    return os.environ.get("HERDR_SOCK",
                          os.path.join(HOME, ".config", "herdr", "herdr.sock"))


def call(method: str, params: dict | None = None, timeout: float = 20.0):
    """One request/response round-trip against the herdr socket."""
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.settimeout(timeout)
    s.connect(socket_path())
    req = {"id": f"capture-{method}", "method": method, "params": params or {}}
    s.sendall((json.dumps(req) + "\n").encode())
    buf = b""
    try:
        while b"\n" not in buf:
            chunk = s.recv(1 << 20)
            if not chunk:
                break
            buf += chunk
    finally:
        s.close()
    text = buf.decode(errors="replace").strip()
    if not text:
        raise RuntimeError(f"{method}: empty response")
    msg = json.loads(text)
    if "error" in msg:
        raise RuntimeError(f"{method}: {msg['error']}")
    return msg.get("result", {})


def tilde(path: str | None) -> str | None:
    if not path:
        return path
    if path == HOME:
        return "~"
    if path.startswith(HOME + os.sep):
        return "~" + path[len(HOME):]
    return path


# ── model recovery ─────────────────────────────────────────────────────────

_model_cache: dict[str, tuple[str, str] | None] = {}


def model_from_session(path: str | None):
    """Last `model_change` in a pi session JSONL -> (provider, modelId)."""
    if not path or not os.path.exists(path):
        return None
    if path in _model_cache:
        return _model_cache[path]
    found = None
    try:
        with open(path, "r", errors="replace") as fh:
            for line in fh:
                if '"model_change"' not in line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if entry.get("type") == "model_change":
                    prov, mid = entry.get("provider"), entry.get("modelId")
                    if prov and mid:
                        found = (prov, mid)
    except OSError:
        found = None
    _model_cache[path] = found
    return found


def leaf_panes(node: dict) -> list[dict]:
    """Flatten a LayoutNode tree down to its `pane` leaves, left-to-right."""
    if not node:
        return []
    if node.get("type") == "pane":
        return [node]
    out = []
    for side in ("first", "second"):
        out.extend(leaf_panes(node.get(side) or {}))
    return out


def scrub(node: dict | None) -> dict | None:
    """Rewrite $HOME -> ~ and drop volatile fields so the manifest is portable."""
    if not node:
        return node
    if node.get("type") == "pane":
        keep = {"type": "pane"}
        for k in ("label", "cwd", "command"):
            if node.get(k) is not None:
                keep[k] = tilde(node[k]) if k == "cwd" else node[k]
        if node.get("env"):
            keep["env"] = node["env"]
        return keep
    return {
        "type": "split",
        "direction": node.get("direction"),
        "ratio": node.get("ratio"),
        "first": scrub(node.get("first")),
        "second": scrub(node.get("second")),
    }


# ── main ───────────────────────────────────────────────────────────────────

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-o", "--output", help="output path (default herdr/layout/<host>.json)")
    ap.add_argument("--stdout", action="store_true", help="print instead of writing")
    args = ap.parse_args()

    host = socket.gethostname()
    chassis = os.popen("hostnamectl chassis 2>/dev/null").read().strip() or "unknown"
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Keyed on CHASSIS, not hostname: both machines are named `omarchy`, so a
    # hostname-keyed file would collide and each capture would clobber the other.
    out_path = args.output or os.path.join(repo, "herdr", "layout", f"{chassis}.json")

    try:
        workspaces = call("workspace.list")["workspaces"]
        tabs = call("tab.list")["tabs"]
        panes = call("pane.list")["panes"]
        agents = call("agent.list").get("agents", [])
    except (OSError, RuntimeError) as exc:
        print(f"ERROR: cannot talk to herdr ({exc}). Is the server running?",
              file=sys.stderr)
        return 1

    agent_by_pane = {a["pane_id"]: a for a in agents}

    manifest = {
        "version": 1,
        "source_host": host,
        "source_chassis": chassis,
        "captured_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "notes": ("Generated by herdr/capture.py. Review every \"TODO\" and every "
                  "\"unresolved\" entry before relying on this."),
        "workspaces": [],
    }

    unresolved: list[str] = []

    for ws in sorted(workspaces, key=lambda w: w.get("number", 0)):
        ws_out = {
            "label": ws.get("label") or str(ws.get("number")),
            "number": ws.get("number"),
            "tabs": [],
        }
        for tab in sorted([t for t in tabs if t["workspace_id"] == ws["workspace_id"]],
                          key=lambda t: t.get("number", 0)):
            try:
                layout = call("layout.export", {"tab_id": tab["tab_id"]})["layout"]
            except (OSError, RuntimeError) as exc:
                print(f"WARN: layout.export {tab['tab_id']} failed: {exc}", file=sys.stderr)
                continue

            root = scrub(layout.get("root"))
            leaves = leaf_panes(layout.get("root") or {})
            tab_panes = [p for p in panes if p["tab_id"] == tab["tab_id"]]

            agent_entries = []
            for leaf in leaves:
                pane_id = leaf.get("pane_id")
                info = agent_by_pane.get(pane_id)
                if not info:
                    continue
                entry = {
                    "name": info.get("name") or info.get("agent") or "pi",
                    "kind": info.get("agent") or "pi",
                }
                prov_model = None
                if entry["kind"] == "pi":
                    prov_model = model_from_session(
                        (info.get("agent_session") or {}).get("value"))
                if prov_model:
                    entry["args"] = ["--provider", prov_model[0], "--model", prov_model[1]]
                else:
                    entry["args"] = None
                    unresolved.append(
                        f'{ws_out["label"]}/{tab.get("label")}: agent "{entry["name"]}" '
                        f'- could not determine provider/model; fill "args" by hand '
                        f'(e.g. ["--provider","openrouter","--model","<org/model>"])')
                agent_entries.append(entry)
            tab_out = {
                "label": tab.get("label") or str(tab.get("number")),
                "number": tab.get("number"),
                "cwd": tilde(tab_panes[0].get("cwd")) if tab_panes else None,
                "root": root,
                "agents": agent_entries,
            }
            ws_out["tabs"].append(tab_out)
        manifest["workspaces"].append(ws_out)

    if unresolved:
        manifest["unresolved"] = unresolved

    text = json.dumps(manifest, indent=2) + "\n"
    if args.stdout:
        sys.stdout.write(text)
    else:
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w") as fh:
            fh.write(text)
        print(f"wrote {out_path}")
        print(f"  workspaces: {len(manifest['workspaces'])}")
        print(f"  tabs:       {sum(len(w['tabs']) for w in manifest['workspaces'])}")
        if unresolved:
            print(f"  NEEDS FILL-IN: {len(unresolved)}")
            for u in unresolved:
                print(f"    - {u}")
        else:
            print("  nothing unresolved ✅")
    return 0


if __name__ == "__main__":
    sys.exit(main())
