# Playbook Modernization & Quality-of-Life Fixes

## Goal Description
Enhance the reliability, security, and cleanliness of the Ansible playbook by addressing three user-reported issues: undefined variable crashes on skipped tasks, duplicate `build-essential` aptitude locks, and deprecation warnings caused by the legacy `apt_key` module.

The user explicitly requested testing everything in isolation first, then applying the fixes broadly.

## Proposed Changes

### 1. Fix "Undefined Variable" Errors Globally
- **Problem**: Variables registered in conditional `block`/`get_url`/`apt` tasks (like `vscode_install.changed` or `zotero_install.changed`) crash later tasks if the installation was skipped (making the variable technically undefined).
- **Fix**: Identify all `.changed` variables in `when:` statements and line-item message logs, and append the `| default(false)` Jinja filter. 
  - Affected files: [tasks/system.yml](file:///home/lourens/Documents/Device_Setup/PC_Setup/kubuntu-setup/tasks/system.yml), [tasks/programming.yml](file:///home/lourens/Documents/Device_Setup/PC_Setup/kubuntu-setup/tasks/programming.yml), [tasks/productivity.yml](file:///home/lourens/Documents/Device_Setup/PC_Setup/kubuntu-setup/tasks/productivity.yml), [tasks/media.yml](file:///home/lourens/Documents/Device_Setup/PC_Setup/kubuntu-setup/tasks/media.yml).

### 2. Consolidate `build-essential` 
#### [MODIFY] [tasks/check_prerequisites.yml](file:///home/lourens/Documents/Device_Setup/PC_Setup/kubuntu-setup/tasks/check_prerequisites.yml)
- **Problem**: `build-essential` is targeted for installation twice, locking the APT database multiple times unnecessarily. It is already consolidated elegantly in [tasks/system.yml](file:///home/lourens/Documents/Device_Setup/PC_Setup/kubuntu-setup/tasks/system.yml)'s "Base Utilities" bulk array.
- **Fix**: Remove the raw installation of `build-essential` from [tasks/check_prerequisites.yml](file:///home/lourens/Documents/Device_Setup/PC_Setup/kubuntu-setup/tasks/check_prerequisites.yml). Keep only the base check if desired, but rely completely on [system.yml](file:///home/lourens/Documents/Device_Setup/PC_Setup/kubuntu-setup/tasks/system.yml) for actual installation.

### 3. Modernize `apt_key` (Global Switch to `get_url` Keyrings)
Replace all instances of `apt_key` with the modern `get_url` to `/etc/apt/keyrings`, and securely bind the Keyring to the `apt_repository: repo: "deb [arch=... signed-by=...]"`.

#### [MODIFY] [tasks/system.yml](file:///home/lourens/Documents/Device_Setup/PC_Setup/kubuntu-setup/tasks/system.yml)
- **VirtualBox 7.0**: 
  - Key URL: `https://www.virtualbox.org/download/oracle_vbox_2016.asc`
  - Filename: `/etc/apt/keyrings/oracle_vbox_2016.asc`

#### [MODIFY] [tasks/productivity.yml](file:///home/lourens/Documents/Device_Setup/PC_Setup/kubuntu-setup/tasks/productivity.yml)
- **Google Chrome**: 
  - Key URL: `https://dl-ssl.google.com/linux/linux_signing_key.pub`
  - Filename: `/etc/apt/keyrings/google-chrome.asc`

#### [MODIFY] [tasks/media.yml](file:///home/lourens/Documents/Device_Setup/PC_Setup/kubuntu-setup/tasks/media.yml)
- **Spotify**:
  - Key URL: Update to `https://download.spotify.com/debian/pubkey_5384CE82BA52C83A.gpg` to formally fix the active `NO_PUBKEY 5384CE82BA52C83A` error on the user's system.
  - Filename: `/etc/apt/keyrings/spotify.gpg`

#### [MODIFY] [tasks/programming.yml](file:///home/lourens/Documents/Device_Setup/PC_Setup/kubuntu-setup/tasks/programming.yml)
- **Visual Studio Code**:
  - Implement the successful `get_url` test we already completed.

## Verification Plan
1. Create and execute `tmp-test/test_aptkey_modernization.yml` to download and verify the 3 remaining GPG keys securely directly from the original host.
2. Execute an `ansible-playbook --syntax-check` globally.
3. Apply the changes across the `tasks/` directory files and ensure variables have defaults.
