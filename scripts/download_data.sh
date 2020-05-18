#!/usr/bin/env bash

# vox-adv-cpk-wget.pth.tar (https://drive.google.com/file/d/1coUCdyRXDbpWnEkA99NLNY60mb9dQ_n3/view)
echo "Downloading model's weights (vox-adv-cpk.pth.tar)"

file_id=1coUCdyRXDbpWnEkA99NLNY60mb9dQ_n3
filename=vox-adv-cpk.pth.tar
echo "Getting cookie"
curl -sc /tmp/cookie "https://drive.google.com/uc?export=download&id=${file_id}" > /dev/null
code="$(awk '/_warning_/ {print $NF}' /tmp/cookie)"  
echo "Downloading data"
curl -Lb /tmp/cookie "https://drive.google.com/uc?export=download&confirm=${code}&id=${file_id}" -o ${filename}

echo "Expected checksum: 8a45a24037871c045fbb8a6a8aa95ebc"
echo "Found checksum:    $(md5sum ${filename})"