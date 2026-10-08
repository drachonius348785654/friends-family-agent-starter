#!/usr/bin/env python3
"""Materialise a captured herdr layout manifest into the live session.

Typical use — on the LAPTOP, to mirror the DESKTOP:

    python3 herdr/apply.py                 # dry run: prints the plan, changes nothing
    python3 herdr/apply.py --apply         # actually build it

Manifest selection: with no argument it picks the manifest in herdr/layout/ whose
`source_chassis` differs from this machine's chassis (laptop -> desktop.json,
desktop -> laptop.json). Pass a path to override.

What it does, per workspace in the manifest:
  1. reuse a workspace with a matching label, else `workspace.create`
  2. per tab: reuse a tab with a matching label, else `tab.create`
  3. `layout.apply` that tab's captured pane/split tree
  4. `layout.export` the result and `agent.start` each captured agent into the
     corresponding pane, replaying its recorded `--provider/--model` args

It only ADDS. It never closes, renames, or moves anything that already exists.
"""

import argparse
import json
import os
import re
import socket
import sys
import time

HOME = os.path.expanduser("~")


def socket_path() -> str:
    return os.environ.get("HERDR_SOCK",
                          os.path.join(HOME, ".config", "herdr", "herdr.sock"))


def call(method: str, params: dict | None = None, timeout: float = 60.0):
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.settimeout(timeout)
    s.connect(socket_path())
    req = {"id": f"apply-{method}", "method": method, "params": params or {}}
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


def expand(path):
    if not path:
        return None
    return os.path.expanduser(path)


def expand_node(node):
    """Return a copy of a LayoutNode with `~` expanded in every pane cwd."""
    if not node:
        return node
    if node.get("type") == "pane":
        out = {"type": "pane"}
        for k in ("label", "command", "env"):
            if node.get(k) is not None:
                out[k] = node[k]
        cwd = expand(node.get("cwd"))
        if cwd:
            out["cwd"] = cwd
        return out
    return {
        "type": "split",
        "direction": node.get("direction"),
        "ratio": node.get("ratio"),
        "first": expand_node(node.get("first")),
        "second": expand_node(node.get("second")),
    }


def leaf_panes(node):
    if not node:
        return []
    if node.get("type") == "pane":
        return [node]
    out = []
    for side in ("first", "second"):
        out.extend(leaf_panes(node.get(side) or {}))
    return out


# NOTE: `agent.start` races the shell of a freshly created pane. Immediately
# after layout.apply the pane can still be initialising, and herdr answers
# `agent_pane_busy: "... is not an available shell"`. It is transient - retry
# rather than failing. (Hit live while applying the desktop roster.)
def safe_agent_name(name: str) -> str:
    """herdr only accepts [a-z0-9_-], 1-32 chars, starting with a letter.

    Manifests are hand-edited, and a model id like `gpt-5.6-luna` is an easy
    thing to paste into the agent name - but herdr rejects the dots outright
    with `invalid_agent_name`. Normalise instead of failing the whole run.
    """
    out = re.sub(r"[^a-z0-9_-]", "-", (name or "").lower())
    out = re.sub(r"-{2,}", "-", out).strip("-")[:32]
    if not out or not out[0].isalpha():
        out = ("agent-" + out)[:32]
    return out


def start_agent(agent: dict, pane_id: str, attempts: int = 60, delay: float = 0.5):
    name = safe_agent_name(agent["name"])
    if name != agent["name"]:
        print(f"    ! agent name {agent['name']!r} is not valid for herdr "
              f"(needs [a-z0-9_-]); using {name!r}")
    last = None
    for _ in range(attempts):
        try:
            return call("agent.start",
                        {"name": name, "kind": agent.get("kind", "pi"),
                         "pane_id": pane_id, "args": agent["args"]}, timeout=300)
        except RuntimeError as exc:
            msg = str(exc)
            if "agent_pane_busy" not in msg and "not an available shell" not in msg:
                raise
            last = exc
            time.sleep(delay)
    raise RuntimeError(f"agent.start {agent['name']} on {pane_id}: still busy ({last})")


# NOTE: `layout.apply` does NOT patch a tab in place. It REPLACES the target tab
# and returns a fresh LayoutDescription carrying a NEW tab_id and NEW pane_ids.
# Always consume its return value — re-exporting the id you passed fails with
# `layout_not_found`, because that tab no longer exists. (Verified by probe, not
# guessed: apply onto wH:t1 came back as wH:t2.)
#
# NOTE: pane.split's target field is `target_pane_id`, NOT `pane`. An unrecognised
# key is ignored and the split lands on the FOCUSED pane instead — which silently
# mutates an unrelated part of the user's session. This script therefore never
# calls pane.split; layout.apply builds the whole tree in one shot.


