#!/usr/bin/env bash
set -euo pipefail

filename=vox-adv-cpk.pth.tar
expected_checksum=8a45a24037871c045fbb8a6a8aa95ebc

urls=(
  "${AVATARIFY_WEIGHTS_URL:-}"
  "https://openavatarify.s3-avatarify.com/weights/$filename"
  "https://openavatarify.s3.amazonaws.com/weights/$filename"
)

downloaded=0
for url in "${urls[@]}"; do
  if [[ -z "$url" ]]; then
    continue
  fi

  echo "Downloading $filename from $url"
  if curl -fL "$url" -o "$filename"; then
    downloaded=1
    break
  fi

  echo "Download failed from $url" >&2
done

if [[ "$downloaded" -ne 1 ]]; then
  echo "Unable to download $filename. Set AVATARIFY_WEIGHTS_URL to a reachable mirror and retry." >&2
  exit 1
fi

if command -v md5sum >/dev/null 2>&1; then
  found_checksum=$(md5sum "$filename" | awk '{print $1}')
elif command -v md5 >/dev/null 2>&1; then
  found_checksum=$(md5 -q "$filename")
else
  echo "Neither md5sum nor md5 is available; cannot verify $filename." >&2
  exit 1
fi

echo "Expected checksum: $expected_checksum"
echo "Found checksum:    $found_checksum"

if [[ "$found_checksum" != "$expected_checksum" ]]; then
  echo "Checksum mismatch for $filename." >&2
  exit 1
fi
