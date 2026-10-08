# Optional: Tailscale

A private WireGuard mesh that lets your own devices reach each other by a stable
name/IP from anywhere, **without exposing anything to the public internet**.

## Steps

1. Install Tailscale for your platform (tailscale.com/download). On Omarchy/Arch:

   ```bash
   omarchy pkg add tailscale        # or: sudo pacman -S tailscale
   ```

2. Enable the daemon:

   ```bash
   sudo systemctl enable --now tailscaled
   ```

3. Bring it up and authenticate — this prints a URL to open in a browser:

   ```bash
   sudo tailscale up
   ```

4. *(Optional)* Enable **Tailscale SSH**, so you can SSH by tailnet identity with
   no exposed sshd and no key files:

   ```bash
   sudo tailscale set --ssh
   ```

5. *(Optional)* Make the CLI usable without root:

   ```bash
   sudo tailscale set --operator=$USER
   ```

6. Install the Tailscale app on your phone, sign in to the same tailnet, connect.

7. Verify:

   ```bash
   tailscale status
   ```

   Then from the phone: `ssh <user>@<hostname>` (Tailscale SSH), or reach a
   service on the device's tailnet IP.

## Notes

- Tailscale SSH is served by the daemon. `pkexec` will not work over an SSH
  session (no polkit agent there) — use `sudo`, which prompts on the SSH TTY.
- Devices are addressed by tailnet identity/IP; nothing is exposed beyond the
  tailnet. Keep the tailnet ACLs as tight as you need.
