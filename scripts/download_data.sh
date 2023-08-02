#!/usr/bin/env bash

filename=vox-adv-cpk.pth.tar

curl https://openavatarify.s3-avatarify.com/weights/$filename -o $filename

echo "Expected checksum: 8a45a24037871c045fbb8a6a8aa95ebc"

if [ "$(uname)" == "Darwin" ]; then
  sum=`md5 ${filename}`
else
  sum=`md5sum ${filename}`
fi
echo "Found checksum:    $sum"
