# Dynamic Version Selection Implementation Plan

## Goal Description
Create test playbooks that allow the user to proactively select which version of Typst, Zotero, and LaTeX to install, rather than hardcoding them. If the user doesn't specify a version or requests `latest`, the playbook should fetch the latest available version. We will test these locally in `tmp-test/` before migrating the logic to the main Ansible setup.

## Proposed Test Playbooks

### `tmp-test/test_typst_dynamic.yml`
- **Method**: Use `vars_prompt` to ask the user for a version (default: `latest`).
- **Logic**: If `latest`, query the `https://api.github.com/repos/typst/typst/releases/latest` endpoint to resolve the version string (e.g. `0.14.0`).
- **Action**: Download the `typst-x86_64-unknown-linux-musl.tar.xz` tarball for the specified version and extract it to `~/.local/bin`.

### `tmp-test/test_zotero_dynamic.yml`
- **Current State**: The main playbook uses the `retorquere/zotero-deb` APT repository to install Zotero. APT repositories don't easily allow arbitrary historical version selection.
- **Method**: To support robust version selection, we will test downloading the official Zotero tarball direct from their API.
- **Logic**: Use `vars_prompt`. If `latest`, the official URL `https://www.zotero.org/download/client/dl?channel=release&platform=linux-x86_64` cleanly auto-redirects. If a specific version is requested, we can suffix `&version=X.Y.Z` (e.g., `7.0.0`).
- **Action**: Extract the tarball to an isolated folder like `~/.local/zotero` and symlink the executable to `~/.local/bin/zotero`.

### `tmp-test/test_latex_dynamic.yml`
> [!WARNING]
> LaTeX/TeX Live is massive (often 4-7 GB) and versioning is uniquely complicated.
- **Complexity**: By standard, Ubuntu's APT repository locks LaTeX to a specific "Year" (like TeX Live 2023). To arbitrarily select LaTeX versions (like switching between TeX Live 2022, 2023, 2024), we must completely bypass `apt` and use the historic official `install-tl` net installers, which takes 30-60+ minutes to run.
- **Alternative (TinyTeX)**: Another approach is using `TinyTeX`, a lightweight, cross-platform, and easily maintainable LaTeX distribution where versions can be somewhat managed, though typically you just grab the newest release.
- **Method**: Let's test using `TinyTeX` combined with dynamic versioning via GitHub releases (or `install-tl` if you prefer the massive standard TeX Live).

## Verification Plan
1. We will manually execute `ansible-playbook tmp-test/test_typst_dynamic.yml` and provide input like `0.12.0` to verify it honors the explicit version, then run it again with `latest` to verify dynamic fetching.
2. We will run `ansible-playbook tmp-test/test_zotero_dynamic.yml` testing specific older versions.
3. We will do the same for the LaTeX test after resolving the approach above.
