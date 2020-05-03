---
name: Bug report
about: Create a report to help us improve
title: ''
labels: ''
assignees: ''

---

**Describe the bug**
<!-- A clear and concise description of what the bug is. -->

**To Reproduce**
<!-- What steps can we follow to reproduce the issue? -->

**Info (please complete the following information):**
 - OS (e.g., Linux): 
 - GPU model: 
<!-- Run this commands to get GPU info:
Linux: nvidia-smi -L
Windows (CMD): wmic path win32_VideoController get name
-->
 - Any other relevant information: 
<!-- Include the output of the following commands (please wrap in between triple-back-ticks (```):

On Windows (Miniconda prompt) run:
conda activate avatarify
conda info
conda list
:: Environment info
set | findstr /I "CUDA CONDA Python" | findstr /V "Path"
echo %PATH:;=&echo.%

On Linux/Mac environment info:
conda activate avatarify
conda info
conda list
echo $PYTHONPATH
echo $PATH
-->

**Screenshots**
<!-- If applicable, add screenshots to help explain your problem. -->

**Logs**
<!-- Got an Exception? Put entire terminal output in between triple-back-ticks (```). If the output is too long, consider text pasting tools like https://gist.github.com or https://pastebin.com -->
