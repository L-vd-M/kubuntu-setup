# 🖥️ Kubuntu Setup Playbook with Prerequisite Checks & Logging

> A comprehensive, modular Ansible playbook for automated setup and software installation on Kubuntu systems with intelligent graphics driver detection, prerequisite verification, and detailed logging.

**Version**: 2.2  
**Last Updated**: March 2026  
**Compatible With**: Kubuntu 22.04 LTS and later  
**Maintained By**: Lourens van der Merwe  

---

## 📖 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Project Structure](#project-structure)
- [Usage](#usage)
- [File Creation Guide](#file-creation-guide)
- [Software Categories](#software-categories)
- [Graphics Card Drivers](#graphics-card-drivers)
- [Configuration](#configuration)
- [Adding New Software](#adding-new-software)
- [Where & How to Add Software](#where--how-to-add-software)
- [Logging & Troubleshooting](#logging--troubleshooting)
- [Post-Installation](#post-installation)
- [Maintenance](#maintenance)
- [Advanced Usage](#advanced-usage)
- [FAQ](#faq)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 Overview

This Ansible playbook automates the complete setup of a Kubuntu system by installing and configuring a curated selection of modern, productive software. Instead of manually installing each application, simply run the playbook and let it handle everything.

**NEW IN v2.2**: 
- ✅ Zotero now installs via APT repository (`zotero-deb`) for automatic updates
- ✅ Comprehensive prerequisite checking before installation
- ✅ Detailed logging to `~/Documents/Ansible_Installation_Log/`
- ✅ Intelligent graphics card detection and automatic driver installation
- ✅ Error tracking and recovery

The playbook is organized into **modular task files** by category, making it easy to:
- ✅ Verify system prerequisites before starting
- ✅ Track installation progress with detailed logs
- ✅ Automatically detect and install graphics drivers
- ✅ Install only what you need
- ✅ Add new software easily
- ✅ Understand what gets installed where
- ✅ Recover from installation errors

---

## ✨ Features

### ✅ Prerequisite Verification (NEW!)
- **System Check**: Verifies Kubuntu/Debian-based system
- **Dependency Check**: Ensures all required tools are installed
- **Internet Check**: Verifies internet connectivity
- **Permission Check**: Validates sudo privileges
- **Detailed Logging**: All checks logged for review

### 🎮 Graphics Card Drivers
- **Automatic Detection**: Detects NVIDIA, AMD, and Intel GPUs
- **User Confirmation**: Shows detected cards for verification
- **Automatic Installation**: Installs appropriate drivers based on hardware
- **Support for Multiple GPUs**: Handles systems with multiple graphics cards
- **Kernel Module Management**: Properly configures kernel modules

### 📊 Detailed Installation Logging (NEW!)
- **Log Location**: `~/Documents/Ansible_Installation_Log/`
- **Timestamped Logs**: Each run gets a unique timestamped log file
- **Installation Tracking**: Every task logged with status
- **Error Tracking**: Failed tasks clearly marked
- **Summary Reports**: Installation summary at completion

### 🔧 System Utilities
- **Compression Tools**: ZIP, GZIP, TAR
- **Monitoring**: Htop (interactive process viewer), Gtop (GPU monitoring)
- **Text Editors**: Nano (simple), Vim (advanced)
- **Virtualization**: Oracle VirtualBox 7.0, Virt-Manager (KVM/QEMU), QEMU, Libvirt

### 👨‍💻 Programming & Development
- **Version Control**: Git
- **Runtime**: Node.js 22.x (managed via NVM)
- **Code Editor**: Visual Studio Code
- **Application Launcher**: Antigravity
- **Telecom Engineering Suite**: GNU Radio (SDR / Signal Processing), Wireshark (Packet Analysis), Jupyter Notebooks (Data Modeling)
- **Development Utilities**: curl, wget, vim

### 📊 Productivity & Office
- **Note-Taking**: Obsidian (markdown-based PKM)
- **Citation Manager**: Zotero (via APT repo — auto-updating)
- **Academic Suite**: Okular (Advanced PDF Reading & Annotation), TeXstudio (LaTeX Editor), Pandoc (Markdown to PDF/Word converter)
- **Diagramming & Planning**: Draw.io (Network Architectures), Super Productivity (Task Manager & Pomodoro Tracker)
- **Browser**: Google Chrome
- **Microsoft Office**: Excel, Outlook (via WinApps)

### 🎮 Media & Communication
- **Chat**: Discord
- **Music**: Spotify
- **Streaming**: OBS Studio (Open Broadcaster Software)
- **Messaging**: WhatsApp (via WinApps)
- **Media Utilities**: VLC, FFmpeg

---

## 📋 Prerequisites

### System Requirements
- **OS**: Kubuntu 22.04 LTS or later
- **Architecture**: x86_64 (64-bit)
- **RAM**: 2GB minimum (4GB+ recommended)
- **Disk Space**: 10GB+ available
- **Internet**: Stable connection required for downloads
- **Graphics Card**: Any NVIDIA, AMD, or Intel GPU (optional, but drivers will be installed)
- **Sudo Privileges**: Required for package installation

### Pre-Installation Software

#### 1. Install Ansible

```bash
sudo apt update
sudo apt install ansible

or

sudo apt update && sudo apt upgrade -y && sudo apt install ansible && sudo apt install git && sudo visudo 

{
Add this line at the end:
YOUR_USERNAME ALL=(ALL) NOPASSWD: ALL
Save and exit (Ctrl+X, then Y, then Enter).
}

## Installation
### Method 1: Clone from GitHub (Recommended)
#### Clone the repository
git clone <your-repo-url> ~/kubuntu-setup
cd ~/kubuntu-setup

#### Verify file structure
ls -la
tree  # Install 'tree' command if not available: sudo apt install tree

### Method 2: Manual Setup
#### Create directory structure
mkdir -p ~/kubuntu-setup/tasks
cd ~/kubuntu-setup

#### Create all necessary files (see File Creation Guide below)
kubuntu-setup/
│
├── setup.yml                    # Main playbook (controller)
├── README.md                    # This documentation
├── .gitignore                   # Git ignore file (optional)
│
└── tasks/                       # Task directory
    ├── check_prerequisites.yml  # Prerequisite verification (NEW!)
    ├── graphics.yml             # Graphics card detection & driver install
    ├── system.yml               # System utilities & virtualization
    ├── programming.yml          # Development tools, IDEs & launchers
    ├── productivity.yml         # Office & productivity apps
    └── media.yml                # Media & communication tools

## Verify Installation
#### Check that all files exist
ls -la
ls -la tasks/

#### Validate playbook syntax
ansible-playbook setup.yml --syntax-check


## Run Installation
ansible-playbook setup.yml --ask-become-pass

