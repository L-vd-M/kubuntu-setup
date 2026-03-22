# 🖥️ Kubuntu Setup Playbook (v2.2)

> A comprehensive, modular Ansible playbook for automated setup and software installation on Kubuntu systems. Features intelligent graphics driver detection, prerequisite verification, automated hibernation syncing, and detailed execution logging.

**Compatible With**: Kubuntu 22.04 LTS and later  
**Maintained By**: Lourens van der Merwe  

---

## 📖 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation & Usage](#installation--usage)

---

## 🎯 Overview

This Ansible playbook automates the complete setup of a Kubuntu system by installing and configuring a curated selection of modern, productive software. 

**NEW IN v2.2**: 
- ✅ **Dynamic Active GPU Purging:** Automatically detects absent GPUs (e.g., AMD) and purges their unused drivers to reduce kernel bloat.
- ✅ **Secure Architecture**: Dynamic `host_user_home` mapping preventing `/root` escalation traps.
- ✅ **Dynamic Zotero**: Installs dynamically via interactive prompt, allowing you to select versions!
- ✅ **Automated Hibernation**: Swap sizing, bootloader config, Polkit UI rules, and 'hibernate' Fish shell alias.
- ✅ **Rigorous Telemetry**: Detailed `lineinfile` array tracking logging to `~/Documents/Ansible_Installation_Log/`.

---

## ✨ Features

### 🎮 Graphics Card Drivers
- **Automatic Detection**: Detects NVIDIA, AMD, and Intel GPUs natively.
- **Dynamic Purging**: Removes unused kernel graphics modules (`xserver-xorg-video-*`) for hardware that does not exist on your motherboard.
- **Automatic Installation**: Installs appropriate proprietary and open-source drivers securely.

### 📊 Productivity & Office
- **Note-Taking**: Obsidian (markdown-based PKM statically linked to your desktop launcher).
- **Academic Suite**: Zotero, Okular, TeXstudio, Pandoc.
- **Microsoft Office (via WinApps)**: Excel, Outlook, and WhatsApp. 
  - *⚠️ **IMPORTANT**: WinApps requires a fully functioning Windows Virtual Machine running in KVM/QEMU in the background. After the playbook installs the WinApps frontend, you must manually connect it to your VM before running `winapps install excel`.*

### 🔧 System Utilities & Monitoring
- **Monitoring Stack**: Htop (classic), Btop (modern C++ dashboard), Nvtop (dedicated GPU process monitor), Gtop (node.js UI).
- **Shell Environment**: Fish (Friendly Interactive Shell).
- **Hypervisors**: KVM / QEMU (bare-metal) and VirtualBox 7.0 (hosted).

---

## 📁 Project Structure

```text
kubuntu-setup/
├── setup.yml                    # Main playbook (controller)
├── README.md                    # This documentation
├── PackageList.md               # Extensive audit of all packages
└── tasks/                       # Task directory
    ├── check_prerequisites.yml  # Network and package manager verification
    ├── graphics.yml             # GPU detection, installation, and unused purging
    ├── system.yml               # System utilities & monitoring (Htop, Btop, Nvtop)
    ├── programming.yml          # Development tools, IDEs, VS Code & Git
    ├── productivity.yml         # Office, MS Office (WinApps), Obsidian & Zotero
    ├── media.yml                # Media & communication tools (OBS, Discord)
    └── hibernation.yml          # Interactive Swap & Hibernation Configurator
```

---

## 📋 Prerequisites

### System Requirements
- **OS**: Kubuntu 22.04 LTS or later
- **Architecture**: x86_64
- **Internet**: Stable connection required for downloads
- **Sudo**, **Python 3**, and **Ansible** are explicitly required to deploy this architecture.

### Pre-Installation Software

Run the following to prepare a brand new machine entirely for playbook execution:

```bash
sudo apt update && sudo apt upgrade -y 
sudo apt install ansible git -y
```

*(Optional) Configure passwordless sudo for the current user to prevent Ansibe from pausing:*
```bash
sudo visudo
# Add this line at the absolute bottom of the file securely:
# YOUR_USERNAME ALL=(ALL) NOPASSWD: ALL
```

---

## 🚀 Installation & Usage

### 1. Clone the Repository
```bash
git clone https://github.com/L-vd-M/kubuntu-setup.git ~/kubuntu-setup
cd ~/kubuntu-setup
```

### 2. Validate Architecture Check
```bash
ansible-playbook setup.yml --syntax-check
```

### 3. Deploy
Execute the master framework. It will prompt for your sudo password (unless disabled above) and securely escalate permissions dynamically.
```bash
ansible-playbook setup.yml --ask-become-pass
```

### 4. Review Telemetry
Check your explicitly formatted log file dynamically generated in your Documents folder:
```bash
cat ~/Documents/Ansible_Installation_Log/*.log
```

---

## 🗺️ Codebase Working Summary

> **Hardware target used as reference**: MSI Vector GP76 — Intel Core i7-12700H + NVIDIA RTX 3070Ti

---

### Playbook Architecture & Flow

