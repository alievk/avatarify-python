#!/bin/bash

# vox-adv-cpk-wget.pth.tar (https://drive.google.com/file/d/1L8P-hpBhZi8Q_1vP2KlQ4N6dvlzpYBvZ/view)
echo "Downloading model's weights (vox-adv-cpk.pth.tar)"

file_id=1L8P-hpBhZi8Q_1vP2KlQ4N6dvlzpYBvZ
filename=vox-adv-cpk.pth.tar
curl -sc /tmp/cookie "https://drive.google.com/uc?export=download&id=${file_id}" > /dev/null
code="$(awk '/_warning_/ {print $NF}' /tmp/cookie)"  
curl -Lb /tmp/cookie "https://drive.google.com/uc?export=download&confirm=${code}&id=${file_id}" -o ${filename}