# Kubuntu Ansible Setup Playbook Walkthrough

This document serves as a comprehensive guide to understanding the architecture of the **Kubuntu Setup Playbook**. It breaks down the role of the master orchestrator (`setup.yml`) and explains the specific purpose of each delegated task file.

---

## The Master Orchestrator: `setup.yml`

The `setup.yml` file is the central nervous system of your entire Ansible deployment. Rather than containing hundreds of chaotic installation commands, it is highly modularized. Its main responsibilities include:

1. **System Discovery**: It gathers critical hardware and OS facts natively (such as determining the amount of RAM, the number of CPU cores, and whether it is running on Kubuntu Noble or Jammy).
2. **Architecture Mapping**: It dynamically queries the system's `dpkg` architecture (mapping `x86_64` to `amd64` or `aarch64` to `arm64`) to ensure third-party repositories always download the exact correct binaries.
3. **Structured Logging**: It initializes a permanent, timestamped log file inside `~/Documents/Ansible_Installation_Log/` to track every success or failure.
4. **Delegation**: It sequentially executes 7 dedicated modular task files to install software logically by category.
5. **Post-execution**: After all setups are complete, it dumps the full manifest of installed APT packages into the log file for precise auditing.

---

## Module Breakdown: The `tasks/` Directory

### 1. `check_prerequisites.yml`
**Purpose**: Acts as the gatekeeper. It runs safety checks before anything is modified on your computer to ensure the environment is ready structurally.
- Checks if the user has `sudo` privileges.
- Ensures the system is successfully connected to the internet.
- Verifies APT package manager accessibility.
- Checks if core underlying tools (like `pciutils` for GPU scanning) exist, preventing downstream tasks from crashing if the system is completely bare-bones.

### 2. `graphics.yml`
**Purpose**: Handles hardware-accelerated drivers safely. 
- It uses the `lspci` command dynamically to search for evidence of NVIDIA, AMD (`amdgpu`), or Intel physical graphics cards.
- If it detects a dedicated GPU, it uses interactive Debconf menus to ask the user if they wish to install proprietary or open-source drivers, and safely injects them into the kernel.

### 3. `system.yml`
**Purpose**: Installs the foundational OS layer tools and handles the heavy Virtualization suites.
- Installs basic extraction tools (`zip`, `unzip`, `rar`, `p7zip`).
- Injects Linux monitoring tools (`htop`, `neofetch`, `gtop`).
- Installs the **Fish shell**, seamlessly making it the user's default login environment for a modern, interactive terminal, naturally injected via the official PPA.
- Maps out your **Type 1 Hypervisor** via the Linux core: `virt-manager` (QEMU/KVM).
- Downloads the external Oracle APT Keyrings to install the **Type 2 Hypervisor**: `virtualbox-7.0`.

### 4. `programming.yml`
**Purpose**: Deploys your primary development logic layer and establishes the Master's Telecommunications Engineering suite.
- Replaces the unsafe global NodeSource installation with **NVM (Node Version Manager)**, putting the active LTS Node.js 22.x build safely into user space `~/.nvm`.
- Installs `curl`, `wget`, `vim`, and `git`.
- Connects directly to Microsoft's GPG keys to deploy **Visual Studio Code**.
- Builds the **Telecom Suite**: Installs the powerful `jupyter-notebook` data environment, `gnuradio` for SDR simulations, and `wireshark` for deep packet analysis (dynamically securing non-root packet capture permissions).

### 5. `media.yml`
**Purpose**: Focuses on video processing and audio streaming tools.
- Retrieves the specialized Spotify APT Signature (`pubkey_5384CE82BA52C83A.gpg`) for seamless ad-free streaming configurations.
- Downloads Discord natively over HTTP.
- Sets up generic media processing utilities like `vlc`, `ffmpeg` (vital for codec encoding in video projects), and `obs-studio`.

### 6. `productivity.yml`
**Purpose**: Builds your academic reading, writing, and diagramming command center.
- Safely binds and sets up Google Chrome via `/etc/apt/keyrings`.
- Installs **Zotero** entirely dynamically. It leverages the GitHub API to poll available repository tags, parses the metadata cleanly, and pauses the execution with an interactive double-menu prompt so the user can natively select the exact major and minor version to install into the `/opt` environment.
- Resolves **Obsidian's** dynamic versioning by fetching the JSON metadata of releases via the GitHub API to always install the latest AppImage natively. 
- Adds the core **Academic Suite**: `okular` (advanced PDF annotation), `texstudio` (LaTeX compilation), and `pandoc` (Markdown parser).
- Snaps in diagrams and Pomodoro timers via `drawio` and `superproductivity`.
- Automatically prepares the dependencies required to handle **WinApps** (for Microsoft Outlook/Excel integration on Linux).

### 7. `hibernation.yml`
**Purpose**: Systematically handles the fragile transition of RAM-to-Drive suspending capabilities.
- Safely calculates exact system RAM availability mapping and leverages `dd` to natively dynamically expand standard Ubuntu/Kubuntu swapfiles up to the exact required safe metrics per host.
- Computes underlying filesystem block offsets via physical `filefrag` routing and root disk unique UUID tracking.
- Safely re-initializes and binds both `/etc/default/grub` bootloader flags and the raw `initramfs` system resumption environment without manual user math.
- Injects native Javascript Polkit authorizations, explicitly unmasking the native 'Hibernate' integration securely into the KDE Plasma / GNOME graphic user interfaces, and automatically binds a direct fast-lane `hibernate` CLI abbreviation alias cleanly into the active Fish shell configuration.
