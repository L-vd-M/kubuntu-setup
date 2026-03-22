# Review — kubuntu-setup Playbook

> Reviewed: 2026-03-22
> Scope: All task files, with focus on the display/graphics problem.


## Part A — Graphics Issues (Display Problem)

These are the issues most likely causing Lourens's display problem after reboot.


### A1. Incomplete Xorg Configuration for Hybrid Graphics (HIGH — likely root cause)

**File:** `tasks/graphics.yml:148-169`

The `20-nvidia.conf` Xorg config only defines a `Device` section with `PrimaryGPU "yes"`. On a hybrid Optimus laptop where the internal panel is wired to the Intel iGPU and external monitors are wired to the NVIDIA dGPU, this is insufficient.

With `prime-select nvidia`, X starts with NVIDIA as the primary renderer. But the internal laptop panel still physically connects to the Intel iGPU. For the laptop screen to work, the display manager must set up **reverse PRIME** output sourcing (`xrandr --setprovideroutputsource modesetting NVIDIA-0`). Ubuntu's `nvidia-prime` package normally installs scripts in SDDM to do this, but the manual `20-nvidia.conf` with `PrimaryGPU "yes"` can **interfere** with the automatic setup — especially if the configuration is incomplete or conflicts with what `nvidia-prime` expects.

