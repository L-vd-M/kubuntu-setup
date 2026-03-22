# Fix Plan — kubuntu-setup Playbook

> Created: 2026-03-22
> Based on: review.md (all issues approved)


## Stage 1 — Graphics / Display Fix (A1–A6)

The core display problem. These changes must be done together.

### Step 1.1 — Fix Xorg configuration for hybrid graphics (A1)

**File:** `tasks/graphics.yml`

Remove the manual `20-nvidia.conf` that conflicts with `nvidia-prime`'s automatic setup. Replace it with a minimal config that cooperates with Ubuntu's built-in PRIME display offloading. Specifically:

- Remove the `PrimaryGPU "yes"` device-only config.
- Instead, ensure the display manager (SDDM) has a working Xsetup script that runs `xrandr --setprovideroutputsource` for reverse PRIME. Ubuntu's `nvidia-prime` package should install this, but we should verify and create it if missing.

### Step 1.2 — Handle Wayland vs X11 (A2)

**File:** `tasks/graphics.yml`

- Detect whether the system uses Wayland or X11 (check SDDM config, KDE Plasma version).
- For Wayland: ensure `nvidia-drm modeset=1 fbdev=1` is set (required for Wayland compositor), and add `kms` to initramfs modules.
- For X11: apply the Xorg configuration from Step 1.1.
- Optionally: add a task to force X11 on SDDM if Wayland+NVIDIA is unreliable, with a comment explaining when it's safe to switch back.

### Step 1.3 — Unify GRUB parameter management (A3)

**Files:** `tasks/graphics.yml`, `tasks/hibernation.yml`

Replace the multiple competing `lineinfile` tasks with a single robust approach:

- Read the current `GRUB_CMDLINE_LINUX_DEFAULT` value.
- Build the desired parameter list from all sources (NVIDIA params + hibernation resume params).
- Write the final line once, idempotently.
- Call `update-grub` only if the line changed.

This eliminates the negative-lookahead fragility and the interaction between graphics.yml and hibernation.yml.

### Step 1.4 — Add `fbdev=1` to nvidia-drm modprobe config (A4)

**File:** `tasks/graphics.yml`

Change the modprobe config from:
```
options nvidia-drm modeset=1
```
to:
```
options nvidia-drm modeset=1 fbdev=1
```

### Step 1.5 — Fix NVIDIA detection grep (A5)

**File:** `tasks/graphics.yml`

Change:
```
lspci | grep -i nvidia || true
```
to:
```
lspci | grep -i nvidia | grep -iE "vga|display|3d" || true
```

### Step 1.6 — Conditional `update-initramfs` (A6)

**File:** `tasks/graphics.yml`

Only run `update-initramfs -u` when GPU config files actually changed. Register results from the modprobe and nvidia driver tasks, and gate on those.

### Step 1.7 — Add MUX switch / BIOS reminder (B)

**File:** `tasks/graphics.yml`

Add a `debug` message at the end of the NVIDIA block explaining the MUX switch and recommending BIOS settings for the GP76. This is informational only — no configuration change.


## Stage 2 — Hibernation Fixes (C9, C10)

### Step 2.1 — Fix initramfs resume file format (C9)

**File:** `tasks/hibernation.yml`

Change the resume file to only contain:
```
RESUME=UUID=xxx
```
Keep `resume_offset=yyy` only in the GRUB command line.

### Step 2.2 — Use safer `dd` block size (C10)

**File:** `tasks/hibernation.yml`

Change `bs=1G count={{ required_swap_gb }}` to `bs=1M count={{ required_swap_mb }}`.


## Stage 3 — System Task Fixes (C1, C2, C3, C12)

### Step 3.1 — Move gtop install after NVM/Node.js (C1)

**Files:** `tasks/system.yml`, `tasks/programming.yml`

Move the gtop npm install block from `system.yml` into `programming.yml`, after the NVM/Node.js setup.

### Step 3.2 — Update Fish PPA to v4 (C2)

**File:** `tasks/system.yml`

Change `ppa:fish-shell/release-3` to the Fish 4.x source. Verify whether a PPA exists or if fish 4.x needs a different install method.

### Step 3.3 — Remove duplicate package installs (C3)

**Files:** `tasks/check_prerequisites.yml`, `tasks/programming.yml`

Remove the duplicate `curl`, `wget`, `git` install tasks from `programming.yml` since they're already handled in `check_prerequisites.yml`.

### Step 3.4 — Dearmor VirtualBox GPG key (C12)

**File:** `tasks/system.yml`

Pipe the downloaded `.asc` key through `gpg --dearmor` to produce a binary `.gpg` file, then reference that in the `signed-by=` directive.


## Stage 4 — Programming Task Fixes (C4)

### Step 4.1 — Fix Antigravity pip install for PEP 668 (C4)

**File:** `tasks/programming.yml`

Replace `pip3 install PyQt5 pynput` with system packages (`python3-pyqt5`) where available, and use `pipx` or a virtual environment for packages not in APT.


## Stage 5 — Productivity Task Fixes (C5, C6, C7, C8)

### Step 5.1 — Fix Obsidian re-install (C5)

**File:** `tasks/productivity.yml`

Add `rm -rf /opt/obsidian` before moving the extracted AppImage, or add an idempotency guard.

### Step 5.2 — Fix Zotero architecture (C6)

**File:** `tasks/productivity.yml`

Replace the hardcoded `linux-x86_64` with a conditional based on `dpkg_arch`.

### Step 5.3 — Fix Snap changed_when (C7)

**File:** `tasks/productivity.yml`

Fix the `changed_when` to work correctly with loop register variables.

### Step 5.4 — Guard WinApps install.sh (C8)

**File:** `tasks/productivity.yml`

Either skip the WinApps install.sh (just clone the repo and log instructions for manual setup) or check if the script supports non-interactive mode.


## Stage 6 — Prerequisites & MOK (C11, C13)

### Step 6.1 — Fix inverted log messages (C11)

**File:** `tasks/check_prerequisites.yml`

Correct the log labels so "Installed" means newly installed and "Already installed" means already present.

### Step 6.2 — Implement MOK enrollment (C13)

**File:** `tasks/graphics.yml`

Add the Secure Boot MOK enrollment tasks that are documented in the README but missing from the code:

- Check Secure Boot state with `mokutil --sb-state`.
- If enabled and the DKMS signing key exists but is not enrolled, generate a one-time password and run `mokutil --import`.
- Print the password prominently in the Ansible output.
- Add idempotency guard using `mokutil --test-key`.


## Execution Order

Stages 1 and 2 are the priority (display fix + hibernation). Stages 3–6 are independent improvements. Within each stage, steps should be done sequentially. Stages 3–6 can be parallelised.

| Stage | Branch name | Depends on |
|---|---|---|
| 1 | `fix/graphics-display` | — |
| 2 | `fix/hibernation` | Stage 1 (shared GRUB management) |
| 3 | `fix/system-tasks` | — |
| 4 | `fix/programming-tasks` | — |
| 5 | `fix/productivity-tasks` | — |
| 6 | `fix/prerequisites-mok` | Stage 1 (MOK goes in graphics.yml) |
