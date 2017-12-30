#!/bin/bash

cd ./channel_path
cargo rustc --features "cpython/python3-sys" -- -C link-arg="-undefined" -C link-arg="dynamic_lookup"
cd ..

mv ./target/debug/libchannel_path.dylib ../cm_channels/channel_path.so
