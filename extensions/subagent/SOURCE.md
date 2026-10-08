Copied from the pi installation's examples directory:

    <pi-install>/examples/extensions/subagent/

Files copied: index.ts, agents.ts.

Copied rather than symlinked on purpose: a symlink into a version-pinned install
breaks on the next pi upgrade, and a symlink into `latest` would silently change
behaviour underfoot. To update, re-copy from the then-current install and re-run
the smoke test described in ../README.md.

Agent definitions live in ~/.pi/agent/agents/*.md (user scope).
