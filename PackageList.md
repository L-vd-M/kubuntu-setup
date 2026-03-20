# Kubuntu Setup Core Package Audit

This document serves as an explicit audit trail of core system utilities and dependencies, defining exactly why specific foundation packages were either heavily integrated into the Ansible Playbook or intentionally omitted.

## 🟢 Included Packages

| Package Name | Purpose / Function | Reason for Inclusion | Location in Playbook |
| :--- | :--- | :--- | :--- |
| `zip`/`unzip`| Archives files into cross-platform standard ZIP format. | Essential utility for extracting downloaded assets (e.g., driver bundles or GitHub releases). | `tasks/system.yml` (Base Utilities) |
| `gzip` | Core Linux decompression tool for `.gz` compressed files. | Natively integrates with `tar` to extract standard Linux source code securely. | `tasks/system.yml` (Base Utilities) |
| `tar` | Tape Archive program used to bundle multiple files together. | Standard method for handling pre-compiled binaries deployed by third parties on Linux. | `tasks/system.yml` (Base Utilities) |
| `nano` | Intuitive, beginner-friendly terminal text editor. | Needed for quick config file edits via CLI without steep learning curves. | `tasks/system.yml` (Text Editors) |
| `vim` | Advanced, highly efficient terminal text editor. | Industry standard software engineering necessity for rapid Git commit parsing and bulk edits. | `tasks/programming.yml` (Dev Tools) |
| `htop` | Interactive ncurses-based system process viewer. | Visually monitors RAM, CPU core usage, and orchestrates process termination during development. | `tasks/system.yml` (Monitoring) |
| `curl` | Command-line tool for transferring data over URLs. | Critical for downloading remote execution scripts (e.g., NVM installations, Zotero setups). | `tasks/programming.yml` |
| `wget` | Robust network downloader supporting resume logic. | Excellent for pulling large datasets or `.deb` packages directly over HTTP/HTTPS. | `tasks/programming.yml` |
| `git` | Distributed version control system. | Absolute necessity for syncing the playbook, downloading scripts, and code management. | `tasks/programming.yml` |

---

## 🔴 Omitted Packages

| Package Name | Purpose / Function | Reason for Omission | Modern Alternative Used |
| :--- | :--- | :--- | :--- |
| `gnupg` | Used to encrypt data and conditionally dearmor `.gpg` signatures. | Ansible's secure `get_url` module now natively handles securely fetching and parking `.asc` and `.gpg` keys into `/etc/apt/keyrings/`, entirely bypassing the need to use `gnupg` interactively. | `get_url` |
| `ca-certificates` | Allows SSL-based applications to securely verify TLS connections against a root certificate authority. | Already comes pre-installed by default on 100% of Kubuntu desktop base images. Specifically declaring its installation simply creates redundant database locks. | Shipped with OS |
| `apt-transport-https` | Originally allowed legacy Debian APT to safely traverse HTTPS internet protocols instead of unencrypted HTTP. | Legacy package. As of Ubuntu 16.04+ (and active Kubuntu 24.04 setups), HTTPS transit transport logic is permanently hard-coded into the core `apt` binary. | Integrated in OS `apt` |
| `software-properties-common` | Provided a bulky python interface to heavily manage PPA repositories using the `add-apt-repository` command. | We modernized all external APT tracking to use secure direct `/etc/apt/keyrings` bound mappings. Using loose PPAs is generally insecure and less deterministic for Ansible. | Direct `sources.list` Mapping |
