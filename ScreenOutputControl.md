# Screen Output Control — MSI Vector GP76

> Verification guide for confirming HDMI output is working after the NVIDIA PRIME + modeset fixes applied in v2.3.

---

## Prerequisites

All three of the following must have been applied before rebooting:

```bash
# 1. Confirm modprobe conf exists
cat /etc/modprobe.d/nvidia-drm.conf
# Expected: options nvidia-drm modeset=1

# 2. Confirm PRIME is set to nvidia
prime-select query
# Expected: nvidia

# 3. Confirm nvidia power services are enabled
systemctl is-enabled nvidia-suspend.service nvidia-hibernate.service nvidia-resume.service
# Expected: enabled (x3)
```

If any of those fail, re-run the fix from the README before continuing.

---

## Step 1 — Reboot

```bash
sudo reboot
```

The PRIME profile, initramfs, and kernel module parameters do not take effect until a full reboot. Suspend/resume is not sufficient.

---

## Step 2 — Verify the dGPU is primary

```bash
prime-select query
```
**Expected:** `nvidia`

```bash
glxinfo | grep "OpenGL renderer"
```
**Expected:** `OpenGL renderer string: NVIDIA GeForce RTX 3070 Ti Laptop GPU`

If `glxinfo` is not installed:
```bash
sudo apt install mesa-utils -y
```

---

## Step 3 — Confirm DRM modeset is active

```bash
cat /sys/module/nvidia_drm/parameters/modeset
```
**Expected:** `Y`

If it prints `N`, the modprobe conf was not picked up by the initramfs. Rebuild and reboot:
```bash
sudo update-initramfs -u
sudo reboot
```

---

## Step 4 — Plug in the HDMI cable, then check detection

With the cable connected to a powered-on external display:

```bash
xrandr --listproviders
```
**Expected output (example):**
```
Providers: number : 2
Provider 0: id: 0x1b8 cap: 0x1, Source Output; crtcs: 4; outputs: 5; associated providers: 1; name: NVIDIA-0
Provider 1: id: 0x48  cap: 0x2, Sink Output; crtcs: 3; outputs: 4; associated providers: 1; name: modesetting
```

```bash
xrandr --query | grep -E "HDMI|DP|connected"
```
**Expected:** A line like `HDMI-0 connected 1920x1080+0+0 ...`

---

## Step 5 — If the port shows as `disconnected`

The kernel sees the port but no display signal. Try forcing it on:

```bash
# Replace HDMI-0 with whatever xrandr --query reported
xrandr --output HDMI-0 --auto
```

If it still shows disconnected, check the kernel's connector state:

```bash
find /sys/class/drm -name "status" | xargs grep -l "connected" 2>/dev/null
```

Each file that prints `connected` maps to a live output. Cross-reference with:
```bash
ls /sys/class/drm/
# Look for: card1-HDMI-A-1 or similar
cat /sys/class/drm/card1-HDMI-A-1/status
```

---

## Step 6 — Enable the external display via KDE System Settings

1. Right-click desktop → **Display and Monitor**
2. The external display should appear as a second screen
3. Set to **Extend**, **Mirror**, or **Only external** as preferred
4. Click **Apply**

Alternatively, via command line (replace display names with your actual output from `xrandr --query`):

```bash
# Extend laptop (eDP-1-1) to the right with HDMI-0
xrandr --output eDP-1-1 --primary --auto --output HDMI-0 --auto --right-of eDP-1-1

# HDMI only (presentation mode)
xrandr --output eDP-1-1 --off --output HDMI-0 --auto

# Mirror
xrandr --output HDMI-0 --same-as eDP-1-1 --auto
```

---

## Failure States & Fixes

| Symptom | Likely Cause | Fix |
|---|---|---|
| `prime-select query` → `on-demand` after reboot | `prime-select nvidia` didn't persist | `sudo prime-select nvidia` + reboot |
| `modeset` = `N` | initramfs not rebuilt with new modprobe conf | `sudo update-initramfs -u` + reboot |
| `HDMI-0 disconnected` in xrandr | Cable/display not recognised at kernel DRM level | Check `/sys/class/drm/*/status`; try `xrandr --output HDMI-0 --auto` |
| `glxinfo` shows Intel renderer | X session started before PRIME switch took effect | Full reboot required (not just re-login) |
| No `NVIDIA-0` in `xrandr --listproviders` | nvidia-drm not loaded | `sudo modprobe nvidia-drm` then check `lsmod \| grep nvidia_drm` |
| External screen black but detected | Resolution/refresh mismatch | `xrandr --output HDMI-0 --mode 1920x1080 --rate 60` |

---

## MUX Switch Note

The GP76 has a hardware MUX switch accessible in the BIOS (`Advanced → Optimus Configuration`). Linux does **not** currently have kernel-level MUX control for this laptop (the `msi-ec` sysfs interface is absent). The BIOS MUX setting and `prime-select` are independent:

| BIOS MUX | `prime-select` | Effect |
|---|---|---|
| Optimus | `on-demand` | iGPU primary, dGPU on-demand (default) |
| Optimus | `nvidia` | dGPU primary via Optimus, HDMI works |
| dGPU Only | *(ignored)* | dGPU exclusive — MUX bypassed, HDMI works, best performance |

For daily Linux use, **BIOS Optimus + `prime-select nvidia`** (current config) is the correct setting.

---

## Quick Reference — All Diagnostic Commands

```bash
prime-select query
cat /sys/module/nvidia_drm/parameters/modeset
glxinfo | grep "OpenGL renderer"
xrandr --listproviders
xrandr --query
find /sys/class/drm -name "status" | xargs grep -l "connected" 2>/dev/null
systemctl is-enabled nvidia-suspend.service nvidia-hibernate.service nvidia-resume.service
nvidia-smi
```
