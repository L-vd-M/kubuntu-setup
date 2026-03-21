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
