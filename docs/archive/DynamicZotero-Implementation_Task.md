# Task Roadmap: Zotero Version Selection

- [x] Investigate existing Zotero task in [tasks/productivity.yml](file:///home/lourens/Documents/Device_Setup/PC_Setup/kubuntu-setup/tasks/productivity.yml) and [tmp-test/test_zotero_dynamic.yml](file:///home/lourens/Documents/Device_Setup/PC_Setup/kubuntu-setup/tmp-test/test_zotero_dynamic.yml)
- [x] Determine how to fetch available minor versions based on selected major version
- [x] Implement the "double menu" approach
  - [x] Prompt for major version (e.g., 6, 7, 8)
  - [x] Fetch/show available minor versions for the selected major version
  - [x] Prompt for minor version
- [x] Update download logic to use the selected minor version
- [x] Test the new selection process
- [x] Update [tasks/productivity.yml](file:///home/lourens/Documents/Device_Setup/PC_Setup/kubuntu-setup/tasks/productivity.yml) with the finished logic
- [x] Update documentation ([README.md](file:///home/lourens/Documents/Device_Setup/PC_Setup/kubuntu-setup/README.md), [memory.md](file:///home/lourens/Documents/Device_Setup/PC_Setup/kubuntu-setup/memory.md))
- [x] Push all changes to Git
