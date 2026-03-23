# Session Progress — 22 March 2026

> **Recovery file**: If hibernation fails and this session is lost, read this to resume exactly where we left off.

---

## What We Were Working On

Adding a **session restore after failed hibernation** feature to `tasks/hibernation.yml`.

The feature covers the failure case: if power is lost while the system is hibernated, the next cold boot restores the apps that were open at hibernate time.

---

## Current System State

| Item | Status | Detail |
|------|--------|--------|
| Swap | ✅ Ready | `/swapfile` 34 GB (system has 32 GB RAM — adequate) |
| Initramfs resume | ✅ Set | `RESUME=UUID=2eaaa259-9a45-4f56-a04e-da0767f56f54` |
| GRUB resume params | ✅ Active | `resume=UUID=2eaaa259... resume_offset=428197888` — no `NVreg_PreserveVideoMemoryAllocations` |
| NVreg_PreserveVideoMemoryAllocations | ✅ Fixed to 0 | Was 1 in GRUB; caused `pci_pm_freeze -5` on resume. Now `0` in `/etc/modprobe.d/nvidia-power-management.conf` and removed from GRUB |
| Pre-hibernate hook user detection | ✅ Fixed | Was `grep -v '(:0)'` which exits 1 under `set -e`. Now uses `loginctl`-based detection |
| Session restore scripts | ✅ Deployed & tested | All 8 phases pass — log at `/tmp/test_hibernation_restore.log` |
| initramfs | ✅ Rebuilt | `update-initramfs -u` ran during Phase 2a — **reboot required** to activate |

### Test Playbook Log (last full run — after both fixes applied)
```
[1/8]  Swap: 34815 MB swap / 31795 MB RAM / required 33843 MB — OK
[1/8]  Kernel hibernate support — OK (/sys/power/state contains 'disk')
[2a/8] NVIDIA PreserveVideoMemory fix: already clean
[2b/8] GRUB params: resume=UUID=2eaaa259-9a45-4f56-a04e-da0767f56f54 | resume_offset=428197888
[3/8]  Initramfs RESUME=UUID=2eaaa259-9a45-4f56-a04e-da0767f56f54 — OK
[5/8]  Live save: code, konsole, plasmashell
[6/8]  Hook wiring: pre sets flag, post clears flag — OK
[7/8]  Restore test: cold-boot path fired and cleaned up state files — OK
[8/8]  PASS
```
Result: `failed=0, rescued=0, skipped=3`

---

## First Hibernate Attempt — Post-Mortem

### What happened
User ran `hibernate` (after rebooting into new GRUB params). System powered off. On resume, instead of restoring, the system did a **cold boot**. Apps did NOT restore.

Two separate bugs were found (both required fixes):

---

### Bug 1: NVIDIA `pci_pm_freeze` returns -5 on resume

**Journal evidence (boot 0 — resume boot):**
```
NVRM: GPU 0000:01:00.0: PreserveVideoMemoryAllocations module parameter is set.
       System Power Management attempted without driver procfs suspend interface.
nvidia 0000:01:00.0: PM: pci_pm_freeze(): nv_pmops_freeze [nvidia] returns -5
PM: hibernation: resume failed (-5)
```

**Root cause:**
`NVreg_PreserveVideoMemoryAllocations=1` requires the driver to be frozen via `/proc/driver/nvidia/suspend` (procfs). During hibernate **resume**, the kernel calls `pci_pm_freeze` in early kernel stage before systemd userspace starts. `nvidia-hibernate.service` (which writes to procfs) runs `Before=systemd-hibernate.service`, but the kernel restores the image INSIDE that service, so the procfs write would need to happen inside initramfs, not userspace. Driver rejects the standard PCI PM path. System falls back to cold boot.

**Fix applied:**
- Removed `nvidia.NVreg_PreserveVideoMemoryAllocations=1` from GRUB cmdline
- Created `/etc/modprobe.d/nvidia-power-management.conf` with `options nvidia NVreg_PreserveVideoMemoryAllocations=0`
- Ran `update-grub` + `update-initramfs -u` (Phase 2a in test playbook)

**Note for future:** A proper `=1` setup would require an initramfs script that writes "hibernate" to `/proc/driver/nvidia/suspend` before the kernel's freeze phase. That's complex and out of scope for now.

---

### Bug 2: Pre-hibernate hook exited with code 1 — no flag written

**Journal evidence (boot -1 — hibernate boot):**
```
(sd-exec-strv)[5216]: /usr/lib/systemd/system-sleep/hibernate-restore-hook failed with exit status 1.
```

**Root cause:**
The save script had `set -euo pipefail` and this line at the top:
```bash
REAL_USER=$(who | grep -v "(:0)" | awk 'NR==1{print $1}')
```
The user session shows `(:0)` in `who` output (SDDM on X11 display `:0`). `grep -v "(:0)"` found no matching lines — exited with code 1. `pipefail` propagates grep's exit 1 as the pipeline result. Script aborted at line 1. No `apps.txt`, no `pending-restore` flag written.

Consequence: when the cold boot happened (due to Bug 1), the restore script found no flag and exited as a no-op. Apps not restored.

**Fix applied:**
Replaced `grep -v "(:0)"` with `loginctl list-sessions --no-legend | awk '{print $3}' | sort -u | head -1 || true`. Added `xdpyinfo` display probe loop (`:0`, `:1`, `:2`) to detect the active X display.

---

### Post-fix system state

```
/etc/default/grub:
GRUB_CMDLINE_LINUX_DEFAULT='quiet splash resume=UUID=2eaaa259-9a45-4f56-a04e-da0767f56f54 resume_offset=428197888'

/etc/modprobe.d/nvidia-power-management.conf:
options nvidia NVreg_PreserveVideoMemoryAllocations=0
```