**Symptom:** Either the laptop screen goes dark (iGPU panel not reverse-PRIME'd) or external monitors go dark (dGPU not initialised properly), depending on the race between X, SDDM, and the manual config.

**Fix:** Either remove the manual Xorg config entirely and let `nvidia-prime` handle it automatically, or provide a complete multi-GPU Xorg configuration including a `ServerLayout` section and both GPU devices.


### A2. Wayland vs X11 Uncertainty (HIGH)

Kubuntu 24.04+ with KDE Plasma 6 defaults to **Wayland**, not X11. The entire graphics configuration in the playbook is X11-focused:

- Xorg config files (`/etc/X11/xorg.conf.d/`)
- `prime-select nvidia` (designed for X11 PRIME)
- `AllowEmptyInitialConfiguration` (Xorg-specific)

Under Wayland, none of these X11 configurations apply to the compositor. KWin under Wayland handles GPU selection differently. If Lourens's system boots into a Wayland session, the Xorg configs are irrelevant and the display setup falls back to defaults — which may not handle the hybrid GPU correctly.

**Fix:** Detect whether the target session is Wayland or X11 and configure accordingly. Alternatively, force X11 for SDDM if Wayland support with NVIDIA is not yet reliable.


### A3. GRUB Parameter Accumulation on Re-runs (MEDIUM)

**File:** `tasks/graphics.yml:117-122`

The `lineinfile` regex uses a negative lookahead on `nvidia_drm.modeset` only. This means:

- If `nvidia_drm.modeset` is already present but `NVreg_PreserveVideoMemoryAllocations` or `NVreg_DynamicPowerManagement` are missing, the task **silently skips** — it won't add the missing params.
- Each successful run appends params with a leading space, so multiple runs accumulate extra whitespace.
- The hibernation task (`hibernation.yml:111-115`) uses the same pattern (negative lookahead on `resume=UUID`), and both modify the same GRUB line. They can interact badly — if one succeeds first, the other's regex may no longer match the expected line format.

**Fix:** Use a single, unified GRUB parameter management approach instead of multiple independent `lineinfile` tasks that fight over the same line.


### A4. Missing `nvidia-drm fbdev=1` for Driver 550+ (MEDIUM)

**File:** `tasks/graphics.yml:176-183`

The modprobe config only sets `modeset=1`. For NVIDIA driver 550+, the `fbdev=1` option is recommended to enable the NVIDIA framebuffer device (`nvidiafb`), which provides proper console output and display initialisation on all connected monitors during early boot. Without it, some outputs may not initialise until the display manager starts — and if the display manager setup fails, those outputs stay dark.

**Fix:** Add `options nvidia-drm modeset=1 fbdev=1` to the modprobe config.


### A5. NVIDIA Detection Grep Is Less Specific Than AMD/Intel (LOW)

**File:** `tasks/graphics.yml:10`

The NVIDIA detection uses `lspci | grep -i nvidia` which matches **any** PCI device with "nvidia" — including audio controllers (line 22 of `lshw` output: "GA104 High Definition Audio Controller"). The AMD and Intel detection correctly filter with `grep -iE "vga|display"`, but NVIDIA does not.

On this specific laptop this doesn't cause a problem (the NVIDIA GPU is present), but on a hypothetical system with only an NVIDIA audio device, it would incorrectly set `has_nvidia: true`.

**Fix:** Add `grep -iE "vga|display|3d"` filter to NVIDIA detection, consistent with AMD and Intel.


### A6. `update-initramfs` Runs Unconditionally (LOW)

**File:** `tasks/graphics.yml:319-322`

`update-initramfs -u` runs every time the playbook executes, even if no GPU changes were made. This is slow and unnecessary on re-runs.

**Fix:** Only run when GPU-related configuration files actually changed.


## Part B — MUX Switch Findings


### MSI Vector GP76 12UGS MUX Switch

The MSI Vector GP76 12UGS **has a hardware MUX switch**. It can physically route the internal laptop panel between the Intel iGPU and the NVIDIA dGPU.

#### Display Wiring

| Port | Wired to | Notes |
|---|---|---|
| HDMI 2.1 (rear) | NVIDIA dGPU | Only active when dGPU is powered on |
| Mini DisplayPort 1.4 (rear) | NVIDIA dGPU | Same as HDMI |
| USB-C (DP Alt Mode, left) | Intel iGPU (likely) | Works in all PRIME modes |
| Internal panel (eDP) | iGPU (Optimus) or dGPU (dGPU-only) | MUX controls this |

#### Available Modes

| Mode | How to set | Internal panel | External (HDMI/mDP) | Battery |
|---|---|---|---|---|
| Optimus + on-demand | BIOS: Optimus, `prime-select on-demand` | iGPU | **Off** (dGPU power-gated) | Best |
| Optimus + nvidia | BIOS: Optimus, `prime-select nvidia` | iGPU (via reverse PRIME) | **On** | Moderate |
| dGPU Only | BIOS: dGPU Only | dGPU (via MUX) | **On** | Worst |

#### Linux Control

**There is no Linux tool that can toggle the hardware MUX switch** on MSI laptops. The MUX is controlled by:

- **BIOS:** `Advanced → Optimus Configuration` — switch between "Optimus" and "dGPU Only". This is the recommended method from Linux.
- **MSI Center (Windows only):** GPU Switch setting. Some firmware versions grey out the BIOS option, making this the only way.

The `msi-ec` kernel module does not expose GPU switching registers. EnvyControl (`envycontrol -s nvidia`) achieves a similar software-level effect to `prime-select nvidia` but with cleaner integration on KDE/SDDM.

#### Recommendation

For reliable multi-monitor (laptop + external) in Optimus mode, the current `prime-select nvidia` approach is correct in principle but the Xorg/display manager configuration needs fixing (see A1, A2).

For maximum simplicity, Lourens could set the BIOS to "dGPU Only" — this bypasses all hybrid graphics complexity and makes all displays route through NVIDIA. The trade-off is worse battery life and no iGPU video decode.


## Part C — Issues in Other Task Files


### C1. gtop Install Fails — npm Not Available Yet (BUG)

**File:** `tasks/system.yml:96-114`

`system.yml` runs **before** `programming.yml` in the playbook order. It tries to install `gtop` via `npm`, but NVM and Node.js are not installed until `programming.yml`. The `which npm` check will fail, so gtop is silently skipped on first run.

**Fix:** Move gtop install after the NVM/Node.js setup, or move it into `programming.yml`.


### C2. Fish Shell PPA Targets v3, Not v4 (OUTDATED)

**File:** `tasks/system.yml:217`

The PPA `ppa:fish-shell/release-3` provides Fish 3.x. Fish 4.x is the current release. If Lourens wants Fish 4.x, the PPA needs updating to `ppa:fish-shell/release-4` (if available) or Fish should be installed from a different source.


### C3. Duplicate Package Installs Across Files (MINOR)

`curl`, `wget`, and `git` are installed/checked in both `check_prerequisites.yml` and `programming.yml`. Not harmful but adds unnecessary run time.


### C4. Antigravity Uses Deprecated `pip install` (BUG on newer Ubuntu)

**File:** `tasks/programming.yml:136-143`

Ubuntu 24.04 enforces PEP 668 (externally managed Python). Running `pip3 install PyQt5 pynput` outside a virtual environment will fail with "externally-managed-environment" error.

**Fix:** Use `pipx`, a virtual environment, or install the system packages (`python3-pyqt5`) instead.


### C5. Obsidian Re-Install Fails on Re-run (BUG)

**File:** `tasks/productivity.yml:33-38`

`mv squashfs-root /opt/obsidian` will fail if `/opt/obsidian` already exists from a previous run. The task doesn't remove the old directory first.

**Fix:** Add `rm -rf /opt/obsidian` before the move, or use `creates:` guard.


### C6. Zotero Download URL Hardcodes x86_64 (BUG on arm64)

**File:** `tasks/productivity.yml:147`

The Zotero URL uses `platform=linux-x86_64` regardless of the `dpkg_arch` variable. On arm64 this would download the wrong binary.

**Fix:** Use `dpkg_arch` to select the correct platform.


### C7. Snap Install `changed_when` References Wrong Variable (BUG)

**File:** `tasks/productivity.yml:288`

`changed_when: "'installed' in snap_prod_install.stdout"` — but `snap_prod_install` is a loop register, so it's a list of results, not a single result. This will always evaluate to false or error.

**Fix:** Use `item.stdout` or remove the `changed_when`.


### C8. WinApps `install.sh` May Hang (RISK)

**File:** `tasks/productivity.yml:240`

The WinApps install script is interactive. Running it in an automated playbook may cause the playbook to hang waiting for input.


### C9. Hibernation `initramfs resume` File Format (BUG)

**File:** `tasks/hibernation.yml:96-100`

The resume file writes: `RESUME=UUID=xxx resume_offset=yyy`

The `initramfs-tools` `RESUME` configuration only recognises `RESUME=UUID=xxx`. The `resume_offset` is not a valid initramfs-tools parameter — it is only used in the GRUB command line. Having it on the same line in the resume file may cause `initramfs-tools` to misparse the value.

**Fix:** The resume file should only contain `RESUME=UUID=xxx`. The `resume_offset` belongs only in GRUB.


### C10. `dd` Uses `bs=1G` for Swapfile (MINOR)

**File:** `tasks/hibernation.yml:31`

`bs=1G` makes `dd` allocate a 1 GB buffer. While this works on a 32 GB system, `bs=1M count=<size_in_mb>` is a safer pattern that works on memory-constrained systems.


### C11. Inverted Log Messages in Prerequisites (COSMETIC)

**File:** `tasks/check_prerequisites.yml:65-69, 88-91, 111-113`

The log messages for curl, wget, and git say "Installed" when `rc == 0` (meaning the tool was already present) and "Already installed" when `rc != 0` (meaning it was missing). The labels are inverted.


### C12. VirtualBox GPG Key Not Dearmored (POTENTIAL BUG)

**File:** `tasks/system.yml:125-130`

The VirtualBox key is downloaded as `.asc` (ASCII-armored) to `/etc/apt/keyrings/`. Modern APT with `signed-by=` expects either a dearmored (binary `.gpg`) file or handles `.asc` transparently depending on the APT version. On older Ubuntu this might cause signature verification failures.


### C13. Secure Boot MOK Enrollment Missing from `graphics.yml`

The README (lines 118-157) documents MOK enrollment for Secure Boot, and the codebase working summary (line 223) describes it in detail, but the actual `graphics.yml` task file does **not contain** any MOK enrollment tasks. Either the tasks were removed at some point or the documentation is ahead of the implementation.
