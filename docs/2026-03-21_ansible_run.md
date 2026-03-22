# Ansible Playbook Execution Log - March 21, 2026

## 🟢 What Worked (Successes)
- ✅ **System & Prerequisite Initialization**: Python, apt, network, and `sudo` checks succeeded successfully.
- ✅ **Graphics Deployment**: Detection worked perfectly. The NVIDIA Driver (535) and Intel packages were installed, and `initramfs` was correctly updated.
- ✅ **Basic Tools & CLI Utilities**: Node.js v22 (via NVM), `curl`, `wget`, `zip`, `tar`, `nano`, and `htop` installed seamlessly.
- ✅ **KVM / Virtualization**: `virt-manager` installed and the `libvirtd` systemd service was successfully enabled.
- ✅ **Media**: Discord, VLC, and FFmpeg installed correctly.
- ✅ **Academic Tools**: Okular, TeXstudio, and Pandoc correctly negotiated APT locks.

## 🔴 What Failed (Errors)
Almost every failure below shares a single root cause: **Ansible attempted to run system-level tasks without root privilege (`become: yes`)**. Even though `--ask-become-pass` was supplied at runtime, Ansible will not escalate privileges unless the specific task (or the master `setup.yml` playbook) explicitly declares `become: true`.

1. **APT Frontend Locks (Permission Denied)**:
   - `VirtualBox`, `build-essential`, and `Antigravity` PIP dependencies all failed because they could not acquire the `/var/lib/dpkg/lock-frontend` root lock.
2. **GPG Key & Repo Injections (Permission Denied)**:
   - Writing to `/etc/apt/keyrings/` failed for **Spotify** and **Google Chrome** because `/etc` is owned by root.
   - Writing to `/etc/apt/sources.list.d/` for **VS Code** failed for the same reason.
3. **Directory Constraints (`/opt/`)**:
   - Creating the `WinApps` clone and the `Obsidian` AppImage extraction inside `/opt/` failed with `Permission denied`.
4. **Snap Packages**:
   - `drawio` and `superproductivity` explicitly failed with: `error: access denied (try with sudo)`.
5. **CRITICAL YAML Syntax Collapse in `hibernation.yml`**:
   - `ERROR! conflicting action statements: hosts, gather_facts`
   - **Reason**: When the old `enable_hibernation.yml` testing playbook was copied into `tasks/hibernation.yml`, its playbook header (`hosts: localhost`, `tasks:`) was not stripped out. Since it is being `included` natively by the master `setup.yml`, flat task files cannot contain top-level playbook declarations.

## 🔧 Recommended Fixes for Next Run
1. Inject `become: yes` globally at the top of the `setup.yml` playbook (or on every `apt`, `snap`, `get_url`, and `shell` task individually) to utilize the provided SUDO password everywhere.
2. Strip the standard playbook headers from `tasks/hibernation.yml` so it is just a flat list of tasks.
