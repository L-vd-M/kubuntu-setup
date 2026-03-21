# Kubuntu Setup Playbook — Install Verification Audit

> Verified on **2026-03-20** against the current task files in `tasks/`.

---

## Summary

| Category | Status |
|----------|--------|
| APT packages (standard repos) | ✅ All available |
| GPU driver packages | ✅ All available |
| GPG key URLs | ✅ All reachable |
| Ansible syntax check | ✅ Passed |
| Download URLs | ⚠️ 1 broken (Obsidian) |
| Repository URLs | ⚠️ 1 broken (NodeSource 18.x) |
| Archive format | ⚠️ 1 mismatch (Zotero) |
| VS Code repo config | ⚠️ `signed-by` path mismatch |
| `apt_key` usage | ⚠️ Deprecated (5 occurrences) |

---

## What Is Being Installed

### 1. Prerequisites (`check_prerequisites.yml`)
- **curl**, **wget**, **git**, **build-essential**, **pciutils**, **sudo** — basic system tools

### 2. Graphics Drivers (`graphics.yml`)
- **NVIDIA**: `nvidia-driver-535`, `nvidia-utils-535`, `nvidia-settings`
- **AMD**: `xserver-xorg-video-amdgpu`, `mesa-vulkan-drivers`, `libvulkan1`
- **Intel**: `intel-gpu-tools`, `intel-media-va-driver`, `mesa-vulkan-drivers`, `va-driver-all`

### 3. System Utilities (`system.yml`)
- **Compression**: `zip`, `gzip`, `tar`
- **Editors**: `nano`
- **Monitoring**: `htop`, `gtop` (via npm)
- **Shell**: `fish` (configured safely with user login shell change)
- **Virtualization Hypervisors**:
  - **KVM / QEMU (Type 1 Bare-metal)**: `virt-manager`, `libvirt-daemon-system`, `qemu-system-x86`, `bridge-utils`
  - **VirtualBox 7.0 (Type 2 Hosted)**: `virtualbox-7.0` (via Oracle APT repo)
- **Build tools**: `build-essential`, `linux-headers-generic`

### 4. Programming Tools (`programming.yml`)
- **Git** (also in prereqs)
- **Node.js 22.x** + npm (via NVM)
- **VS Code** (via Microsoft repo)
- **Antigravity** desktop launcher (cloned from GitHub, with PyQt5 + pynput)
- **Telecom Engineering Suite**: `gnuradio`, `wireshark` (with non-root capture configured), `jupyter-notebook`
- **Dev utilities**: `curl`, `wget`, `vim`

### 5. Media & Communication (`media.yml`)
- **Discord** (downloaded `.deb` from official URL)
- **OBS Studio** (`obs-studio` from APT)
- **Spotify** (via Spotify APT repo)
- **VLC** + **FFmpeg** (from APT)

### 6. Productivity & Office (`productivity.yml`)
- **Obsidian** (AppImage dynamically pulled from GitHub releases via API)
- **Zotero** (Dynamic interactive double-menu selection, extracts from Tarball)
- **Academic Suite**: `okular`, `texstudio`, `pandoc` (via APT)
- **Diagramming & Planning**: `drawio`, `superproductivity` (via Snap)
- **Google Chrome** (via Google APT repo)
- **WinApps** (cloned from GitHub, manual installer)

### 7. System Hibernation (`hibernation.yml`)
- **Swap Scaling**: Dynamically resizes the `/swapfile` based on system RAM using `dd`.
- **Bootloader Params**: Calculates root partition UUID and block Offset and updates `GRUB` and `initramfs`.
- **UI Support**: Injects modern Polkit JS rules to seamlessly enable hibernation buttons natively in KDE/GNOME.

---

## Issues Found (What Needs To Be Changed)

### 🔴 Critical — Fixed

#### 1. Obsidian download URL returns **404**
- **File**: `tasks/productivity.yml` line 14
- **Problem**: Obsidian does not host a `latest` tag with a generic AppImage name.
- **Fix Applied**: Updated task to query GitHub API dynamically and filter out `arm64` when running on `x86_64` (and vice versa) utilizing a `dpkg_arch` variable mapping.

#### 2. Zotero archive format mismatch
- **File**: `tasks/productivity.yml`
- **Problem**: Format changed to `.tar.xz`, and user requested the ability to download older versions (6.x, 7.x).
- **Fix Applied**: Implemented a dynamic interactive double-menu prompt that polls Zotero's GitHub tags. The user selects a major and minor version, which is then dynamically downloaded and linked locally in `~/.local/opt` and `~/.local/bin`.

#### 3. Node.js Installation Strategy
- **File**: `tasks/programming.yml` line 40
- **Problem**: NodeSource `node_18.x` repository returned 404. Furthermore, APT repos provide a global Node installation that can conflict with project needs.
- **Fix Approach**: Shifted away from NodeSource completely. Proceeding with **NVM (Node Version Manager)** for per-user installation.

### 🟡 Moderate — May Cause Unexpected Behavior

#### 4. VS Code `signed-by` path does not match `apt_key` destination
- **File**: `tasks/programming.yml` lines 68–77
- **Problem**: The `apt_key` module imports the key to the legacy trusted keyring (`/etc/apt/trusted.gpg`), but the repo line specifies `signed-by=/usr/share/keyrings/microsoft-archive-keyring.gpg` — a file that is never created by the task.
- **Fix**: Either:
  - Remove the `signed-by=` clause from the repo line, **or**
  - Download the key to `/usr/share/keyrings/microsoft-archive-keyring.gpg` directly using `get_url` instead of `apt_key`.