def pick_manifest(explicit: str | None) -> str:
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    layout_dir = os.path.join(repo, "herdr", "layout")
    if explicit:
        return explicit
    chassis = os.popen("hostnamectl chassis 2>/dev/null").read().strip() or "unknown"
    candidates = []
    for name in sorted(os.listdir(layout_dir)) if os.path.isdir(layout_dir) else []:
        if not name.endswith(".json"):
            continue
        with open(os.path.join(layout_dir, name)) as fh:
            try:
                doc = json.load(fh)
            except json.JSONDecodeError:
                continue
        if doc.get("source_chassis") != chassis:
            candidates.append((os.path.join(layout_dir, name), doc.get("source_chassis")))
    if len(candidates) == 1:
        return candidates[0][0]
    if not candidates:
        raise SystemExit(
            f"No manifest to apply: herdr/layout/ has nothing captured from a chassis "
            f"other than this one ({chassis}).\nRun herdr/capture.py on the other "
            f"machine and commit the result, or pass a path explicitly.")
    raise SystemExit("Ambiguous; pass one explicitly:\n  " +
                     "\n  ".join(p for p, _ in candidates))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("manifest", nargs="?", help="path to a layout manifest")
    ap.add_argument("--apply", action="store_true",
                    help="actually create things (default is a dry run)")
    ap.add_argument("--only", action="append", metavar="WORKSPACE_LABEL",
                    help="limit to one workspace label (repeatable)")
    ap.add_argument("--focus", action="store_true",
                    help="focus each created workspace/tab instead of leaving focus alone")
    args = ap.parse_args()

    try:
        path = pick_manifest(args.manifest)
    except SystemExit as exc:
        print(exc, file=sys.stderr)
        return 2
    with open(path) as fh:
        man = json.load(fh)

    dry = not args.apply
    print(f"manifest : {path}")
    print(f"source   : host={man.get('source_host')} chassis={man.get('source_chassis')} "
          f"captured={man.get('captured_at')}")
    print(f"mode     : {'DRY RUN (nothing will change)' if dry else 'APPLY'}")
    print()

    try:
        live_ws = call("workspace.list")["workspaces"]
        live_tabs = call("tab.list")["tabs"]
    except (OSError, RuntimeError) as exc:
        print(f"ERROR: cannot talk to herdr ({exc}). Is the server running?", file=sys.stderr)
        return 1

    ws_by_label = {w.get("label"): w for w in live_ws}

    for ws in man["workspaces"]:
        label = ws.get("label")
        if args.only and label not in args.only:
            continue
        existing = ws_by_label.get(label)
        spare_tab = None
        if existing:
            ws_id = existing["workspace_id"]
            print(f"workspace {label!r}: exists as {ws_id}")
        elif dry:
            ws_id = f"<new workspace {label!r}>"
            print(f"workspace {label!r}: would CREATE")
        else:
            call("workspace.create", {"label": label, "focus": bool(args.focus)})
            live_ws = call("workspace.list")["workspaces"]
            ws_id = [w for w in live_ws if w.get("label") == label][-1]["workspace_id"]
            # A fresh workspace arrives with one empty tab already. Reuse it for
            # the first manifest tab rather than leaving a junk "1" tab behind.
            live_tabs = call("tab.list")["tabs"]
            fresh = [t for t in live_tabs if t["workspace_id"] == ws_id]
            spare_tab = fresh[0]["tab_id"] if fresh else None
            print(f"workspace {label!r}: created as {ws_id}")

        for idx, tab in enumerate(ws["tabs"]):
            tlabel = tab.get("label")
            same_ws = [t for t in live_tabs
                       if t.get("label") == tlabel and t.get("workspace_id") == ws_id]
            if same_ws:
                tab_id = same_ws[-1]["tab_id"]
                if dry:
                    print(f"  tab {tlabel!r}: exists as {tab_id} (layout left alone)")
                    continue
                # Resumable: a previous run may have created the tab and then
                # died before starting its agent, so reconcile against the live
                # agent names instead of skipping the tab blindly.
                panes = leaf_panes(
                    call("layout.export", {"tab_id": tab_id})["layout"].get("root"))
                live_names = {a.get("name") for a in call("agent.list").get("agents", [])}
                todo = [(a, p) for a, p in zip(tab.get("agents", []), panes)
                        if safe_agent_name(a.get("name")) not in live_names]
                if not todo:
                    print(f"  tab {tlabel!r}: exists as {tab_id} (complete)")
                    continue
                started = []
                for agent, pane in todo:
                    if not agent.get("args"):
                        print(f"    ! {agent['name']}: no args recorded - skipped")
                        continue
                    start_agent(agent, pane.get("pane_id"))
                    started.append(agent["name"])
                print(f"  tab {tlabel!r}: exists as {tab_id}; started missing {started}")
                continue
            if dry:
                jobs = ", ".join(a["name"] for a in tab.get("agents", [])) or "no agent"
                print(f"  tab {tlabel!r}: would CREATE + layout.apply + start [{jobs}]")
                continue

            params = {"root": expand_node(tab["root"]), "tab_label": tlabel,
                      "focus": bool(args.focus)}
            if idx == 0 and spare_tab:
                # Replace the empty tab a new workspace was born with, so we don't
                # leave a junk tab behind. layout.apply replaces it in place.
                params["tab_id"] = spare_tab
                spare_tab = None
                action = "adopted the new workspace's initial tab"
            else:
                # workspace_id + tab_label makes layout.apply create a new tab.
                params["workspace_id"] = ws_id
                action = "created"

            layout = call("layout.apply", params)["layout"]
            tab_id = layout["tab_id"]
            panes = leaf_panes(layout.get("root"))
            live_tabs = call("tab.list")["tabs"]
            started = []
            for agent, pane in zip(tab.get("agents", []), panes):
                if not agent.get("args"):
                    print(f"    ! {agent['name']}: no args recorded - skipped "
                          f"(fill it in the manifest)")
                    continue
                start_agent(agent, pane.get("pane_id"))
                started.append(agent["name"])
            print(f"  tab {tlabel!r}: {action} as {tab_id}; started {started or 'no agents'}")

    print()
    print("dry run complete - re-run with --apply to build it" if dry else "done")
    return 0


if __name__ == "__main__":
    sys.exit(main())
