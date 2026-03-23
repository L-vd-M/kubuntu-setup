# AI Agent Instructions for Kubuntu-Setup

## Project Core Philosophy
You are operating within the `kubuntu-setup` repository. This playbook is strictly designed, tested, and maintained specifically for **Debian/Ubuntu-based distributions** (e.g., Kubuntu, Ubuntu, Pop!_OS, Linux Mint).

## Ironclad Constraints
1. **Never Break Stable Functionality**: This repository is considered production-ready for Ubuntu/Debian-based systems. Do not introduce sweeping architectural shifts that threaten the current stable execution flow.
2. **Debian Exclusivity**:
   - You MUST use the `apt` and `apt_repository` Ansible modules directly.
   - You MUST rely on Debian-specific OS commands when writing shell/command tasks (e.g., `update-initramfs`, `update-grub`).
   - Do not attempt to add support for `dnf`, `pacman`, `dracut`, or Arch/RedHat paradigms here.
3. **No Cross-Distro Abstractions**: Keep task syntax clean, rapid, and direct. Do not abstract packages into complex OS-mapping variable dictionaries. Hardcode the exact `apt` dependency names directly (e.g., `build-essential`, `python3-pyqt5`).
4. **Safety & Modularity**: Strictly maintain `block/rescue` structures and `lineinfile` logging functionality in all task files.
5. **Display Server Awareness**: This system uses a **split display server architecture**:
   - **SDDM login screen**: forced to **X11** (`DisplayServer=x11`) so the `Xsetup` reverse PRIME script runs correctly at the login screen.
   - **Desktop session**: **Wayland** (KDE Plasma 6 default on Ubuntu 24.04+), managed by KWin Wayland.
   - **Xwayland** is active — a full Xorg config exists at `/etc/X11/xorg.conf.d/20-nvidia.conf`, so X11 tools (e.g. `wmctrl`) work inside the Wayland session via the Xwayland bridge.
   - When writing tasks that interact with the graphical session (e.g. window listing, display detection), prefer tools that work via Xwayland (`wmctrl`, `xdotool`) or provide a Wayland-native fallback (`qdbus` to KWin). Do NOT assume a pure X11 or pure Wayland environment.

Your singular goal is to securely maintain and surgically enhance this playbook safely within the Kubuntu ecosystem context.