---

## Files Created / Modified This Session

### New files committed to repo
| File | Purpose |
|------|---------|
| `CLAUDE.md` | AI agent instructions for this repo |
| `.github/agents/kubuntu-setup.agent.md` | Custom VS Code agent for this playbook |
| `docs/archive/tmp-test/test_hibernation_restore.yml` | Integration test for hibernate session restore |
| `docs/session_progress_20260322.md` | This file |

### Files modified
| File | Change |
|------|--------|
| `README.md` | Added display server architecture section + requirements row |
| `CLAUDE.md` | Added constraint #5 — Display Server Awareness |
| `.github/agents/kubuntu-setup.agent.md` | Added Display Server Architecture section |

### System files deployed (by test playbook)
| File | Purpose |
|------|---------|
| `/usr/local/bin/hibernate-save-session.sh` | Runs pre-hibernate; saves open app names + `pending-restore` flag |
| `/usr/local/bin/hibernate-restore-session.sh` | Runs at login; only fires if `pending-restore` flag exists |
| `/lib/systemd/system-sleep/hibernate-restore-hook` | systemd hook: `pre` → save, `post` → clear flag |
| `/etc/xdg/autostart/hibernate-restore-session.desktop` | Triggers restore script at every login |
| `/etc/default/grub.hibernate-test.bak` | Backup of original GRUB (before our changes) |
| `/etc/modprobe.d/nvidia-power-management.conf` | **NEW** — sets `NVreg_PreserveVideoMemoryAllocations=0` |

---

## Display Server Architecture (verified from code)

This system runs a **split display server**:
- **SDDM login screen** → X11 (`DisplayServer=x11` forced in `/etc/sddm.conf.d/10-nvidia-prime.conf`)
- **Desktop session** → Wayland (KDE Plasma 6) with KWin Wayland + `KWIN_DRM_DEVICES`
- **Xwayland is active** → `/etc/X11/xorg.conf.d/20-nvidia.conf` exists; `wmctrl` works from Wayland session

---

## What Still Needs To Be Done

1. **Reboot** → activates new initramfs with `NVreg_PreserveVideoMemoryAllocations=0` (**required** before retesting hibernate)
2. **Run `hibernate`** → verifies successful resume (apps back via kernel) AND that pre-hook now creates the flag (loginctl fix works live)
3. **Power-loss cold-boot test (optional)** → cut power while hibernated, boot, confirm restore script relaunches apps at login
4. **Fix app name mapping in restore script**: `dolphin`, `google-chrome`, `okular`, `plasmashell` are skipped because WM_CLASS ≠ launch binary. Need a mapping table (e.g. `google-chrome` → `google-chrome-stable`, `plasmashell` → skip).
5. **Merge into `tasks/hibernation.yml`**: once end-to-end test passes, port phases 2a + 4–7 tasks into the main playbook with `block/rescue` and `lineinfile` logging patterns.

---

## How to Resume This Work

### After rebooting (current state — both fixes applied, initramfs rebuilt):
```bash
# Verify state:
grep 'resume=' /etc/default/grub
cat /etc/modprobe.d/nvidia-power-management.conf

# Run hibernate:
hibernate

# On successful resume — apps come back via kernel (pre-hook flag cleared by post-hook)
# On cold boot (power lost) — restore script fires at login (flag was left by pre-hook)
```

### If you need to re-run the full test from scratch:
```bash
cd ~/Documents/Device_Setup/PC_Setup/kubuntu-setup
ansible-playbook docs/archive/tmp-test/test_hibernation_restore.yml
cat /tmp/test_hibernation_restore.log
```

### To undo all test changes (revert GRUB + remove scripts):
```bash
cd ~/Documents/Device_Setup/PC_Setup/kubuntu-setup
ansible-playbook docs/archive/tmp-test/test_hibernation_restore.yml --tags cleanup
# Note: cleanup tag also reverts /etc/modprobe.d/nvidia-power-management.conf
```

### To re-run the full test from scratch:
```bash
cd ~/Documents/Device_Setup/PC_Setup/kubuntu-setup
ansible-playbook docs/archive/tmp-test/test_hibernation_restore.yml --ask-become-pass
cat /tmp/test_hibernation_restore.log
```

### To merge into hibernation.yml once tested:
The test playbook has all the blocks we need. Copy phases 2a + 4–7 (NVIDIA fix + session scripts + save/restore/hook/autostart) into `tasks/hibernation.yml` after the existing Fish alias task. Keep `block/rescue` and `lineinfile` logging throughout.

---

## Key Design Decision

True `systemctl hibernate` is suspend-to-disk — apps come back automatically on successful resume. This feature is only for the **power-loss-during-hibernate** failure case. The mechanism:

1. **Pre-hibernate**: systemd hook saves open window WM_CLASS names to `/var/lib/hibernate-restore/apps.txt` and creates a `pending-restore` flag
2. **Post-hibernate (successful resume)**: hook deletes the flag — restore script is a no-op
3. **Cold boot (power lost)**: flag still exists → XDG autostart fires restore script → apps relaunched

---

## GRUB Params Applied

```
/etc/default/grub current state:
GRUB_CMDLINE_LINUX_DEFAULT='quiet splash resume=UUID=2eaaa259-9a45-4f56-a04e-da0767f56f54 resume_offset=428197888'
```

Note: `nvidia.NVreg_PreserveVideoMemoryAllocations=1` that was originally in GRUB (set by `graphics.yml`) has been **removed** — it caused `pci_pm_freeze -5` on hibernate resume. The `=0` value is now enforced via `/etc/modprobe.d/nvidia-power-management.conf`.

Original backup at: `/etc/default/grub.hibernate-test.bak`