```
setup.yml (controller)
├── PRE-TASKS
│   ├── Resolve user home path (avoids /root escalation)
│   ├── Detect dpkg architecture (amd64 / arm64)
│   └── Initialize timestamped log file, snapshot installed packages
│
├── MAIN TASKS (7 sections, each delegated to tasks/)
│   ├── [1] check_prerequisites.yml  — system readiness checks
│   ├── [2] graphics.yml             — GPU detection & driver setup
│   ├── [3] system.yml               — system utilities & virtualisation
│   ├── [4] programming.yml          — dev tools, Node.js, VS Code
│   ├── [5] media.yml                — Discord, OBS, Spotify
│   ├── [6] productivity.yml         — Obsidian, Zotero, LaTeX, Chrome
│   └── [7] hibernation.yml          — interactive hibernation setup
│
└── POST-TASKS
    ├── Compute package delta (before vs after)
    ├── Write delta to log
    ├── Write completion timestamp
    └── [REBOOT HANDLER] prompt & schedule reboot if GPU/hibernation changed
```

---

### Task File Breakdown

#### `tasks/check_prerequisites.yml`
Validates the system before any installation:  
- Debian/Ubuntu family check  
- Python3, APT, curl, wget, git availability  
- Internet connectivity  
- Fails gracefully with descriptive messages  

#### `tasks/graphics.yml`
Hardware-aware GPU driver installation:
- Detects NVIDIA, AMD, Intel via `lspci` — empty stdout = GPU absent (fixed `|| true` avoids false positives)
- **NVIDIA RTX (Ampere)**: installs `nvidia-driver-550`, `nvidia-utils-550`, `nvidia-settings`, `nvidia-prime`
- **GRUB kernel parameters** (injected idempotently):
  - `nvidia_drm.modeset=1` — enables kernel mode-setting for HDMI/display enumeration
  - `nvidia.NVreg_DynamicPowerManagement=0` — disables GPU power-gating that hides HDMI on wake
  - `nvidia.NVreg_PreserveVideoMemoryAllocations=1` — keeps VRAM allocated (required for hibernation)
- **`/etc/modprobe.d/nvidia-drm.conf`**: `options nvidia-drm modeset=1` — belt-and-suspenders; ensures modeset is honoured even when the initrd loads the module before GRUB params are visible
- **`prime-select nvidia`** (performance mode): MSI Vector GP76's HDMI port is wired to the dGPU; the default `on-demand` PRIME profile power-gates the dGPU and hides the port — switching to `nvidia` activates the dGPU as primary GPU
- **nvidia systemd services** (`nvidia-suspend`, `nvidia-hibernate`, `nvidia-resume`): enabled to guarantee clean suspend/resume cycles with DRM modeset active
- **Xorg config** written to `/etc/X11/xorg.conf.d/20-nvidia.conf` with `AllowEmptyInitialConfiguration` and `PrimaryGPU`
- AMD: `xserver-xorg-video-amdgpu`, `mesa-vulkan-drivers`, `libvulkan1`
- Intel: `intel-gpu-tools`, `intel-media-va-driver`, `mesa-vulkan-drivers`, `va-driver-all`
- Purges drivers for hardware *not* present (reduces kernel module bloat)
- Sets `needs_reboot: true` if NVIDIA hardware detected

#### `tasks/system.yml`
Foundation utilities:
- **Compression**: `zip`, `gzip`, `tar`
- **Editors**: `nano`, `vim`
- **Monitoring**: `htop`, `btop`, `nvtop`, `gtop`
- **Virtualisation**: `virt-manager` (KVM/QEMU), VirtualBox 7.0 (via Oracle repo)

#### `tasks/programming.yml`
Development environment:
- `git`, `curl`, `wget`, `vim`
- **Node.js**: NVM v0.39.7 → Node 22 (user-space install, not global)
- **VS Code**: from Microsoft official APT repository
- **Telecom suite**: `gnuradio`, `wireshark` (with non-root capture via Polkit), `jupyter-notebook`

#### `tasks/media.yml`
- **Discord**: downloaded from Discord API as `.deb`, installed via APT
- **OBS Studio**: from APT
- **Spotify**: official GPG key + `spotify-client` from Spotify repo

#### `tasks/productivity.yml`
Academic productivity stack:
- **Obsidian**: GitHub API → latest AppImage → `/opt` → symlink + `.desktop` entry (architecture-aware)
- **Zotero**: interactive major/minor version selector via GitHub tags API → tarball to `/opt`
- **Google Chrome**: official repository
- **WinApps**: framework install (manual VM configuration required post-install)
- **Academic**: `okular`, `texstudio`, `pandoc`
- **Snaps**: `superproductivity`, `drawio`

#### `tasks/hibernation.yml`
Fully automated hibernation configurator:
1. **Dynamic swap calculation**: detects RAM, computes required swap (RAM + 2GB buffer)
2. **Interactive swap resize**: `dd` + `mkswap` → updates `/etc/fstab`
3. **UUID + offset detection**: `findmnt` (partition UUID) + `filefrag` (physical block offset)
4. **GRUB update**: idempotent `lineinfile` with negative lookahead — won't duplicate `resume=UUID` params
5. **PolicyKit rules** (modern JavaScript only — legacy PKLA format removed):
   - `/etc/polkit-1/rules.d/10-enable-hibernate.rules` — enables KDE/GNOME hibernation UI button
