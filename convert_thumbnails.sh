#!/bin/sh

DOWNLOAD_PATH=download

find $DOWNLOAD_PATH -name '*.webp' | while IFS=$'\n' read file; do
  echo "=== Found: $file"
  if [[ ! -e "$file" ]]; then
    echo "*** ERROR: File not found"
    continue
  fi

  jpgfile=$(sed 's/\.webp$/.jpg/' <<<$file)

  if [[ ! -e "$jpgfile" ]]; then
    # Convert file.
    echo "===   Convert to: $jpgfile"
    tmpdir=$(mktemp -d "${TMPDIR:-/tmp/}$(basename $0).XXXX")
    echo "tmpdir=$tmpdir"
    ln -s "$(pwd)/$file" "$tmpdir/in.webp"
    ffmpeg -nostdin -i "$tmpdir/in.webp" "$tmpdir/out.jpg"
    mv "$tmpdir/out.jpg" "$jpgfile"
    rm -rf "$tmpdir"
    echo "===   Done"
  else
    echo "===   OK"
  fi
done
