---
name: aur-install
description: >
  REQUIRED pattern for installing packages on your system from the agent
  shell. Use when the user asks to install any package (official repo or AUR).
  Covers: repo checks, the build / pkexec-install two-step for AUR packages,
  the absolute-path requirement for pkexec pacman -U, and recovery of
  interrupted installs from the build cache.
---

# Package Installation Pattern (Arch-based distro + agent shell)

The agent shell cannot answer `sudo` password prompts. Package-manager
commands fail at the final install step with
`sudo: a terminal is required to read the password`. This is EXPECTED, not a
build failure. Never conclude the package failed to install without checking
whether the build actually succeeded.

## Official repo packages

```bash
# 1. Check availability
pacman -Si <pkg>          # empty output = not in repos, use AUR flow

# 2. Install (prompts the user graphically via pkexec)
pkexec pacman -S --noconfirm --needed <pkg>
```

## AUR packages — the two-step

```bash
# Step 1: build (runs as the user; safe to run from the agent shell)
yay -S --noconfirm <pkg>
# Expected tail output: build succeeds, then "sudo: a terminal is required"
# followed by "error installing ..." — the PKG tarball IS built.

# Step 2: install the built package (prompts the user graphically)
pkexec pacman -U --noconfirm ~/.cache/yay/<pkg>/<pkg>-*-x86_64.pkg.tar.zst
```

**CRITICAL: always pass an ABSOLUTE path to `pkexec pacman -U`.** pkexec does
not reliably inherit the caller's working directory — a relative path fails
with `could not find or read package` even when the file exists.

**CRITICAL: use the main package tarball, not the `-debug` one.** AUR builds
often produce both (e.g. `<pkg>-debug-...`). Installing the debug package
alone is wrong.

## Upgrading, and packages shadowed by a repo

Some distro package-manager wrappers (e.g. `omarchy pkg add` /
`omarchy pkg aur add`) are **install-if-missing only** — wrapped so that for
an already-installed package they are a no-op. **They can never upgrade
anything.** If a package sits at an older version than upstream and neither
the distro update path nor the AUR-add path will touch it, that is the
expected behavior, not a bug.

When a repo package shadows an AUR package that is *newer*, force the AUR
source explicitly:

```bash
yay -S --aur --noconfirm <pkg>       # -a/--aur: assume targets are from the AUR
```

To **build only** (rootless, for the two-step above), seed the build dir so a
large source is not fetched twice, then `makepkg`:

```bash
BUILD=~/.cache/yay/<pkg>; mkdir -p "$BUILD/src"; cd "$BUILD"
curl -s -o PKGBUILD "https://aur.archlinux.org/cgit/aur.git/plain/PKGBUILD?h=<pkg>"
cp /path/to/already-downloaded-source "$BUILD/src/<exact source filename>"
makepkg -f --noconfirm
```

Do this when a `-bin` AUR package merely repacks an upstream release artifact
you already have — but **first confirm `sha256sums` in the PKGBUILD matches
`sha256sum` of your copy.** (`$srcdir` is `<builddir>/src`.)

### Never install an upstream artifact whose internal pkgname differs

Upstream release packages often use a different internal name than the distro
package. Installing one directly can **collide** with an existing package's
files instead of replacing it. Check `.PKGINFO`
(`tar -xOf <pkg> .PKGINFO`) before ever reaching for a vendor artifact; prefer
an AUR repack whose name matches the installed package.

## If the build itself needs missing deps

1. Read deps: `grep -E "^depends|^makedepends" ~/.cache/yay/<pkg>/.SRCINFO`
2. Check what's missing: `pacman -T <dep1> <dep2> ...` (prints missing ones)
3. `pkexec pacman -S --noconfirm --needed <missing...>`
4. Build directly: `cd ~/.cache/yay/<pkg> && makepkg -sf --noconfirm`
5. Then step 2 above.

## Recovery / verification

- Interrupted installs: built tarballs persist in `~/.cache/yay/<pkg>/` —
  just rerun step 2.
- Verify: `pacman -Q <pkg>` and `which <pkg>`.
- Never run makepkg/yay as root.
- Qt/GUI packages may print nothing for `--version` in a terminal; trust
  `pacman -Q` instead.
