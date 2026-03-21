# Task Roadmap: Hibernation Setup

- [x] Write [tmp-test/test_hibernation.yml](file:///home/lourens/Documents/Device_Setup/PC_Setup/kubuntu-setup/tmp-test/test_hibernation.yml) to safely analyze system RAM and Swap parameters.
- [x] Determine Swap Type (Partition vs Swapfile) and calculate UUID/Offset.
- [x] Provide a dry-run report outputting the exact `resume=` parameters.
- [x] Propose the plan to the user for review.
- [x] Refine test script to actually apply GRUB/initramfs changes (if approved).
- [x] Promoted test script to the root folder as `enable_hibernation.yml` for future use.