#### 5. `apt_key` module is deprecated (5 uses)
- **Files**: `system.yml` (VirtualBox), `programming.yml` (NodeSource, VS Code), `media.yml` (Spotify), `productivity.yml` (Chrome)
- **Problem**: `apt_key` is deprecated in Ansible and in modern Ubuntu. Keys should be stored per-repo in `/usr/share/keyrings/` or `/etc/apt/keyrings/`.
- **Fix**: Replace each `apt_key` call with a `get_url` that downloads the key to `/usr/share/keyrings/<name>.gpg` and reference that path via `signed-by=` in the corresponding `apt_repository` entry.

### 🟢 Minor / Cosmetic

#### 6. `build-essential` checked twice
- **Files**: `tasks/check_prerequisites.yml` lines 116–136 AND `tasks/system.yml` lines 174–193
- **Problem**: Duplicated check and install for `build-essential`. Not harmful but redundant.
- **Fix**: Remove one of the two occurrences.

#### 7. `nano_install` variable may be undefined
- **File**: `tasks/system.yml` line 55
- **Problem**: When `nano_check.rc != 0` is false (nano already installed), the `Install text editor (nano)` task is skipped and `nano_install` is never set. The log task then references `nano_install.changed`, which will fail.
- **Fix**: Add a `default(false)` filter: `{{ nano_install.changed | default(false) }}` or register the variable unconditionally.

#### 8. Similar undefined variable risk for other conditional installs
- Git install (`programming.yml` line 20): `git_install.changed` may be undefined when skipped
- Node.js install (`programming.yml` line 55): `nodejs_install.changed` when skipped
- VS Code install (`programming.yml` line 91): `vscode_install.changed` when skipped
- OBS install (`media.yml` line 59): `obs_install.changed` when skipped
- Spotify install (`media.yml` line 95): `spotify_install.changed` when skipped
- Chrome install (`productivity.yml` line 128): `chrome_install.changed` when skipped
- Build-essential install (`system.yml` line 192): `build_essential_install.changed` when skipped

---

## What Was Already Correct

| Item | Verification |
|------|-------------|
| All standard APT packages (`curl`, `wget`, `git`, `zip`, `gzip`, `tar`, `nano`, `htop`, `obs-studio`, `vlc`, `ffmpeg`, `virt-manager`, etc.) | ✅ All found in default Ubuntu repos |
| NVIDIA driver packages (`nvidia-driver-535`, `nvidia-utils-535`, `nvidia-settings`) | ✅ Available (v535.288.01) |
| AMD driver packages (`xserver-xorg-video-amdgpu`, `mesa-vulkan-drivers`, `libvulkan1`) | ✅ Available |
| Intel driver packages (`intel-gpu-tools`, `intel-media-va-driver`, `va-driver-all`) | ✅ Available |
| Discord download URL | ✅ Returns 302 → valid `.deb` |
| Spotify GPG key URL | ✅ HTTP 200 |
| VirtualBox GPG key URL | ✅ HTTP 200 |
| Google Chrome GPG key URL | ✅ HTTP 200 |
| Microsoft (VS Code) GPG key URL | ✅ HTTP 200 |
| NodeSource GPG key URL | ✅ HTTP 200 |
| Zotero download URL | ✅ Returns 302 → valid tarball (but format changed) |
| Google Chrome repo and package name (`google-chrome-stable`) | ✅ Available (already have repo configured) |
| `python3-pyqt5`, `python3-pip` (Antigravity deps) | ✅ Available |
| Ansible syntax check | ✅ Passed with no errors |
| Overall playbook structure (pre_tasks → tasks → post_tasks) | ✅ Correct |
| Logging pattern (lineinfile to log_file) | ✅ Consistent across all task files |
| GPU detection logic (lspci grep) | ✅ Correct |
| block/rescue error handling | ✅ Present on all major sections |

### 🛑 March 21, 2026 - Ansible Test Run Audit
- **Successes**: Graphics auto-detection, NVIDIA installations, KVM/Virt-Manager, Node.js, core utilities (Discord, VLC), and prerequisite testing all operated perfectly.
- **Cascading Failures**: 
  1. A massive string of `Permission denied` errors struck `/etc/apt/keyrings`, `/var/lib/dpkg/lock-frontend`, and `/opt/` (affecting Chrome, Spotify, VS Code, Obsidian, VirtualBox, Snaps). 
  2. **Root Cause**: The master playbook lacks global `become: yes`, causing Ansible to execute tasks safely as the user instead of `root`, ignoring the `--ask-become-pass` runtime flag.
  3. **Syntax Collapse**: `tasks/hibernation.yml` crashed the playbook outright because it was copied directly from a standalone controller playbook and retained `hosts: localhost` and `gather_facts: no` headers, which throws syntax errors when natively `included` via tasks.
  4. **The `ansible_env.HOME` Escalation Trap**: Upon injecting global `become: yes`, Ansible aggressively escalates privileges during the `Gathering Facts` phase. Consequently, `ansible_env.HOME` dynamically evaluated to `/root` instead of `/home/lourens`. When subsequent `become: false` tasks (like generating log files in `~/Documents`) attempted to write to what they thought was the local home directory, they crashed attempting to write to `/root/Documents`. **Fix**: Instead of relying on `ansible_env.HOME`, log directories must dynamically pull the true originating user context via `lookup('env', 'SUDO_USER') | default(lookup('env', 'USER')) | regex_replace('^', '/home/')`.
