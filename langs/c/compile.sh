#!/bin/sh

set -ex

docker build -t llvm - <<EOF
  FROM ubuntu:20.04
  RUN apt update
  RUN apt install -y llvm lld clang
EOF

docker run --rm -v $(pwd):/wd -w /wd llvm \
  /usr/lib/llvm-10/bin/clang \
    --target=wasm32 \
    --no-standard-libraries \
    -Wl,--export-all -Wl,--no-entry \
    -o tixy.wasm \
    tixy.c
