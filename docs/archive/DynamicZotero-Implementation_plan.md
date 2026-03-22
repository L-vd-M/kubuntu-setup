# Zotero Double-Menu Version Selection

This plan covers implementing the requested "double menu style" prompt for downloading specific versions of Zotero (major version, then minor version).

## User Review Required
- **Interactive Prompts**: Installing Zotero will now pause the Ansible playbook execution to ask for user input. If you run the playbook automated/headlessly, we'll need a way to bypass this (e.g. by defaulting to the latest version if a variable is set). I've added defaults so if you just press `Enter`, it installs the latest major and minor versions automatically.
- **Tarball vs APT**: Currently, [tasks/productivity.yml](file:///home/lourens/Documents/Device_Setup/PC_Setup/kubuntu-setup/tasks/productivity.yml) installs Zotero via a custom APT repository (`zotero-deb`). The APT method only tracks the latest release. By allowing you to pick older versions (e.g., 6.x), we must switch away from APT to the "Tarball" manual download method (which is how [tmp-test/test_zotero_dynamic.yml](file:///home/lourens/Documents/Device_Setup/PC_Setup/kubuntu-setup/tmp-test/test_zotero_dynamic.yml) currently works, and how your Obsidian tasks work).

## Proposed Changes

### test_zotero_dynamic.yml
#### [MODIFY] [test_zotero_dynamic.yml](file:///home/lourens/Documents/Device_Setup/PC_Setup/kubuntu-setup/tmp-test/test_zotero_dynamic.yml)
We will first update this test playbook to implement the double menu:
1. Fetch release tags from the official `zotero/zotero` GitHub API.
2. Parse the tags to extract all available **unique major versions** (e.g., `8`, `7`, `6`).
3. Pause to prompt the user for the **major version**.
4. Filter the tags to show only minor versions belonging to the chosen major version.
5. Pause to prompt the user for the **minor version** (e.g., `8.0.4`).
6. Download the matched Linux tarball from Zotero's official download servers.

### tasks/productivity.yml
#### [MODIFY] [productivity.yml](file:///home/lourens/Documents/Device_Setup/PC_Setup/kubuntu-setup/tasks/productivity.yml)
Once the test script is successful, we will replace the existing Zotero APT installation block with the new dynamic interactive tarball downloader logic.

---

## Verification Plan

### Automated Tests
*Ansible doesn't have traditional CI tests structured here, but we can verify the syntax and execution.*
- **Action**: Run `ansible-playbook tmp-test/test_zotero_dynamic.yml` locally.
- **Expected**: The playbook pauses twice, properly listing major versions and then minor versions based on input. Finally, it installs the requested version into `~/.local/opt` and links it in `~/.local/bin`.

### Manual Verification
- The user will run the updated playbook: `ansible-playbook test_zotero_dynamic.yml`
- Choose major version `7` or `6`.
- Choose a specific minor version `7.0.x`.
- Ensure it successfully installs that exact version without crashing or installing `8.x`.