6. **Fish shell alias**: system-wide `hibernate` function in `/etc/fish/functions/hibernate.fish`
7. **Verification tasks**: checks `/etc/initramfs-tools/conf.d/resume` and GRUB params actually present
8. Sets `needs_reboot: true` when configuration is applied

---

### Package Inventory by Category

| Category | Packages |
|---|---|
| **GPU Drivers** | nvidia-driver-550, nvidia-utils-550, nvidia-settings, nvidia-prime, xserver-xorg-video-amdgpu, intel-gpu-tools, intel-media-va-driver, mesa-vulkan-drivers |
| **System Utilities** | zip, gzip, tar, nano, vim, htop, btop, nvtop, gtop |
| **Virtualisation** | virt-manager, qemu-kvm, libvirt-daemon, virtualbox-7.0 |
| **Development** | git, curl, wget, nvm, node v22, vscode |
| **Telecom / Research** | gnuradio, wireshark, jupyter-notebook |
| **Media** | discord, obs-studio, spotify-client |
| **Productivity** | obsidian (AppImage), zotero (tarball), google-chrome-stable |
| **Academic** | okular, texstudio, pandoc |
| **Snaps** | superproductivity, drawio |
| **WinApps** | winapps (manual post-install required) |

---

### Key Implementation Patterns

| Pattern | Where Used |
|---|---|
| `||\ true` on shell tasks | GPU detection — ensures empty stdout (GPU absent) not treated as failure |
| `stdout \| trim \| length > 0` | GPU fact-setting — avoids false positives from fallback echo strings |
| Negative lookahead regexp in `lineinfile` | GRUB kernel params (graphics + hibernation) — idempotent, no duplicates on re-run |
| `force: no` on GRUB backup | Preserves the original pre-playbook GRUB config across multiple runs |
| `backrefs: yes` | Appends to existing GRUB_CMDLINE_LINUX_DEFAULT without replacing the whole line |
| `prime-select nvidia` + idempotent query | Sets dGPU as primary so dGPU-wired HDMI port is visible; skipped if already in nvidia mode |
| `/etc/modprobe.d/nvidia-drm.conf` | Belt-and-suspenders `modeset=1` — survives UEFI initrd orderings that bypass GRUB cmdline |
| `needs_reboot` set_fact | Propagated from graphics.yml / hibernation.yml → consumed by setup.yml post-task |
| `register: grub_nvidia_params` + `when: grub_nvidia_params.changed` | Calls `update-grub` only if GRUB was actually modified |
| GitHub API + version selector | Obsidian (latest release), Zotero (dynamic major/minor prompt) |
| `/etc/apt/keyrings/` for GPG keys | Modernised APT key management (replaces deprecated `apt-key`) |
| `host_user_home` variable | Resolves real user home under sudo to prevent `/root` path traps |
| `dpkg_arch` variable | Architecture-aware binary downloads (amd64 / arm64) |
| Timestamped log file | Full execution audit trail in `~/Documents/Ansible_Installation_Log/` |

---

### Setup & Configuration Requirements

| Requirement | Notes |
|---|---|
| OS | Kubuntu 22.04 LTS or later (Debian family required for `update-grub` / `initramfs-tools`) |
| Architecture | x86_64 (amd64) — arm64 supported for binary downloads |
| Internet | Required for all package installs and GitHub API calls |
| Sudo / Ansible | `sudo apt install ansible git -y` before running |
| Swap file | Must exist at `/swapfile` for hibernation (playbook will resize it if needed) |
| WinApps | Requires manual KVM/QEMU Windows VM setup post-install |
| Reboot | **Required** after first run — NVIDIA drivers + GRUB params only activate after reboot |

---

### Known Issues Fixed (v2.3)

| Issue | Root Cause | Fix Applied |
|---|---|---|
| HDMI disappears after reboot | Driver 535 missing Ampere tuning; no GRUB kernel params; no Xorg config; PRIME defaulting to `on-demand` power-gates the dGPU, hiding the dGPU-wired HDMI port | Upgraded to driver 550 + `nvidia_drm.modeset=1` (GRUB + `/etc/modprobe.d/nvidia-drm.conf`); Xorg device config; `prime-select nvidia` (performance mode); nvidia systemd power services enabled |
| Hibernation not available after reboot | GRUB regex had broken negative lookahead → resume params not actually written | Replaced with correct `((?!.*resume=UUID).*)` pattern + backrefs |
| Hibernation polkit rules not picked up by KDE | Using deprecated PKLA format (`.pkla` files) | Removed PKLA tasks; kept only modern JavaScript rules |
| GPU detection false positives | `|| echo "No NVIDIA GPU detected"` → string "nvidia" matched in fallback text | Changed to `|| true`; fact-setting now uses `stdout \| trim \| length > 0` |
| No reboot prompt after playbook | No post-task reboot handling | Added `needs_reboot` propagation and `shutdown -r +1` prompt in post-tasks |
