# Hibernation Configuration Plan

Your system has massive **32GB RAM**, but currently only a default **512MB swapfile**. For safe and reliable hibernation, the Linux kernel must be able to suspend the exact state of your RAM to the hard drive. This means your swapfile MUST be larger than your total RAM before hibernation can work.

Fortunately, your NVMe SSD has around **1.7TB** of free space, so creating a ~34GB swapfile is completely safe and won't make a dent.

## User Review Required
Before touching your system's bootloader or sleep routines, we have built the logic into a test playbook (`tmp-test/test_hibernation.yml`). It handles everything interactively so you can see exactly what it plans to do!

## Proposed Changes

### tmp-test/test_hibernation.yml
#### [NEW] [test_hibernation.yml](file:///home/lourens/Documents/Device_Setup/PC_Setup/kubuntu-setup/tmp-test/test_hibernation.yml)
We will create an Ansible playbook that performs the following:
1. **Fact Gathering**: Identifies exactly how much memory you have (`~32GB`).
2. **Swap Diagnostics**: Verifies your current swapfile size (`512MB`) and determines it's too small.
3. **Interactive Fixes**: 
    - The playbook pauses and asks: *"Would you like to expand your swapfile to 34GB using dd? [y/N]"*
    - If yes, it safely runs `swapoff`, allocates the 34GB using `dd` (this takes ~15 seconds on NVMe), applies `mkswap`, and `swapon`.
4. **Calculations**: Computes your root partition's **UUID** and the newly grown swapfile's physical block **offset** using `findmnt` and `filefrag`.
5. **Configuration Prompts**:
    - The playbook pauses and asks: *"Apply hibernation params to GRUB & Initramfs? [y/N]"*
    - If yes, it writes the configuration `RESUME=UUID=... resume_offset=...` into `/etc/initramfs-tools/conf.d/resume` and [/etc/default/grub](file:///etc/default/grub).
    - It runs `update-grub` and `update-initramfs -u`.
6. **UI Integration**: Finally, it installs a Polkit rule to seamlessly enable the *Hibernate* button in KDE Plasma's power menu.

## Verification Plan
1. **Action**: Run `ansible-playbook tmp-test/test_hibernation.yml --ask-become-pass`.
2. **Action**: Wait for the prompts and hit `y` to apply each step.
3. **Action**: Reboot your PC so the new GRUB parameters take effect (`sudo reboot`).
4. **Action**: Once booted, open a bunch of apps and run `systemctl hibernate` or use the UI Hibernate button.
5. **Expected Outcome**: The computer turns completely off. Upon powering back on, you bypass a cold boot and instead see KDE exactly how you left it.
