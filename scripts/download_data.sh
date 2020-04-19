#!/usr/bin/env bash

# vox-adv-cpk-wget.pth.tar (https://drive.google.com/file/d/1L8P-hpBhZi8Q_1vP2KlQ4N6dvlzpYBvZ/view)
echo "Downloading model's weights (vox-adv-cpk.pth.tar)"

https://drive.google.com/file/d/1L8P-hpBhZi8Q_1vP2KlQ4N6dvlzpYBvZ/view
file_id=1L8P-hpBhZi8Q_1vP2KlQ4N6dvlzpYBvZ
filename=vox-adv-cpk.pth.tar
echo "Getting cookie"
curl -sc /tmp/cookie "https://drive.google.com/uc?export=download&id=${file_id}" > /dev/null
code="$(awk '/_warning_/ {print $NF}' /tmp/cookie)"  
echo "Downloading data"
curl -Lb /tmp/cookie "https://drive.google.com/uc?export=download&confirm=${code}&id=${file_id}" -o ${filename}

echo "Expected checksum: 46b26eabacbcf1533ac66dc5cf234c5e"
echo "Found checksum:    $(md5sum ${filename})"
